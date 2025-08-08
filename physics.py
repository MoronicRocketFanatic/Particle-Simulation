import pygame
from pygame import gfxdraw, Vector2
from quadtrees import Quadtree


class Celestial_Body():
    def __init__(self, position:Vector2, radius:int, mass:int, color:tuple[int,int,int]) -> None:
        """Initialize a Celestial Body object with the given parameters:

        Args:
            position (Vector2): _A Vector2 of the body's position._
            radius (int): _The radius of the body._
            mass (int): _The mass (or gravitational influence) the body will have._
            color (tuple[int,int,int]): _An RGB tuple that describes the color of the body._
        """        
        self.position = position 
        self.radius = radius
        self.mass = mass
        self.color = color
        self.acceleration = Vector2(0,0)
        self.anchored = False # Anchored isn't necessary, but I like extra functionality
        
        self.previous_position = position # This is just for our Verlet calculations
        
      
        
    def draw(self, surface:pygame.Surface, scale:float = 1, offset:Vector2 = Vector2(0,0)) -> None:
        """Utilizes PyGame's experimental GFXDraw module to render the body. Camera scale and offset are used like such: _(body.position * scale) + offset | (body.radius * scale)._ 

        Args:
            surface (pygame.Surface): _PyGame Surface to render on._
            scale (int, optional): _Scale of the rendered body, useful for "camera" implementations._ Defaults to 1.
            offset (Vector2, optional): _Offest of the rendered body, useful for "camera" implementations._ Defaults to Vector2(0,0).
        """        
        self.surface = surface
        try:
            gfxdraw.aacircle(surface, int(self.position.x*scale + offset.x), int(self.position.y*scale + offset.y), int(self.radius*scale), self.color) # Refer to docstring regarding questions on scale or offset
        except OverflowError:
            print(f"{self}: RENDER OVERFLOW") # TODO: Decide what do do with these, perhaps just skip their rendering? Maybe there's another way to go about this
            # self.position = Vector2(0,0) # Only if we need to reset positions...
    
    
    def update_position(self, delta_time:float=1/60) -> None:
        """Update the position of the Celestial_Body given a timestep, please keep this low if you are doing manual stepping with the solver object, it can cause issues with collision detection quality.
        Formula for the postional change: _position + change\_in\_position + (acceleration - change\_in\_position) * delta\_time^2_.

        Args:
            delta_time (float, optional): _Time step._ Defaults to 1/60, this works for a simulation refresh rate of 60 per second and so forth.
        """        
        self.displacement = self.position - self.previous_position # Calculate change in position
        self.previous_position = self.position # Update old position
        
        self.position = self.position + self.displacement + (self.acceleration - self.displacement) * (delta_time*delta_time) # Formula!
        
        self.acceleration = Vector2(0, 0) # Reset acceleration
        



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------






class Solver():
    def __init__(self, objects:list[Celestial_Body], quadtree: "Quadtree", gravity:float = 6.67*10**-11, subsets:int = 8) -> None:
        """Initialize a physics solving object, Solver only works on particles initialized by the Celestial\_Body class for the time being.

        Args:
            objects (list[Celestial_Body]): _Your initial list of Celestial Bodies._
            gravity (float, optional): _Gravitational constant._ Defaults to 6.67*10**-11, also known as the Universe's.
            subsets (int, optional): _Subsets (or physics steps) to run in a timestep, higher will result in lower performance, lower will result in worse simulation quality, keep it balanced._ Defaults to 8.
        """        
        self.objects = objects
        self.subsets = subsets
        self.gravity = gravity
        self.quadtree = quadtree
        
        self.constraint_position = False
        self.constraint_radius = False
        self.constraint_color = (65, 65, 65)
        
        self.collision_checks = 0
        
    
    def create_constraint(self, radius:int, position:Vector2 = Vector2(0,0), color:tuple[int,int,int] = (165, 165, 165)) -> None:
        """Create a circular constraint for the particles.

        Args:
            radius (int): _Constraint size._
            position (Vector2, optional): _Constraint position._ Defaults to Vector2(0,0).
            color (tuple[int,int,int], optional): _Constraint color._ Defaults to (165, 165, 165).
        """        
        self.constraint_position = position
        self.constraint_radius = radius
    
    
    def draw_constraint(self, surface:pygame.Surface, scale:int = 1, offset:Vector2 = Vector2(0,0)) -> None:
        """Draw the particle constraint with PyGame's Experimental GFXDraw module. Camera scale/zoom and offset are used like such: _(body.position * scale) + offset | (body.radius * scale)._ 

        Args:
            surface (pygame.Surface): _Surface to draw on._
            scale (int, optional): _Scale/Zoom of the environment, useful for "camera" implementations._ Defaults to 1.
            offset (Vector2, optional): _Offset/Position of the environment, useful for "camera" implementations._ Defaults to Vector2(0,0).
        """        
        self.constraint_surface = surface
        gfxdraw.filled_circle(surface, int(self.constraint_position.x*scale + offset.x), int(self.constraint_position.y*scale + offset.y), int(self.constraint_radius*scale), self.constraint_color)
        gfxdraw.aacircle(surface, int(self.constraint_position.x*scale + offset.x), int(self.constraint_position.y*scale + offset.y), int(self.constraint_radius*scale), self.constraint_color)
        
    
    def apply_constraint(self) -> None:
        """Solve collisions for the particle constraint, runs in O(n) time complexity, one check for every ball.
        """        
        for body in self.objects:
            collision_axis = body.position - self.constraint_position
            distance = collision_axis.length()
            
            if distance > self.constraint_radius - body.radius:
                try:
                    collision_angle = collision_axis / distance
                except ZeroDivisionError:
                    collision_angle = Vector2()
                body.position = self.constraint_position + collision_angle * (self.constraint_radius - body.radius)
    
        
    def update(self, delta_time:float) -> None:
        """Check collisions and update positions for all particles, done once for each solver substep.

        Args:
            delta_time (_float_): _Physics time step, divided so that each subset has a fraction of the timestep._
        """        
        delta_time = delta_time/self.subsets
        for subset in range(self.subsets):
            self.apply_constraint()
            self.solve_collisions()
            for object in self.objects:
                object.update_position(delta_time)
    
    
    def solve_collisions(self) -> None:
        """Solve collisions for all Celestial Bodies, currently runs in O(n^2) time complexity (each particle compares with every other one), upcoming Quadtree implementation will speed this up substantially.
        """        
        self.quadtree = Quadtree(self.quadtree.position, self.quadtree.width, self.quadtree.expansion_threshold)
        
        for body in self.objects:
            self.quadtree.insert(body)
        
        self.collision_checks = 0
        self.quadtree_collision_check(self.quadtree)
    

    def quadtree_collision_check(self, quadtree:Quadtree) -> None:
        """Check for collisions between all Quadtree contents.

        Args:
            quadtree (Quadtree): _Quadtree full of objects._
        """        
        if quadtree.is_divided: # We need to do this recursively
            for cell_row in quadtree.cells:
                for cell in cell_row:
                    self.quadtree_collision_check(cell)
                    
        else: # Does not yet compare to adjacent Quadtree cells... TODO
            object_pool = []
            object_pool += quadtree.contents
            for cell in quadtree.find_adjacent():
                object_pool += cell.contents
            for body_1 in object_pool:
                for body_2 in object_pool:
                    self.collision_checks+=1 # Increment debug variable
                    
                    if body_1 != body_2:
                        collision_axis = body_1.position - body_2.position # Axis of collision is also the midpoint
                        distance = collision_axis.length()

                        if distance < body_1.radius + body_2.radius: # If the collision axis is shorter than the combined radius then there is a collision
                            try:
                                collision_angle = collision_axis / distance # Now we pretty much normalize the axis to get the angle

                            except ZeroDivisionError:
                                collision_angle = Vector2()

                            
                            overlap = body_1.radius + body_2.radius - distance # Figure out how far the bodies are touching

                            body_1.position += (0.5 * overlap * collision_angle) * (not body_1.anchored) # Include anchored in the off chance that we want that functionality, may be removed further down the line
                            body_2.position -= (0.5 * overlap * collision_angle) * (not body_2.anchored) # Multiply by 0.5 each time because we want to equally distribute the collision between the objects

