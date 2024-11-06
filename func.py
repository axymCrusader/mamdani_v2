import numpy as np

def gaussian_membership_function(x, mean, sigma):
    return np.exp(-((x - mean) ** 2) / (2 * sigma ** 2))