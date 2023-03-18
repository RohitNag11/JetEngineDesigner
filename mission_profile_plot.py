import numpy as np
import matplotlib.pyplot as plt
from src.utils import unit_conv


def midpoint(points):
    return sum(points) / 2


CLIMB_ANGLE = np.deg2rad(5)
DESCENT_ANGLE = np.deg2rad(5)

FIRE_CRUISE_SPEED = 60  # (m/s)

Z1 = 600    # Cruise altitude over fire
Z2 = 35000  # Cruise altitude (normal)

X1 = 1.5            # takeoff point
X2 = X1 + unit_conv.feet2km(Z2) / np.tan(CLIMB_ANGLE)  # top of climb point
X3 = 1500   # end of normal cruise (departure)
# end of descent point (start of fire)
X4 = X3 + unit_conv.feet2km(Z2 - Z1) / np.tan(DESCENT_ANGLE)
X5 = X4 + FIRE_CRUISE_SPEED * 300 / 1000     # end of fire point
# end of climb after fire
X6 = X5 + unit_conv.feet2km(Z2 - Z1) / np.tan(CLIMB_ANGLE)

take_off = np.array([[0, -1, 0], [X1, -1, 0]])
climb_1 = np.array([take_off[1], [X2, -1, Z2]])
cruise_1 = np.array([climb_1[1], [X3, -1, Z2]])
descent_1 = np.array([cruise_1[1], [X4, -1, Z1]])
cruise_2 = np.array([descent_1[1], [X5, -1, Z1]])
climb_2 = np.array([cruise_2[1], [X6, -1, Z2]])
loiter_y = np.linspace(-1, 1, 20)
loiter_x = np.sqrt(250 * (1 - loiter_y**2)) + X6
loiter_z = np.ones(len(loiter_y)) * Z2
loiter = np.array([climb_2[1], [X6, 1, Z2]])
cruise_3 = np.array([loiter[1], [X2, 1, Z2]])
descent_2 = np.array([cruise_3[1], [X1, 1, 0]])
landing = np.array([descent_2[1], [0, 1, 0]])


fig = plt.figure()
ax = plt.axes(projection='3d')
ax.set_xlabel('Distance (km)', labelpad=60)
ax.set_zlabel('Altitude (ft)', labelpad=7)
ax.set_xlim(0, 1800)
ax.set_ylim(-1, 1)
ax.set_zlim(0, 40000)

ax.plot3D(take_off[:, 0], take_off[:, 1], take_off[:, 2], lw=3)
ax.scatter(take_off[1, 0], take_off[1, 1],
           take_off[1, 2], s=30, c='b', label='Take-off')
ax.scatter(climb_1[1, 0], climb_1[1, 1],
           climb_1[1, 2], s=30, c='g', label='Top of Climb')
ax.plot3D(climb_1[:, 0], climb_1[:, 1], climb_1[:, 2],
          lw=3, c='b', label='Climb')
ax.plot3D(cruise_1[:, 0], cruise_1[:, 1],
          cruise_1[:, 2], lw=3, c='g', label='Cruise')
ax.plot3D(descent_1[:, 0], descent_1[:, 1],
          descent_1[:, 2], lw=3, c='orange', label='Descent', ls='-')
ax.plot3D(cruise_2[:, 0], cruise_2[:, 1],
          cruise_2[:, 2], c='r', label='Cruise (over fire)', ls='-')
ax.plot3D(climb_2[:, 0], climb_2[:, 1],
          climb_2[:, 2], c='b', ls='-')
ax.plot3D(loiter_x, loiter_y, loiter_z, c='g', ls='-')
ax.plot3D(cruise_3[:, 0], cruise_3[:, 1], cruise_3[:, 2],
          c='g', ls='-')
ax.plot3D(descent_2[:, 0], descent_2[:, 1],
          descent_2[:, 2], c='orange', ls='-')
ax.plot3D(landing[:, 0], landing[:, 1], landing[:, 2], ls='-')

ax.set_box_aspect(aspect=(10, 0.2, 2))
ax.set_xticks(np.arange(0, 1800, 250), minor=False)
ax.set_yticks([], minor=False)
ax.set_zticks(np.arange(0, 40000, 7000), minor=False)
ax.legend(loc='lower right')

plt.show()
