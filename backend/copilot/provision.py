

from flask import Flask


controllers = []

def controller(func, *args, **kwargs):
    controllers.append({
        "func": func,
        "args": args,
        "kwargs": kwargs
    })
    def wrapper(*args, **kwargs):
        if hasattr(func, '__self__') and func.__self__ is not None:
            # Method of a class
            instance = func.__self__.__class__()
            method = getattr(instance, func.__name__)
            return method(*args, **kwargs)
        else:
            # Standalone function
            return func(*args, **kwargs)
    return wrapper

def provision(app: Flask):
    for controller in controllers:
        app.route(*controller["args"], **controller["kwargs"])(controller["func"])