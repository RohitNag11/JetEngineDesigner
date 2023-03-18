import numpy as np


def get_diameter_from_area(area):
    return 2 * (area / np.pi)**0.5


def get_area_from_diameter(diameter):
    return np.pi * (diameter / 2)**2


def get_tangential_speed(angular_velocity, diameter):
    return angular_velocity * diameter / 2


def get_angular_velocity(tangential_speed, diameter):
    return 2 * tangential_speed / diameter


def get_hub_diameter_from_blade_length(blade_length, annulus_area):
    return 2 * (annulus_area - np.pi * blade_length**2) / (2 * np.pi * blade_length)
    # return annulus_area / (2 * np.pi * blade_length**2) - blade_length / 2


def get_mean_radius_from_blade_length(blade_length, annulus_area):
    return annulus_area / (2 * np.pi * blade_length)


def get_hub_diameter_from_mean_radius(mean_radius, annulus_area):
    return (4 * np.pi * mean_radius**2 - annulus_area) / (2 * np.pi * mean_radius)


def get_tip_diameter_from_mean_radius(mean_radius, annulus_area):
    return (4 * np.pi * mean_radius**2 + annulus_area) / (2 * np.pi * mean_radius)


def get_annulus_area(hub_tip_ratio, mean_radius):
    return 4 * np.pi * mean_radius**2 * (1 - hub_tip_ratio) / (1 + hub_tip_ratio)


def get_tip_diameter_from_hub_diameter(hub_diameter, annulus_area):
    return (annulus_area / np.pi + (hub_diameter / 2)**2)**0.5 * 2
