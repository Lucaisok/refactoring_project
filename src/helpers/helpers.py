import numpy as np


# This helper function calculates the distance between one house and a reference location.
def calculate_distance(long, lat, ref_long, ref_lat):
    """dist computes the distance in km to a reference location.
    Input: long and lat of the location of interest and ref_long and ref_lat
    as the long and lat of the reference location"""
    delta_long = long - ref_long
    delta_lat = lat - ref_lat
    delta_long_corr = delta_long * np.cos(np.radians(ref_lat))
    return (
        ((delta_long_corr) ** 2 + (delta_lat) ** 2) ** (1 / 2) * 2 * np.pi * 6378 / 360
    )
