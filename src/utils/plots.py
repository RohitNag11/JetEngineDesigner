import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np


def draw_engine(engine):
    fig, ax = plt.subplots()
    ax.set_title('Engine Geometry')
    ax.set_ylabel('Radius (m)')
    ax.set_xlabel('Stages')
    ax.set_ylim(-engine.diameter/2 - 0.5,
                engine.diameter/2 + 0.5)
    draw_engine_casing(ax, engine.diameter)
    draw_fan(ax, engine.fan.tip_diameter,
             engine.fan.inner_fan_tip_diameter, engine.fan.hub_diameter, 0, 'Fan')
    draw_fan(ax, -engine.fan.tip_diameter,
             -engine.fan.inner_fan_tip_diameter, -engine.fan.hub_diameter, 0)
    component_gap = 5
    start_pos = 6
    turb_components = [engine.lpc, engine.hpc, engine.hpt, engine.lpt]
    names = ['LPC', 'HPC', 'HPT', 'LPT']
    for i, turb_comp in enumerate(turb_components):
        draw_turb_comp(ax, turb_comp.hub_diameters,
                       turb_comp.tip_diameters, start_pos, names[i])
        draw_turb_comp(ax, -turb_comp.hub_diameters,
                       -turb_comp.tip_diameters, start_pos)
        start_pos += 2 * turb_comp.no_of_stages + component_gap
    plt.show()


def draw_turb_comp(ax, hub_diameters, tip_diameters, axial_start_position, name=None):
    hub_diameters = np.repeat(hub_diameters, 2)
    tip_diameters = np.repeat(tip_diameters, 2)
    mean_radius = (hub_diameters + tip_diameters) / 4
    n_stages_double = len(hub_diameters)
    z = np.linspace(axial_start_position,
                    axial_start_position + n_stages_double, n_stages_double) / 2

    stage_polygons_points = [[(z[i], tip_diameters[i] / 2),
                              (z[i], hub_diameters[i] / 2),
                              (z[i+1], hub_diameters[i+1] / 2),
                              (z[i+1], tip_diameters[i+1] / 2)]
                             for i in range(0, n_stages_double, 2)]

    [ax.add_patch(Polygon(points, alpha=0.5, color='b'))
     for points in stage_polygons_points]
    [ax.plot([z[i], z[i]], [hub_diameters[i] / 2, tip_diameters[i] / 2], 'k')
     for i in range(n_stages_double)]
    ax.plot(z, hub_diameters / 2, 'k')
    ax.plot(z, tip_diameters / 2, 'k')
    ax.plot(z, mean_radius, 'r', ls='-.')
    ax.text(np.mean(z[:-1]), mean_radius[-1]+0.1, name, color='r')


def draw_fan(ax, fan_tip, inner_fan_tip, fan_hub, axial_start_position, name=None):
    hub_diameters = np.repeat(fan_hub, 2)
    tip_diameters = np.repeat(fan_tip, 2)
    inner_fan_tip_diameters = np.repeat(inner_fan_tip, 2)
    inner_fan_mean_radius = (inner_fan_tip_diameters + hub_diameters) / 4
    n_stages_double = len(hub_diameters)
    z = np.linspace(axial_start_position,
                    axial_start_position + n_stages_double, n_stages_double) / 2
    inner_fan_polygons_points = [(z[0], inner_fan_tip_diameters[0] / 2),
                                 (z[0], hub_diameters[0] / 2),
                                 (z[1], hub_diameters[1] / 2),
                                 (z[1], inner_fan_tip_diameters[1] / 2)]
    outer_fan_polygons_points = [(z[0], tip_diameters[0] / 2),
                                 (z[0], inner_fan_tip_diameters[0] / 2),
                                 (z[1], inner_fan_tip_diameters[1] / 2),
                                 (z[1], tip_diameters[1] / 2)]
    ax.add_patch(Polygon(inner_fan_polygons_points, alpha=0.5, color='b'))
    ax.add_patch(Polygon(outer_fan_polygons_points, alpha=0.2, color='b'))
    ax.plot(z, hub_diameters / 2, 'k')
    ax.plot(z, tip_diameters / 2, 'k')
    [ax.plot([z[i], z[i]], [hub_diameters[i] / 2, tip_diameters[i] / 2], 'k')
     for i in range(n_stages_double)]
    ax.plot(z, inner_fan_tip_diameters / 2, 'k')
    ax.plot(z, inner_fan_mean_radius, 'r', ls='-.')
    ax.text(z[0], tip_diameters[0] / 2 + 0.1, name, c='r')


def draw_engine_casing(ax, diameter):
    ax.axhline(0, color='black', linestyle='-.')
    ax.axhline(diameter / 2, color='black', linestyle='-')
    ax.axhline(-diameter / 2, color='black', linestyle='-')


def plot_bezier_curve(start_point, start_angle, end_angle, chord_length, color, control_point_distance=None):
    # Set the default control point distance to one-third of the chord length
    if control_point_distance is None:
        control_point_distance = chord_length/3

    # Calculate the end point based on the start angle and start-to-end distance
    end_point = (start_point[0] + chord_length*np.cos(end_angle),
                 start_point[1] + chord_length*np.sin(end_angle))

    # Calculate the control point based on the start angle and start-to-end distance
    control_point = (start_point[0] + control_point_distance*np.cos(
        start_angle), start_point[1] + control_point_distance*np.sin(start_angle))

    # Calculate the curve using the Bezier curve formula
    t = np.linspace(0, 1, 1000)
    x = ((1 - t)**3)*start_point[0] + 3*((1 - t)**2)*t*control_point[0] + \
        3*(1 - t)*(t**2)*end_point[0] + (t**3)*end_point[0]
    y = ((1 - t)**3)*start_point[1] + 3*((1 - t)**2)*t*control_point[1] + \
        3*(1 - t)*(t**2)*end_point[1] + (t**3)*end_point[1]

    # Plot the curve
    plt.plot(x, y, color)


def get_bezier_curve_geometry(start_point, end_angle, chord_length):
    end_point = (start_point[0] + chord_length*np.cos(end_angle),
                 start_point[1] + chord_length*np.sin(end_angle))
    curve_width = end_point[0] - start_point[0]
    curve_height = end_point[1] - start_point[1]
    return curve_width, curve_height


# def plot_compressor_blades(stage_angles, rotor_chord_lengths, stator_chord_lengths, rotor_thicknesses, stator_thicknesses):
#     plt.figure(figsize=(10, len(stage_angles)*4))
#     start_x = 0
#     for i, angles in enumerate(stage_angles):
#         alpha_1 = angles['alpha_1']
#         alpha_2 = angles['alpha_2']
#         beta_1 = -angles['beta_1']
#         beta_2 = -angles['beta_2']

#         rotor_chord_length = rotor_chord_lengths[i]
#         stator_chord_length = stator_chord_lengths[i]

#         # Calculate the rotor and stator start and end points
#         # rotor_width, rotor_height = get_bezier_curve_geometry(
#         rotor_start = (start_x, 0)
#         # Calculate the rotor and stator curves using the plot_bezier_curve() function
#         rotor_end = plot_bezier_curve(rotor_start, beta_1,
#                                       beta_2, rotor_chord_length, 'r')

#         stator_start = (rotor_end[0] + rotor_stator_spacing, rotor_end[1])
#         stator_end = plot_bezier_curve(stator_start, alpha_2,
#                                        alpha_1, stator_chord_length, 'b')

#         # # Plot the rotor and stator lines
#         # plt.plot([rotor_start[0], rotor_end[0]], [
#         #          rotor_start[1], rotor_end[1]], 'r--')
#         # plt.plot([stator_start[0], stator_end[0]], [
#         #          stator_start[1], stator_end[1]], 'b--')

#         # Set the x and y limits for the plot
#         # plt.xlim(-chord_length*2, chord_length*3)
#         # plt.ylim(-chord_length*2, chord_length*2)

#         # Add labels for the rotor and stator
#         # plt.text(chord_length/2, -chord_length*2.2,
#         #          f'Rotor {i+1}', ha='center', va='top', color='r')
#         # plt.text(chord_length*2.5, -chord_length*2.2,
#         #          f'Stator {i+1}', ha='center', va='top', color='b')

#         start_x = stator_end[0] + stage_spacing

#     plt.axis('off')
#     plt.show()


# blade_angles = [
#     {
#         "alpha_1": 0.2066565857775206,
#         "alpha_2": 0.5614338978580816,
#         "beta_1": 0.5614338978580816,
#         "beta_2": 0.20665658577752055
#     },
#     {
#         "alpha_1": 0.2066565857775206,
#         "alpha_2": 0.5614338978580816,
#         "beta_1": 0.5614338978580816,
#         "beta_2": 0.20665658577752055
#     },
# ]

# rotor_chord_lengths = [0.024560584036669702, 0.021639381608756177]
# stator_chord_lengths = [0.024560584036669702, 0.021639381608756177]
# rotor_thicknesses = [0.0036840876055004553, 0.0032459072413134264]
# stator_thicknesses = [0.0036840876055004553, 0.0032459072413134264]

# # start_point = (0, 0)
# # start_angle = 0.5307621007232439
# # end_angle = 0.14917070862523912
# # start_to_end_distance = 5
# # plot_bezier_curve(start_point, start_angle, end_angle, start_to_end_distance)

# plot_compressor_blades(blade_angles, rotor_chord_lengths,
#                        stator_chord_lengths, 1, 1)
