from roboticstoolbox import LatticePlanner, OccupancyGrid
import numpy as np

occ_grid = OccupancyGrid(np.zeros((5,5)))

lattice = LatticePlanner(occgrid=occ_grid);
lattice.plan(iterations=6)
path, status = lattice.query(start=(0, 0, 0), goal=(1, 2, np.pi/2))
print(path.T)
print(status)
lattice.plot(path)

input("Press Enter to continue...")