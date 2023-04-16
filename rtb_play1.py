from roboticstoolbox import LatticePlanner, OccupancyGrid
import numpy as np

width = 10
height = 10
contents = np.zeros((height, width))
#contents[2:height, width//2] = 1
contents[2:height, width//2] = 1

occ_grid = OccupancyGrid(contents)

lattice = LatticePlanner(occgrid=occ_grid);
lattice.plan(iterations=10)
path, status = lattice.query(start=(0, 0, 0), goal=(width-1, 2, np.pi/2))
print(path.T)
print(status)
lattice.plot(path)

input("Press Enter to continue...")