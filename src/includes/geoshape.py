import numpy as np

def generate_domain(start, stop, num):
    return np.linspace(start, stop, num, dtype=float)

def generate_curve_points(domain, expr):
    x = domain
    y = eval(expr) # np arrays can be sent at once to the eval fn
    points = np.column_stack((x, y)) # ts function pairs same indexed elements of multiple lists together forming a 2d list
    return points