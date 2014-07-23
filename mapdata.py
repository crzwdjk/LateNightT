import csv

start_of_latenight = '2014-03-25'

# Get ridership data for bus routes.
# returns a pair of lists, with each list containing tuples of
# (average nightly ridership, route, hour, quarter)
def ridership_by_route(db):
    c = db.cursor()

    c.execute('select count(distinct scheduledate) from ridership where scheduledate > ?',
              (start_of_latenight,))
    days_after = c.fetchone()[0]
    print(days_after, "days after start of late night service ")
    c.execute('select count(distinct scheduledate) from ridership where scheduledate <= ?',
              (start_of_latenight,))
    days_before = c.fetchone()[0]
    print(days_before,  "days before start of late night service")

    c.execute("""select sum(transactions) / ? avgrides, routestation, trxhour, trx15min
                 from ridership
                 where (line = 'Bus'
                        or (line = 'Silver' and routestation in
                            ('SL4 Essex', 'SL5 Washington St')))
                 and scheduledate > ?
                 group by routestation, trxhour, trx15min""",
                 (days_after, start_of_latenight))
    ridership_after = c.fetchall()

    c.execute("""select sum(transactions) / ? avgrides, routestation, trxhour, trx15min
                 from ridership where line = 'Bus' and scheduledate <= ?
                 group by routestation, trxhour, trx15min""",
                 (days_before, start_of_latenight))
    ridership_before = c.fetchall()

    return (ridership_before, ridership_after)

# Get ridership data for subway stations.
# returns a list of tuples containing:
# (average nightly ridership, station, hour, quarter, line)
def ridership_by_station(db):
    c = db.cursor()
    c.execute('select count(distinct scheduledate) from ridership where scheduledate > ?',
              (start_of_latenight,))
    days_after = c.fetchone()[0]
    c.execute('select count(distinct scheduledate) from ridership where scheduledate <= ?',
              (start_of_latenight,))
    days_before = c.fetchone()[0]

    c.execute("""select sum(transactions) / ? avgrides, routestation, trxhour, trx15min, line
                 from ridership
                 where scheduledate >= ?
                 and (line in ('Red', 'Orange', 'Blue')
                      or line = 'Green' and routestation not like 'Green Line%'
                      or line = 'Silver' and routestation in ('Courthouse', 'World Trade Center'))
                 group by routestation, trxhour, trx15min, line""",
        (days_after, start_of_latenight))
    return c.fetchall()

# Read shapes-by-route.txt and return a dict mapping route to shape_id
def init_shape_route_map():
    f = open("shapes-by-route.txt")
    shape_by_route = {}
    for line in f:
        kv = line.strip().split(",")
        shape_by_route.setdefault(kv[0], []).append(kv[1])
    f.close()
    return shape_by_route

# Read shapes.txt, returns a dict mapping shape_id to a list
# of (sequence, lat, lon) tuples for that shape.
def init_shapes():
    r = csv.reader(open('shapes.txt'))
    shapes = {}
    for line in r:
        shape_id, lat, lon, sequence = line[0], float(line[1]), float(line[2]), int(line[3])
        shapes.setdefault(shape_id, []).append((sequence, lat, lon))
    for shapelist in shapes.values():
        shapelist.sort()
    return shapes

# Read stoplocations.txt, returns a dict mapping stop name to (lat, lon)
def init_station_locations():
    r = csv.reader(open('stoplocations.txt'), delimiter = '|')
    locations = {}
    for line in r:

        locations[line[1]] = (float(line[3]), float(line[2]))
    return locations

