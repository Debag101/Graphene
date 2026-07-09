import numpy as np

def generate_domain(start, stop, num):
    return np.linspace(start, stop, num, dtype=float)

def generate_curve_points(domain, expr):
    points = []

    for element in domain:
        x = element
        fx = eval(expr)
        points.append([x, fx])

    return points



