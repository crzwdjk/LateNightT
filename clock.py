# clock.py: draw a clock on a cairo context.

import math

r3_2 = 0.5 * math.sqrt(3)
clock_hour_angle = [
    (0, 1),
    (0.5, r3_2),
    (r3_2, 0.5),
    (1, 0),
    (r3_2, -0.5),
    (0.5, -r3_2),
    (0, -1),
    (-0.5, -r3_2),
    (-r3_2, -0.5),
    (-1, 0),
    (-r3_2, 0.5),
    (-0.5, r3_2)
]

# draw_clock - draw an analog clock
# parameters:
#   ctx - a cairo context
#   x, y - center point of clock
#   radius - of the clock
#   hour - hour to show
#   quarter - quarter hour to show (0, 1, 2, or 3)
def draw_clock(ctx, x, y, radius, hour, quarter):
    (hdx, hdy) = (c * radius * 0.6 for c in clock_hour_angle[hour % 12])
    (mdx, mdy) = (c * radius * 0.8 for c in clock_hour_angle[quarter * 3])

    ctx.set_line_width(0.001)
    ctx.set_source_rgb(1, 1, 1)

    ctx.arc(x, y, radius, 0, 2*math.pi)
    ctx.stroke()

    ctx.set_line_width(0.002)
    ctx.move_to(x, y)
    ctx.line_to(x + hdx, y + hdy)
    ctx.stroke()

    ctx.set_line_width(0.001)
    ctx.move_to(x, y)
    ctx.line_to(x + mdx, y + mdy)
    ctx.stroke()

