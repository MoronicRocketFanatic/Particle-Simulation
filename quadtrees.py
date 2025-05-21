import pygame # My favorite rendering library... 
from pygame import Vector2, gfxdraw # ... outshined only by gfxdraw
from copy import deepcopy

class Quadtree():
    
    def __init__(self, position:Vector2, width:int, expansion_threshold:int, ancestor:"Quadtree" = False, parent: "Quadtree" = False, index: list[int, int] = False,  depth:int = 1) -> None:
        """Initialize a Quadtree cell with the given information.

        Args:
            position (Vector2): _The position of this cell._
            width (int): _The width of this cell._
            expansion_threshold (int): _The maximum amount of values allowed in the contents of the cell before it will subdivide._
            ancestor (Quadtree, optional): _The root/ancestor cell of the Quadtree._. Defaults to self (this works for root cells).
            depth (int, optional): _Recursive depth of the cell, purely for debugging and completely optional._. Defaults to 1.
        """        
        self.position: Vector2 = position
        self.width: int = width
        self.expansion_threshold: int = expansion_threshold
        if not ancestor:
            self.ancestor: Quadtree = self
        else:
            self.ancestor: Quadtree = ancestor
        
        self.depth: int = depth
        self.parent: Quadtree = parent
        self.index: list[int, int] = index
        
        
        self.contents = []
        self.is_divided: bool = False
        self.cells: list[list[Quadtree]] = [[],[]]
        
        # These are only used by the ancestor for debug
        self.positional_checks: int = 0
        self.furthest_depth: int = 1
                
        self.monopole = 0
        self.dipole = Vector2()
        

    
    
    def insert(self, object) -> None:
        """Insert an object into this quadtree cell, inserted object needs a position.

        Args:
            object (_Any_): _Object for insertion, preferably a Celestial\_Body._
        """        
        self.contents.append(object)
        
        if len(self.contents) > self.expansion_threshold:
            self.subdivide()
            for obj in self.contents: # Now that we have split, we need to find the cells that our contents inhabit
                self.find_position(self.ancestor, obj.position).contents.append(obj)
            self.contents = []
    
    
    @staticmethod
    def find_position(quadtree:"Quadtree", position:Vector2) -> "Quadtree":
        """Find and return the Quadtree cell that a given position belongs in.

        Args:
            quadtree (Quadtree): _Quadtree to search._
            position (Vector2): _Position to search with._

        Returns:
            Quadtree: _Found cell._
        """        
        position = deepcopy(position) # We operate on the position so we need to make a copy
        position += Vector2(quadtree.width//2, quadtree.width//2) # adjust for slight offset
        while quadtree.is_divided:
            try:
                x = int(position.x // (quadtree.width/2)) # Integer division is the driving force of this algorithm
                y = int(position.y // (quadtree.width/2))
            except ZeroDivisionError: # Don't forget to avoid errors
                x, y = 0, 0
                
            if x == 1: # If the result of the division is greater than or equal to one, we MUST adjust accordingly
                position.x -= quadtree.width/2
            if y == 1: 
                position.y -= quadtree.width/2
                
            
            quadtree = quadtree.cells[x][y]
            quadtree.ancestor.positional_checks += 1 # Keep track for debugging
        return quadtree
            
            
    def find_adjacent(self) -> list["Quadtree"]:
        top = []
        right = []
        bottom = []
        left = []
        

        
    
            
    def calculate_poles(self, surface:pygame.Surface, color:tuple[int, int, int] = (255, 0, 0), scale:float = 1, offset: Vector2 = Vector2(0, 0)) -> None:  
        """Calculate and render the monopole and dipole of this Quadtree cell.

        Args:
            surface (pygame.Surface): _Surface to render to._
            color (tuple[int, int, int], optional): _Color of the pole._. Defaults to (255, 0, 0) / Red.
            scale (float, optional): _Scale of the pole._. Defaults to 1.
            offset (Vector2, optional): _Offset of the Pole._. Defaults to Vector2(0, 0).
        """        
        self.monopole = 0
        self.dipole = Vector2() #PyGame Vector2
        
        if self.is_divided: # Calculate from child cells
            for row in self.cells:
                for quad in row: # Iterate over cells
                    quad.calculate_poles(surface, color, scale, offset) # First find the poles of the cell
                    self.monopole += quad.monopole # Now add the mass to our total
                    self.dipole += quad.dipole * quad.monopole # Add the cell's position (as a PyGame Vector2) times the times its mass (as shown in m_i(x_i, y_i))
            
            if self.monopole > 0:
                self.dipole /= self.monopole
            
        else: # Calculate from particles
            for object in self.contents: # iterate over particles 
                self.monopole += object.mass # add mass
                self.dipole += object.position * object.mass # Add the position (as a PyGame Vector2) times the object's mass (as shown in m_i(x_i, y_i))
            
            if self.monopole > 0:
                self.dipole /= self.monopole 

        try:
            gfxdraw.aacircle(surface, int(self.dipole.x * scale + offset.x), int(self.dipole.y * scale + offset.y), int((self.monopole**0.25) * scale), color)
            # print(int((self.monopole**0.1)*(self.width//8)))
        except OverflowError:
            print(f"X: {int(self.dipole.x)}, Y: {int(self.dipole.y)}, R: {int(self.monopole**0.5)}")
        
    
        
    def subdivide(self) -> None:
        """Subdivide this Quadtree cell into four other cells.
        """        
        subdivided_size = self.width/2  # Do these operations here to avoid doing them a load of times
        half_sub_size = subdivided_size/2
        #       Coordinate          |                              Center Position                        | Set New width  | Set Expansion Threshold | Mark Ancestor
        self.cells[0].append(Quadtree(Vector2(self.position.x-half_sub_size, self.position.y-half_sub_size), subdivided_size, self.expansion_threshold, self.ancestor, self, self.depth+1)) # DATA STRUCTURE:               (EACH QUADRANT WITH IT'S OWN FOUR QUADRANTS)
        self.cells[0].append(Quadtree(Vector2(self.position.x-half_sub_size, self.position.y+half_sub_size), subdivided_size, self.expansion_threshold, self.ancestor, self, self.depth+1)) # [  0 [Q1, Q2]
        self.cells[1].append(Quadtree(Vector2(self.position.x+half_sub_size, self.position.y-half_sub_size), subdivided_size, self.expansion_threshold, self.ancestor, self, self.depth+1)) #    1 [Q3, Q4]  ] 
        self.cells[1].append(Quadtree(Vector2(self.position.x+half_sub_size, self.position.y+half_sub_size), subdivided_size, self.expansion_threshold, self.ancestor, self, self.depth+1)) #       0    1
        self.is_divided = True
        
        if self.depth + 1 > self.ancestor.furthest_depth: # This is for debugging
            self.ancestor.furthest_depth = self.depth + 1
        
    
    def draw_quad(self, surface: pygame.Surface, color: tuple[int, int, int] = (200, 200, 200), scale: float = 1, offset: Vector2 = Vector2(0, 0)) -> None:
        """Use PyGame.gfxdraw to recursively render all child cells of this Quadtree, exists purely for debug.

        Args:
            surface (pygame.Surface): _PyGame Surface to render on._
            color (tuple[int, int, int], optional): _Color of the rendered Quadtree cell._. Defaults to (200, 200, 200).
            scale (int, optional): _Scale of the rendered Quadtree cell, useful for "camera" implementations._ Defaults to 1.
            offset (Vector2, optional): _Offest of the rendered Quadtree cell, useful for "camera" implementations._ Defaults to Vector2(0,0).
        """        
        # scaled_width = self.width * scale
        # rect = pygame.Rect((self.position.x*scale + offset.x) - scaled_width//2, (self.position.y*scale + offset.y) - scaled_width//2, scaled_width, scaled_width)
        # gfxdraw.rectangle(surface, rect, color)
        
        # The above solution (drawing the rect) although likely more efficient seems to have some precision issues.
        points = [Vector2(self.position.x - self.width / 2, self.position.y - self.width / 2) * scale + offset, 
                       Vector2(self.position.x + self.width / 2, self.position.y - self.width / 2) * scale + offset, 
                       Vector2(self.position.x + self.width / 2, self.position.y + self.width / 2) * scale + offset, 
                       Vector2(self.position.x - self.width / 2, self.position.y + self.width / 2) * scale + offset]
        gfxdraw.polygon(surface, points, color)
        
        
        if self.is_divided: # This is a recursive function of course.
            for cell_row in self.cells:
                for cell in cell_row:
                    cell.draw_quad(surface, color, scale, offset)