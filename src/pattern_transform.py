def rotate_90(pattern):
    return [(-y, x) for x, y in pattern]


def rotate_180(pattern):
    return [(-x, -y) for x, y in pattern]


def rotate_270(pattern):
    return [(y, -x) for x, y in pattern]


def reflect_horizontal(pattern):
    return [(-x, y) for x, y in pattern]


def reflect_vertical(pattern):
    return [(x, -y) for x, y in pattern]


def normalize(pattern):
    xs = [x for x, _ in pattern]
    ys = [y for _, y in pattern]

    min_x = min(xs)
    min_y = min(ys)

    return [(x - min_x, y - min_y) for x, y in pattern]

