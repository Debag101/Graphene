import numpy as np

def generate_domain(start, stop, num):
    return np.linspace(start, stop, num, dtype=float)

def generate_curve_points(domain, expr):
    x = domain
    y = eval(expr)
    points = np.column_stack((x, y))
    return points