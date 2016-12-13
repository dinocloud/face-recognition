RIGHT = "RIGHT"
LEFT = "LEFT"


def inside_convex_polygon(point, vertices):
    previous_side = None
    n_vertices = len(vertices)
    for n in xrange(n_vertices):
        a, b = vertices[n], vertices[(n+1)%n_vertices]
        affine_segment = v_sub(b, a)
        affine_point = v_sub(point, a)
        current_side = get_side(affine_segment, affine_point)
        if current_side is None:
            return False #outside or over an edge
        elif previous_side is None: #first segment
            previous_side = current_side
        elif previous_side != current_side:
            return False
    return True


def get_side(a, b):
    x = x_product(a, b)
    if x < 0:
        return LEFT
    elif x > 0:
        return RIGHT
    else:
        return None


def v_sub(a, b):
    return (a[0]-b[0], a[1]-b[1])


def x_product(a, b):
    return a[0]*b[1]-a[1]*b[0]