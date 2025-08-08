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
        self.position: Vector2 = position
        self.width: int = width
        self.expansion_threshold: int = expansion_threshold
        if not ancestor: # Dumb ass shit that I have to do for tree traversal. Perhaps I should just fix my code and omit this entirely... TODO
            self.ancestor: Quadtree = self
        else:
            self.ancestor: Quadtree = ancestor
        
        self.depth: int = depth
        self.max_depth: int = 20 # This is only accessed in the ancestor and is used to protect us from infinite recursion, this may be fixed and not needed when proper collisions are implemented, but I can't ever say for sure
        if not parent: # Dumb ass shit v2. Yet again to prevent TypeErrors when I do my Moronic™ tree traversal
            self.parent: Quadtree = self
        else:
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
        if not self.ancestor.is_divided:
            return []
        """Find and return all four adjacent Quadtree cells. _Useful for detecting collision between cells._

        Returns:
            _list[Quadtree...]_: _A potentially long list of Quadtree cells adjacent to the current one, at the lowest possible depth._
        """        
        needed_directions = [
            [0, -1], # up
            [0, 1], # down
            [-1, 0], # left
            [1, 0] # right
            # #corners:
            # [-1, -1], #top left
            # [1, -1], #top right
            # [1, 1], #bottom right
            # [-1, 1] #bottom left
        ]
            
        found = [] # Tally our found adjacents
        cell:Quadtree = self.parent # Already found the local parent's cells
        ancestor_loops = 0 # We need to do at least one iteration WITH the ancestor, anything else isn't needed
        while ancestor_loops < 1 and len(needed_directions) > 0:
            if cell == self.ancestor:
                ancestor_loops+=1
            dist_between_cells = (self.width + cell.cells[0][0].width)/2 # Calculate the distance between our cell and cells that would sit next to ours
            for sub_row in cell.cells:
                for sub_cell in sub_row:
                    dx = sub_cell.position.x - self.position.x # sub_cell is first because it makes more sense with negatives
                    dy = sub_cell.position.y - self.position.y
                    
                    # if abs(dx) == dist_between_cells and abs(dy) == dist_between_cells: # Theoretical corner logic, NOT YET IMPLEMENTED!!! TODO
                    #     if dx > 0:
                    #         dx = 1
                    #     elif dx < 0:
                    #         dx = -1                        
                    #     if dy > 0:
                    #         dy = 1
                    #     elif dy < 0:
                    #         dy = -1
                                                
                    if abs(dx) == dist_between_cells and abs(dy) <= sub_cell.width/2: # Check that we are the correct distance, AND ensure that the other direction is within a margin of error
                        dy = 0 
                        if dx > 0:
                            dx = 1
                        elif dx < 0:
                            dx = -1
                    elif abs(dy) == dist_between_cells and abs(dx) <= sub_cell.width/2: # Same but for y
                        dx = 0
                        if dy > 0:
                            dy = 1
                        elif dy < 0:
                            dy = -1
                    
                    
                    if [dx, dy] in needed_directions: # Now we have the first found adjacent cell in a given direction
                        needed_directions.remove([dx, dy])
                        
                        while sub_cell.depth < self.depth and sub_cell.is_divided: #simply traverse down the tree
                            closest = sub_cell.cells[0][0]
                            closest_distance = (self.position - closest.position).length()
                            
                            for row in sub_cell.cells: 
                                for double_sub_cell in row:
                                    distance = (self.position - double_sub_cell.position).length() # finding the closest cells 
                                    if distance < closest_distance:
                                        closest = double_sub_cell
                                        closest_distance = distance
                                        
                            sub_cell = closest # Continue until we sit at the same level as the working cell
                        if sub_cell.is_divided: # The above method doesn't work for cells below ours
                            found += self.find_child_pair_distance(sub_cell)
                        else:
                            found.append(sub_cell)
            cell = cell.parent
        return found
        
        
    def find_child_pair_distance(self, cell:"Quadtree") -> list["Quadtree"]:
        """Finds a pair of children for a given cell that are closest to the cell calling the function, will then utilize find\_child\_pair() to finish the operation far faster.

        Returns:
            _list[Quadtree...]_: _A potentially long list of children Quadtree cells._
        """        
        closest = [None, None]
        closest_distance = [(self.position - cell.cells[0][0].position).length() * 10, (self.position - cell.cells[0][0].position).length() * 10] # Arbitrarily large values, searching for two distances of the same length
        for x, row in enumerate(cell.cells):
            for y, sub_cell in enumerate(row):
                distance = (self.position - sub_cell.position).length()
                if distance < closest_distance[0]:
                    closest[0] = [x, y]
                    closest_distance[0] = distance
                elif distance < closest_distance[1]: # The genius here is that once we find the first distance, the second one will automatically slot into here, no need to validate that they are different
                    closest[1] = [x, y]
                    closest_distance[1] = distance

        return Quadtree.find_child_pair(cell, closest) # Make use of the much faster index-based method
                    
    @staticmethod
    def find_child_pair(cell:"Quadtree", indices:list[list[int, int], list[int, int]]) -> list["Quadtree"]:
        """Finds the pair of children with the given indices, fairly quick operation. Opt for find\_child\_pair\_distance unless you know what you're doing here.

        Returns:
            _list[Quadtree...]_: _A potentially long list of children Quadtree cells._
        """        
        found_cells = []
        if cell.is_divided:
            for index in indices: # Thanks to this data structure's patterns, children cells will repeat the same two indices for as long as you traverse down 
                found_cells += cell.find_child_pair(cell.cells[index[0]][index[1]], indices) # Recursion putting in the work
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