import pygame
import sys
from pygame import gfxdraw, Vector2
from physics import Celestial_Body, Solver
import physics
import quadtrees
from quadtrees import Quadtree
from misc_tools import rainbow_cycle

# WINDOW_WIDTH, WINDOW_HEIGHT = int(sys.argv[1]), int(sys.argv[2])
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 650
# WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
SCREEN_COLOR = (0,0,0)

display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.mouse.set_cursor(pygame.cursors.arrow)


display_scale = 0.25
display_position = Vector2(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 25)



FPS = 75
engine_clock = pygame.time.Clock()
total_time = 0
delta_time = 1/FPS


DEFAULT_MASS = 2000000
SUBSETS = 1

place_mode = False
dragging = False
mouse_position = pygame.mouse.get_pos()
drag_start = [display_position, mouse_position]

quadtree = Quadtree(Vector2(0, 0), 8000, 5)
celestial_bodies = [Celestial_Body(Vector2(0, 0), 15, DEFAULT_MASS, (0, 50, 255)), Celestial_Body(Vector2(0 + 80, 0), 30, DEFAULT_MASS*2, (255, 165, 0))]

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
                # display_scale += 0.01*display_scale
                display_scale *= 1 + 0.01
            
            elif event.y < 0:
                # display_scale -= 0.01*display_scale
                display_scale *= 1 - 0.01
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                place_mode = not place_mode


                
        # elif event.type == pygame.MOUSEBUTTONDOWN: # Quadtree debug
        #     if pygame.mouse.get_pressed()[2]:
                
        #         mouse_position = Vector2(pygame.mouse.get_pos())
        #         converted_mouse_position = Vector2((mouse_position.x-display_position.x) / display_scale, 
        #                                         (mouse_position.y-display_position.y) / display_scale)

        #         quadtree.find_position(quadtree, deepcopy(converted_mouse_position)).subdivide()
                
                
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
    
    if mouse[0] and place_mode:
        celestial_bodies.append(Celestial_Body(Vector2(converted_mouse_position), 30, DEFAULT_MASS, rainbow_cycle(total_time)))

    elif dragging:
        if mouse[0]:
            display_position = drag_start[0] + mouse_position - drag_start[1]
        else:
            dragging = False
            
    elif mouse[0]:
        dragging = True
        drag_start = [display_position, mouse_position]
        
        
        
    
    # Keypress Handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        display_position += Vector2(0, 1)/display_scale 
    elif keys[pygame.K_s]:
        display_position += Vector2(0, -1)/display_scale
        
    if keys[pygame.K_a]:
        display_position += Vector2(1, 0)/display_scale
    elif keys[pygame.K_d]:
        display_position += Vector2(-1, 0)/display_scale
        
    if keys[pygame.K_UP]:
        # delta_time = 1/FPS
        # color_temp += 10   
        display_scale *= 1.01
    elif keys[pygame.K_DOWN]:
        # delta_time = -1/FPS
        # color_temp -= 10
        display_scale *= 0.99
                    
    if keys[pygame.K_q] and keys[pygame.K_e]:
        celestial_bodies = []
        solver.objects = celestial_bodies
    
    # Update Physics 
    solver.update(delta_time)
    total_time += delta_time
    
    # Render objects
    solver.draw_constraint(display, display_scale, display_position)
    for object in solver.objects:
        object.draw(display, display_scale, display_position)
    
    solver.quadtree.draw_quad(display, (200, 200, 200), display_scale, display_position)
    solver.quadtree.calculate_poles(display, (255, 0, 0), display_scale, display_position)
    gfxdraw.box(display, pygame.Rect(0, 0, 10, 10), rainbow_cycle(total_time))
    
    if int(quadtrees.position_checks/quadtrees.furthest_depth) > len(celestial_bodies):
        temp = f"{int(quadtrees.position_checks/quadtrees.furthest_depth)} > {len(celestial_bodies)}"
    elif int(quadtrees.position_checks/quadtrees.furthest_depth) == len(celestial_bodies):
        temp = f"{int(quadtrees.position_checks/quadtrees.furthest_depth)} == {len(celestial_bodies)}"
    else:
        temp = f"{int(quadtrees.position_checks/quadtrees.furthest_depth)} < {len(celestial_bodies)}"
    
    
    debug_text(display, Vector2(0, 0), f"Quadtree checks: {quadtrees.position_checks}  ||  Quadtree depth: {quadtrees.furthest_depth} || {temp}", debug_font, (200, 200, 200))
    debug_text(display, Vector2(0, 18), f"Collision checks: {physics.collision_checks}", debug_font, (200, 200, 200))
    
    
    # debug_text(display, Vector2(0,0), f"Mouse Position: {converted_mouse_position}", debug_font, (200, 200, 200))
    # quadtree.find_position(quadtree, converted_mouse_position).draw_quad(display, (255, 0, 0), display_scale, display_position)
    # debug_text(display, Vector2(0,18), f"Adjusted Mouse Position: {converted_mouse_position}", debug_font, (200, 200, 200))
    

    
    # Update Screen
    pygame.display.flip()


# Exit
print("Exit successful!")
pygame.quit()
sys.exit()            