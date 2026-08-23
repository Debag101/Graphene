import re
import numpy as np

allowed_functions = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan, 
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "sqrt": np.sqrt, 
    "log": np.log10, 
    "ln": np.log, 
    "pi": np.pi, 
    "e": np.e, 
    "abs": np.abs, 
    "floor": np.floor   
}



def generate_domain(start, stop, num):
    return np.linspace(start, stop, num, dtype=float)

def clean_function_expr(expr):
    cleaned_expr = expr.replace(' ', '')
    cleaned_expr = cleaned_expr.replace('^', "**")
    
    return cleaned_expr


def generate_curve_points(domain, expr, tb, jump_threshold=50):

    cleaned_expr = clean_function_expr(expr)
    allowed_functions_copy = allowed_functions.copy()
    allowed_functions_copy['x'] = domain

    try:
        req_range = eval(cleaned_expr, {"__builtins__": None}, allowed_functions_copy)

        # Incase of exprs like x = 5, numpy returns just the integer 5 or maybe a float in that instance
        # Since my program can't plot a single integer, I use numpy's full_like func

        if isinstance(req_range, (int, float)):
            #Full like creates a list filled with only given int/float, same length as of domain
            req_range = np.full_like(domain, req_range)


        #np.isinf() runs over the whole list, returns true where np.inf is found and changes that to np.nan
        req_range[np.isinf(req_range)] = np.nan

        '''
            np.diff calculates the differences between consecutive values in the numpy array and creates another numpy
            array comprising of those differences.

            For ex:
                x = [1, 3, 7, 4]
                np.diff(x) would return [2, 4, -3]
                the np.abs would change to [2, 4, 3]

            So now we check for differences greater than 50, add them as False, others become True
            The last False is to attach another element, because jump_mask would naturally be 1 less in length
            compared to req_range as we are creating it based on differences, so for 10 elements you'll get 9 differences

        '''

        jump_mask = np.append(np.abs(np.diff(req_range)) > jump_threshold, False)
        req_range[jump_mask] = np.nan

        tb.error = False

        valid_mask = ~np.isnan(req_range)
        valid_x = domain[valid_mask]
        valid_y = req_range[valid_mask]

        roots = []
        if len(valid_y) > 1:
            sign_flips = np.where(np.diff(np.sign(valid_y)))[0]
            for flip_idx in sign_flips:
                x1, y1 = valid_x[flip_idx], valid_y[flip_idx]
                x2, y2 = valid_x[flip_idx + 1], valid_y[flip_idx + 1]

                if y2 - y1 != 0:
                    root_x = x1 - y1 * ((x2 - x1) / (y2 - y1))
                    roots.append(root_x)

        points = np.column_stack((domain, req_range))

        return points, roots

    except Exception as e:
        print(f"Error parsing {cleaned_expr}: {e}")
        tb.error = True
        return np.array([]), []
