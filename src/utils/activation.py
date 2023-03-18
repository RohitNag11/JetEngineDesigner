import numpy as np
import matplotlib.pyplot as plt


def smooth_step_up(x, start, end, min_y, max_y):
    height = max_y - min_y
    # Convert x to a numpy array if it's a float
    if isinstance(x, float):
        x = np.array([x])
    # Calculate the normalized value of x
    t = (x - start) / (end - start)
    # Apply the smooth step function
    smooth_t = t * t * (3 - 2 * t)
    # Calculate the value of the step function
    step_value = np.where(x < start, 0, np.where(
        x >= end, height, height * smooth_t))
    # Return the final value
    return step_value.squeeze() + min_y


def smooth_step_down(x, start, end, min_y, max_y):
    height = max_y - min_y
    # Convert x to a numpy array if it's a float
    if isinstance(x, float):
        x = np.array([x])
    # Calculate the normalized value of x
    t = (x - start) / (end - start)
    # Apply the smooth step function
    smooth_t = t * t * (3 - 2 * t)
    # Calculate the value of the step function
    step_value = np.where(x < start, height, np.where(
        x >= end, 0, height * (1 - smooth_t)))
    # Return the final value
    return step_value.squeeze() + min_y
