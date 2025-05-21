# Quadtree-Optimized Particle Simulation

## Brief Description
A 2-Dimensional simple particle simulation made in python that utilizes PyGame for rendering.
Quadtrees are used to optimize O(n^2) collision detection into something more managable, the tree is rebuilt each frame (or iteration).
The Fast Multipole Method (FMM) will eventually be implemented in order to calculate n-body gravity.

Updates are slow because this is a side-project of mine, expect an eventual conversion to C++, which may be a re-factor, a seperate branch, or another repository altogether.

## Up Next:
* Solve collisions for objects in adjacent cells
* Fast Multipole Method (FMM)
* Optimize Quadtrees (May not be an actual issue, they just seem like there may be an error in their derivation)