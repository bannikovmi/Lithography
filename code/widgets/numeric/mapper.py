import numpy as np

from PyQt5.QtCore import QObject

class QMapper(QObject):
    """
    A class for representing various scales.

    In mathematical terms a mapper is a tuple of two intervals [x_min, x_max] and [y_min, y_max]
    and a mapping function f(x) : [x_min, x_max] -> [y_min, y_max]. Input parameters are intervals
    and mapping function class (i.e. linear/logarithmic etc)

    Parameters
    ----------
    x_min : float
        Minimal value of the input scale (default=0).
    x_max : float
        Maximal value of the input scale (default=100). Raises a ValueError if x_max <= x_min.
    y_min : float
        Minimal value of the output scale (default=0).
    y_max: float
        Maximal value of the output scale (default=100). Raises a ValueError if y_max <= y_min.
    map_func : function
        The function mapping one interval to another (default function: f(x)=x). 
        The function should be monotonous and continiously differentiable over [x_min, x_max]
        interval. Both increasing and decreasing functions are valid.
    inverse_map_func : function
        The inverse of the mapping function (default function: f(x)=x). 
        User should make sure that it is indeed the inverse of the map_func.
    """

    def __init__(self,
        x_min: float=0,
        x_max: float=100,
        y_min: float=0,
        y_max: float=100, 
        map_func=lambda x: x,
        inverse_map_func=lambda x: x):
        # Save class arguments as attributes
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.map_func = map_func
        self.inverse_map_func = inverse_map_func        

    def evaluate(self, x):
        """ Evaluate the mapping function for the given argument."""
        return self.map_func(x)

    def evaluate_inverse(self, y):
        """ Evaluate the inverse of the mapping function for the given argument."""
        return self.inverse_map_func(y)

    ####################################################################################
    # Commonly used mappers
    ####################################################################################
    @classmethod
    def linear(cls, x_min=0, x_max=100, y_min=0, y_max=100):
        """Linear mapping function y = a*x + b"""
        # Calculate ranges
        y_range = y_max - y_min
        x_range = x_max - x_min
    
        def map_func(x):
            return y_min + y_range*((x - x_min)/x_range)
        def inverse_map_func(y):
            return x_min + x_range*((y-y_min)/y_range)

        return cls(x_min, x_max, y_min, y_max, map_func, inverse_map_func)

    @classmethod
    def square(cls, x_min=0, x_max=100, y_min=0, y_max=100):

        """Quadratic mapping function y = a*(x-x_min)^2 + b"""
        if x_min < 0:
            raise ValueError("x_min should be >= 0")

        # Calculate ranges
        y_range = y_max - y_min
        x_range = x_max - x_min
    
        def map_func(x):
            return y_min + y_range*((x - x_min)/x_range)**2
        def inverse_map_func(y):
            return x_min + x_range*((y-y_min)/y_range)**(1/2)

        return cls(x_min, x_max, y_min, y_max, map_func, inverse_map_func)

    @classmethod
    def log10(cls, x_min=0, x_max=100, y_min=1e-2, y_max=100):
        """Exponential mapping function y = 10**(a*(x-b))"""
        
        if y_min <= 0:
            raise ValueError("y_min should be > 0")

        # Calculate a and b
        a = np.log10(y_max/y_min)/(x_max - x_min)
        b = x_max - np.log10(y_max)/a
    
        def map_func(x):
            return pow(10, a*(x-b))
        def inverse_map_func(y):
            return b + np.log10(y)/a

        return cls(x_min, x_max, y_min, y_max, map_func, inverse_map_func)