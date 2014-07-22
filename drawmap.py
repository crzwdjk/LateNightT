#!/usr/bin/python3
import sqlite3
from maputils import init_canvas, convert_point
from mapdata import *

def normalize_color(value):
    # goes from (0, 0, 0) to (1, 1, 0) to (1, 1, 0.75)
    if value < 10:
        return (0, 0, 0)
    if value <= 50:
        factor = value / 50.0
        return (factor, factor, 0)
    else:
        factor = (value - 50) / 50.0
        return (1, 1, max(factor, 0.75))

def normalize_station_color(number):
    if number >= 180:
        return (0.9, 0.9, 0.9)
    else:
        return tuple(number / 180 * i for i in (0.9,)*3)

def normalize_linewidth(value):
    if value >= 80:
        return 0.002
    return value / 80 * 0.001 + 0.001

bounds = (-71.291176, -70.845367, 42.17, 42.51)

import cairo
def drawshape(ctx, shape, color, linewidth = 0.0015, operator = cairo.OPERATOR_ADD):
    ctx.set_operator(operator)
    ctx.set_line_width(linewidth)
    ctx.set_source_rgb(*color)
    (seq, x, y) = shape[0]
    ctx.move_to(*convert_point(bounds, (x, y)))
    for (seq, x, y) in shape[1:]:
        ctx.line_to(*convert_point(bounds, (x, y)))
    ctx.stroke()

subwaycolors = {
    "Blue": {
        "color": (0.184, 0.365, 0.651),
        "routes": ('946_',),
    },
    "Orange": {
        "color": (0.910, 0.447, 0.0),
        "routes": ('903_',),
    },
    "Red": {
        "color": (0.882, 0.176, 0.153),
        "routes": ('931_', '933_'),
    },
    "Green": {
        "color": (0.259, 0.482, 0.114),
        "routes": ('812_', '831_', '852_', '880_'), # green line
    },
    #"Silver": {
    #    "color": (0.333, 0.333, 0.333),
    #    "routes": ('746'), # silver line Waterfront subway
    #},
}

# transfer stations, and ridership distribution by line (based on 2014 Blue Book data)
transferstations = {
    "Park Street": {"Green": 0.442, "Red": 0.558},
    "Downtown Crossing": {"Red": 0.444, "Orange": 0.556},
    "State Street": {"Orange": 0.623, "Blue": 0.377},
    "Government Center": {"Blue": 0.262, "Green": 0.738},
    "Haymarket": {"Green": 0.386, "Orange": 0.614},
    "North Station": {"Green": 0.366, "Orange": 0.634},
    # "South Station": {"Red": 0.947, "Silver": 0.053},
}

def draw_subway_lines(ctx, shapes_for_route, shapes, station_riderships):
    line_riderships = {l: 0 for l in ["Red", "Green", "Blue", "Orange"]}
    for ridership, station, line in station_riderships:
        if station in transferstations:
            for line in transferstations[station].keys():
                factor = transferstations[station][line]
                line_riderships[line] += factor * ridership
        else:
            line_riderships[line] += ridership

    print(line_riderships)
    for line, data in subwaycolors.items():
        shapeids = []
        weight = max(min(800, line_riderships[line]) / 800, 0.1)
        color = tuple(weight * i for i in data["color"])
        for route in data["routes"]:
            shapeids.extend(shapes_for_route[route])
        for shapeid in shapeids:
            drawshape(ctx, shapes[shapeid], color, 0.004, cairo.OPERATOR_OVER)
    return

def draw_subway_stations(ctx, station_ridership, station_locations):
    for (ridership, station, line) in station_ridership:
        if station not in station_locations:
            print(station, "not found")
            continue
        location = station_locations[station]
        (x, y) = convert_point(bounds, location)
        station_color = normalize_station_color(ridership)
        ctx.set_source_rgb(*station_color)
        ctx.arc(x, y, 0.003, 0, 2*3.1415926535)
        ctx.fill()


def main():
    db = sqlite3.connect('latenight.db')
    c = db.cursor()

    (ridership_before, ridership_after) = ridership_by_route(db)
    station_ridership_after = ridership_by_station(db)

    station_locations = init_station_locations()

    shapes_for_route = init_shape_route_map()
    shapes = init_shapes()

    # normalization value: 60 txs per quarter hour
    for hour in [22, 23, 24, 25, 26, 27]:
        for quarter in [0, 1, 2, 3]:
            (ctx, surf) = init_canvas(800, 800, (0, 0, 0))

            station_riderships = list(map(lambda x: (x[0], x[1], x[4]),
                                     filter(lambda r: r[2] == hour and r[3] == quarter,
                                            station_ridership_after)))
            draw_subway_lines(ctx, shapes_for_route, shapes, station_riderships)

            route_riderships = map(lambda x: (x[0], x[1]),
                                   filter(lambda r: r[2] == hour and r[3] == quarter,
                                          ridership_after))
            for ridership, route in route_riderships:
                if route not in shapes_for_route:
                    continue
                color = normalize_color(ridership)
                linewidth = normalize_linewidth(ridership)
                nshapes = len(shapes_for_route[route])
                color = tuple(x / nshapes for x in color)
                for shapeid in shapes_for_route[route]:
                   drawshape(ctx, shapes[shapeid], color)

            draw_subway_stations(ctx, station_riderships, station_locations)

            filename = "ridership-%d%d.png" % (hour, quarter)
            surf.write_to_png(filename)

if __name__ == "__main__":
    main()
