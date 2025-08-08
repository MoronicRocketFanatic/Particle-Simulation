# Quadtree-Optimized Particle Simulation
To run source, PyGame or PyGame-CE is required, `pip install pygame-ce`
## Brief Description
A 2-Dimensional simple particle simulation made in python that utilizes PyGame for rendering.
Quadtrees are used to optimize O(n^2) collision detection into something more managable, the tree is rebuilt each frame (or iteration).
The Fast Multipole Method (FMM) will eventually be implemented in order to calculate n-body gravity.

Updates are slow because this is a side-project of mine, expect an eventual conversion to C++, which may be a re-factor, a seperate branch, or another repository altogether.

## Up Next:
* Solve collisions for objects in adjacent (corner) cells
* Fast Multipole Method (FMM)
* Optimize Quadtrees (May not be an actual issue, they just seem like there may be an error in their derivation)


### Basic Controls:
* WASD to move the camera.
* Right click and drag to pan.
* Hold left click to create new particles.
* Scroll wheel (or up and down arrow keys) to zoom.
* F9 to cycle through the three debug levels
* F10 to pause the engine's update cycle.
* F11 to toggle rudimentary fullscreen. 
* Q+E or del to remove all objects.