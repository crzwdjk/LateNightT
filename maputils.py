# maputils.py - some utilities to aid with map-drawing
import cairo

# convert-point - convert a point from geographic to canvas coordinates
# bounds is the geographic extent of the canvas in the format
#   of (long_1, long_2, lat_1, lat_2)
# pt is (lat, long).
# returns (x,y) coordinates where x and y are between 0 and 1.
def convert_point(bounds, pt):
    (long_1, long_2, lat_1, lat_2) = bounds
    x = (pt[1] - long_1) / (long_2 - long_1)
    y = (pt[0] - lat_1) / (lat_2 - lat_1)
    return (x, y)

# init_canvas - initialize a cairo canvas and context
# The canvas is of size (w, h), and is optionally cleared to
# the given color.
# The transform matrix is set up such that coordinates range
# from 0 to 1 in each dimension.
def init_canvas(w, h, clearcolor = None):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(surf)
    matrix = cairo.Matrix(xx = w, yy = -h, x0 = 0.0, y0 = h)
    ctx.set_matrix(matrix)
    ctx.set_line_width(0.001)

    if clearcolor:
        ctx.move_to(0, 0)
        ctx.line_to(0, 1)
        ctx.line_to(1, 1)
        ctx.line_to(1, 0)
        ctx.close_path()

        ctx.set_source_rgb(*clearcolor)
        ctx.fill()

    return (ctx, surf)
