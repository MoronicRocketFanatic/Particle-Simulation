import pygame
import sys
from pygame import gfxdraw, Vector2
from physics import Celestial_Body, Solver
from quadtrees import Quadtree
from misc_tools import rainbow_cycle
from random import randint

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 650
SCREEN_COLOR = (0,0,0)

display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
stored_display_size = WINDOW_WIDTH, WINDOW_HEIGHT
pygame.mouse.set_cursor(pygame.cursors.arrow)


display_scale = 0.25
display_position = Vector2(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 25)



FPS = 75
engine_clock = pygame.time.Clock()
total_time = 0
delta_time = 1/FPS
pause = False

DEFAULT_MASS = 2000000
SUBSETS = 1

debug = 0
dragging = False
mouse_position = pygame.mouse.get_pos()
drag_start = [display_position, mouse_position]

sys.setrecursionlimit(5000000) # Needed, stack overflow is not really gonna happen with how the recursion is built
quadtree = Quadtree(Vector2(0, 0), 8000, 3)
celestial_bodies = [Celestial_Body(Vector2(0, 0), 15, DEFAULT_MASS, (0, 50, 255)), Celestial_Body(Vector2(0 + 80, 0), 30, DEFAULT_MASS*2, (255, 165, 0))]

# for body in range(5000): # Uncomment for spawning of 5000 random objects
#     celestial_bodies.append(Celestial_Body(Vector2(randint(-3800, 3800), randint(-3800, 3800)), randint(15, 45), DEFAULT_MASS*randint(1, 5), rainbow_cycle(body/10)))

solver = Solver(celestial_bodies, quadtree, subsets=8)
solver.create_constraint(8000/2, Vector2(0, 0))


pygame.font.init()
debug_font = pygame.font.SysFont("Arial", 18, bold=True)
def debug_text(display: pygame.Surface, position: Vector2, text: str, font: pygame.Font, color: tuple[int,int,int]):
    text = font.render(text, True, color)
    display.blit(text, position)



running = True
while running:
    # Clear Screen
    display.fill(SCREEN_COLOR)
    
    # Manage Framerate
    engine_clock.tick(FPS)
    pygame.display.set_caption(f"Orbiter (PHYSICS ENGINE) | FPS: {int(engine_clock.get_fps())} | SCALE: {round(display_scale, 4)} | DeltaTime: {delta_time} | TotalDT: {total_time} | Total Bodies: {len(celestial_bodies)}")
    
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Attempting exit...")
            running = False
            
        elif event.type == pygame.MOUSEWHEEL: # Display Scaling
            if event.y > 0:
                display_scale *= 1.01
            
            elif event.y < 0:
                display_scale *= 0.99
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE: # Just a scene clear
                solver.objects = []
                celestial_bodies = solver.objects
            elif event.key == pygame.K_F9:
                if debug == 3:
                    debug = 0
                else:
                    debug +=1 
            elif event.key == pygame.K_F10:
                pause = not pause
            elif event.key == pygame.K_F11:
                sizes = pygame.display.get_desktop_sizes()
                if not pygame.display.is_fullscreen():
                    display = pygame.display.set_mode(sizes[0], pygame.RESIZABLE)
                    WINDOW_WIDTH, WINDOW_HEIGHT = sizes[0]
                    pygame.display.toggle_fullscreen()
                else:
                    pygame.display.toggle_fullscreen()
                    display = pygame.display.set_mode(stored_display_size, pygame.RESIZABLE)
                

                
        elif event.type == pygame.VIDEORESIZE:
            WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.get_window_size()
            print(f"{WINDOW_WIDTH}X{WINDOW_HEIGHT}")
                

    
    # Mouse Management
    mouse = pygame.mouse.get_pressed()
    mouse_position = Vector2(pygame.mouse.get_pos())
    converted_mouse_position = Vector2((mouse_position.x-display_position.x) / display_scale, 
                                       (mouse_position.y-display_position.y) / display_scale)
    gfxdraw.aacircle(display,  # Mouse selection
                     int(converted_mouse_position.x*display_scale + display_position.x), # X
                     int(converted_mouse_position.y*display_scale + display_position.y), # Y
                     10, # Radius
                     (255, 0, 0)) # Color
    
    if mouse[0]:
        celestial_bodies.append(Celestial_Body(Vector2(converted_mouse_position), 30, DEFAULT_MASS, rainbow_cycle(total_time)))

    elif dragging:
        if mouse[2]:
            display_position = drag_start[0] + mouse_position - drag_start[1]
        else:
            dragging = False
            
    elif mouse[2]:
        dragging = True
        drag_start = [display_position, mouse_position]
        
        
        
    
    # Keypress Handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        display_position += Vector2(0, 1)/display_scale # this way allows the speed of the camera to be relative to the scale of the screen
    elif keys[pygame.K_s]:
        display_position += Vector2(0, -1)/display_scale
        
    if keys[pygame.K_a]:
        display_position += Vector2(1, 0)/display_scale
    elif keys[pygame.K_d]:
        display_position += Vector2(-1, 0)/display_scale
        
    if keys[pygame.K_UP]:  
        display_scale *= 1.01
    elif keys[pygame.K_DOWN]:
        display_scale *= 0.99
                    
    if keys[pygame.K_q] and keys[pygame.K_e]:
        celestial_bodies = []
        solver.objects = celestial_bodies
    
    # Update Physics 
    if not pause:
        solver.update(delta_time)
        total_time += delta_time
        
    # Render objects
    solver.draw_constraint(display, display_scale, display_position)
    for object in solver.objects:
        object.draw(display, display_scale, display_position)
    if debug >= 1:
        solver.quadtree.draw_quad(display, (200, 200, 200), display_scale, display_position)
        gfxdraw.box(display, pygame.Rect(0, 0, 10, 10), rainbow_cycle(total_time))
    

    # ---------------DEBUG----------------- (can be commented out and functionality will not be hindered)
    if debug >= 3:
        if int(solver.quadtree.positional_checks/solver.quadtree.furthest_depth) > len(celestial_bodies):
            temp = f"{int(solver.quadtree.positional_checks/solver.quadtree.furthest_depth)} > {len(celestial_bodies)}"
        elif int(solver.quadtree.positional_checks/solver.quadtree.furthest_depth) == len(celestial_bodies):
            temp = f"{int(solver.quadtree.positional_checks/solver.quadtree.furthest_depth)} == {len(celestial_bodies)}"
        else:
            temp = f"{int(solver.quadtree.positional_checks/solver.quadtree.furthest_depth)} < {len(celestial_bodies)}"
    

        debug_text(display, Vector2(0, 0), f"Quadtree checks: {solver.quadtree.positional_checks}  ||  Quadtree depth: {solver.quadtree.furthest_depth} || {temp}", debug_font, (200, 200, 200))
        debug_text(display, Vector2(0, 18), f"Collision checks: {solver.collision_checks}", debug_font, (200, 200, 200))
    
    # try:
    if debug >= 1:
        mouse_quad = Quadtree.find_position(solver.quadtree, converted_mouse_position)
        mouse_quad.draw_quad(display, (255, 0, 0), display_scale, display_position)
        adjacent = mouse_quad.find_adjacent()
        if debug >= 2:
            for cell in adjacent:
                cell.draw_quad(display, (0, 0, 255), display_scale, display_position)
            try:
                debug_text(display, Vector2(0, 36), f"Current  Index: {solver.quadtree.temp[0]}", debug_font, (200, 200, 200))
                debug_text(display, Vector2(0, 54), f"Needed Directions: {solver.quadtree.temp[1]}", debug_font, (200, 200, 200))
                debug_text(display, Vector2(0, 72), f"Found Cell: {solver.quadtree.temp[2]}", debug_font, (200, 200, 200))
            except: # Bare except... spooky!
                pass
    # ---------------DEBUG-----------------

    
    # Update Screen
    pygame.display.flip()


# Exit
print("Exit successful!")
pygame.quit()
sys.exit()            