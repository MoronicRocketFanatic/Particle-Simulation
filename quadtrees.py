import pygame # My favorite rendering library... 
from pygame import Vector2, gfxdraw # ... outshined only by gfxdraw

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
        self.max_depth: int = 20 # This is only acessed in the ancestor and is used to protect us from infinite recursion, this may be fixed and not needed when proper collisions are implemented, but I can't ever say for sure
        self.parent: Quadtree = parent
        self.index: list[int, int] = index
    
        
        self.contents = []
        self.is_divided: bool = False
        self.cells: list[list[Quadtree]] = [[],[]]
        
        # These are only used by the ancestor for debug
        self.positional_checks: int = 0
        self.furthest_depth: int = 1
        self.temp = False
                
        self.monopole = 0
        self.dipole = Vector2()
        

    
    
    def insert(self, object) -> None:
        """Insert an object into this quadtree cell, inserted object needs a position.

        Args:
            object (_Any_): _Object for insertion, preferably a Celestial\_Body._
        """        

        if self.is_divided:
            x = 1
            y = 1
            if object.position.x < self.position.x:
                x = 0
            if object.position.y < self.position.y:
                y = 0
            self.cells[x][y].insert(object)
            return
        
        self.contents.append(object)
        
        if len(self.contents) > self.expansion_threshold and self.depth < self.ancestor.max_depth:
            old_contents = self.contents[:]
            self.contents = []
            self.subdivide()
            for obj in old_contents: # Now that we have split, we need to find the cells that our contents inhabit
                x = 1
                y = 1
                if obj.position.x < self.position.x:
                    x = 0
                if obj.position.y < self.position.y:
                    y = 0
                self.cells[x][y].insert(obj)
    
    
    @staticmethod
    def find_position(quadtree:"Quadtree", position:Vector2) -> "Quadtree":
        """Find and return the Quadtree cell that a given position belongs in.

        Args:
            quadtree (Quadtree): _Quadtree to search._
            position (Vector2): _Position to search with._

        Returns:
            Quadtree: _Found cell._
        """        
        position = Vector2(position.x, position.y) # We operate on the position so we need to make a copy
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
        if not self.index:
            return []
        # Find adjacent sibling cells (Children of those siblings is further down the line):
        horizontal_cell_index = [int(not self.index[0]), self.index[1]] # Cells to either side of a given cell at the same level have inverse x values of the cell, even if they have different parents
        vertical_cell_index = [self.index[0], int(not self.index[1])] # Cells above or below a given cell at the same level have inverse y values of the cell, even if they have different parents
        corner_cell_index = [int(not self.index[0]), int(not self.index[1])] # The corner cells always share an index that is opposite the given cell.
        sides = [] # Left and right
        caps = [] # Top and bottom
        corners = [] # All four corners
        
        needed_directions = [
            [0, -1], # up
            [0, 1], # down
            [-1, 0], # left
            [1, 0] # right
        ]
        
        # Section for left or right sibling cell:
        current_indices = [[0, 0],[0, 1]] 
        side:"Quadtree" = self.parent.cells[horizontal_cell_index[0]][horizontal_cell_index[1]]
        if side.is_divided:
            if self.position.x > side.position.x: # If our current cell is to the right of the found adjacent:
                current_indices[0][0] = 1
                current_indices[1][0] = 1
                needed_directions.pop(2) # remove left
            else:
                needed_directions.pop(3) # remove right
                
            sides += self.find_child_pair(self.parent.cells[horizontal_cell_index[0]][horizontal_cell_index[1]], current_indices)
        else:         
            sides.append(side)
            if self.position.x > side.position.x: # If our current cell is to the right of the found adjacent:
                needed_directions.pop(2) # remove left
            else:
                needed_directions.pop(3) # remove right
        
        # Section for top or bottom sibling cell:
        current_indices = [[0, 0],[1, 0]]
        cap:"Quadtree" = self.parent.cells[vertical_cell_index[0]][vertical_cell_index[1]]
        if cap.is_divided:
            if self.position.y > cap.position.y: # If our current cell is below our found adjacent:
                current_indices[0][1] = 1
                current_indices[1][1] = 1
                needed_directions.pop(0) # remove up
            else:
                needed_directions.pop(1) # remove down
            caps += self.find_child_pair(self.parent.cells[vertical_cell_index[0]][vertical_cell_index[1]], current_indices)
        else:         
            caps.append(cap)
            if self.position.y > cap.position.y: # If our current cell is below our found adjacent:
                needed_directions.pop(0) # remove up
            else:
                needed_directions.pop(1) # remove down

        # Section for corner sibling cell:        
        current_indices = [[0, 0]]
        corner:"Quadtree" = self.parent.cells[corner_cell_index[0]][corner_cell_index[1]]
        if corner.is_divided:
            if self.position.y > corner.position.y:
                current_indices[0][1] = 1
            if self.position.x > corner.position.x:
                current_indices[0][0] = 1
            corners += self.find_child_pair(self.parent.cells[corner_cell_index[0]][corner_cell_index[1]], current_indices)
        else:         
            corners.append(corner)
            
        self.ancestor.temp = [self.index, needed_directions]


        # ----- V ----- NOT YET IMPLEMENTED ----- V -----

        # for direction in needed_directions:
        #     if self.parent and self.parent.parent:
        #         current_cell = self.parent
        #         current_parent = current_cell.parent
        #         x = 0
        #         y = 0
        #         while current_parent.index and [x, y] != direction:
        #             print([current_cell.index[0] + direction[0], current_cell.index[1] + direction[1]])
        #             index_x = 0 if current_cell.index[0] + direction[0] > 1 else current_cell.index[0] + direction[0]
        #             index_y = 0 if current_cell.index[1] + direction[1] > 1 else current_cell.index[1] + direction[1]
                    
        #             potential_cell = current_parent.cells[index_x][index_y]
        #             x = -1 if potential_cell.position.x < self.position.x else 1 if potential_cell.position.x < self.position.x else 0
        #             y = -1 if potential_cell.position.y < self.position.y else 1 if potential_cell.position.y < self.position.y else 0
        #             current_cell = current_parent
        #             current_parent = current_parent.parent
                
        #         if [x, y] == needed_directions:
        #             sides.append(potential_cell)
                
            
        return sides + caps + corners
        
        
        
        
        
        
    
    
    def find_child_pair(self, cell:"Quadtree", indices:list[list[int, int], list[int, int]]) -> list["Quadtree"]:
        found_cells = []
        if cell.is_divided:
            for index in indices:
                found_cells += cell.find_child_pair(cell.cells[index[0]][index[1]], indices)
            # found_cells += cell.find_child_pair(cell.cells[indices[1][0]][indices[1][1]], indices)
        else:
            found_cells.append(cell)
        return found_cells
    
            
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
        except OverflowError:
            print(f"X: {int(self.dipole.x)}, Y: {int(self.dipole.y)}, R: {int(self.monopole**0.5)}")
        
    
        
    def subdivide(self) -> None:
        """Subdivide this Quadtree cell into four other cells.
        """        
        subdivided_size = self.width/2  # Do these operations here to avoid doing them a load of times
        half_sub_size = subdivided_size/2
        #       Coordinate          |                              Center Position                        | Set New width  | Set Expansion Threshold | Mark Ancestor
        self.cells[0].append(Quadtree(Vector2(self.position.x-half_sub_size, self.position.y-half_sub_size), subdivided_size, self.expansion_threshold, self.ancestor, self, [0, 0], self.depth+1)) # DATA STRUCTURE:               (EACH QUADRANT WITH IT'S OWN FOUR QUADRANTS)
        self.cells[0].append(Quadtree(Vector2(self.position.x-half_sub_size, self.position.y+half_sub_size), subdivided_size, self.expansion_threshold, self.ancestor, self, [0, 1], self.depth+1)) # [  0 [Q1, Q2]
        self.cells[1].append(Quadtree(Vector2(self.position.x+half_sub_size, self.position.y-half_sub_size), subdivided_size, self.expansion_threshold, self.ancestor, self, [1, 0], self.depth+1)) #    1 [Q3, Q4]  ] 
        self.cells[1].append(Quadtree(Vector2(self.position.x+half_sub_size, self.position.y+half_sub_size), subdivided_size, self.expansion_threshold, self.ancestor, self, [1, 1], self.depth+1)) #       0    1
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