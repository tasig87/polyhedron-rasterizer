
import numpy as np
from polyhedron import Polyhedron, Vec3
from polyhedron import Primitives as pm



# Constants

# Corner offset
f = 0.5 
# Window pixel width
width = 512
window_resolution = (width,width)
# Camera zoom
zoom = 0.8
# Camera depth slider
cam_distance = 4
#Polygon line thickness
line_wgt = 3


# Projecting Functions

def perspective_map(obj: Polyhedron) -> Polyhedron:
    """
    Projects obj, relative to camera origin of (0,0,0) facing z+, using the perspective formula, and
    then scaling/translating relative to the screen origin. Returns itself. \n
    Despite typing hints, obj also works for individual Vec3 objects. \n
    The outputs vertices' x,y values will be screen coordinate ready.

    """
    return obj.f_transform(
        lambda x,_,z: (width/2) + (x/z)*(zoom)*(width),
        lambda _,y,z: (width/2) + (-y/z)*(zoom)*(width),
        lambda _,y,z: z
    )

def perspective_map_undo(obj: Polyhedron) -> Polyhedron:
    return obj.f_transform(
        lambda x,y,z: (x - (width/2))*z/(zoom*width),
        lambda x,y,z: (y - (width/2))*-z/(zoom*width),
        lambda x,y,z: z
    )

def normal2color(v: Vec3, e:float=1) -> tuple[float,float,float]:
    """
    Converts a unit vector into an RGB int tuple. \n
    projected: If true, then acknowledges that vectors are warped and attempts to rescale them.
    """
    tupled_v = tuple(v.copy().rotate(np.pi*0.25,np.pi*0.25).unit()
                      .f_transform( lambda x,y,z: abs(x**e), lambda x,y,z: abs(y**e), lambda x,y,z: abs(z**e) )
                      .scale(255.9)
                    )
    return ( int(tupled_v[0]), int(tupled_v[1]), int(tupled_v[2]) )





# Polyhedron construction

def polyA(f = 0.5) -> Polyhedron:
    """ Makes the Polyhedron from 25W:TSC. Contained in cube with vertices (-1,-1,-1) and (1,1,1). \n
    f represents a float value in (0,1) to modify the 'irregular corner,' defaults to 0.5."""
    #Helper function to create 21 triangular faces, 3 at a time
    def helpA(x_tuple, a1_tuple, a2_tuple, a3_tuple):
        #a1,a2,a3 must go CCW about corner
        x  = Vec3(*x_tuple)
        a1 = Vec3(*a1_tuple)
        a2 = Vec3(*a2_tuple)
        a3 = Vec3(*a3_tuple)
        return [ [x, a1, a2], [x, a2, a3], [x, a3, a1] ]
    lst = []
    lst += helpA( (-1,-1,-1), (0,0,-1), (-1, 0,0), ( 0,-1,0) )
    lst += helpA( (-1,-1, 1), (0,0, 1), ( 0,-1,0), (-1, 0,0) )
    lst += helpA( (-1, 1, 1), (0,0, 1), (-1, 0,0), ( 0, 1,0) )
    lst += helpA( (-1, 1,-1), (0,0,-1), ( 0, 1,0), (-1, 0,0) )
    lst += helpA( ( 1,-1,-1), (0,0,-1), ( 0,-1,0), ( 1, 0,0) )
    lst += helpA( ( 1,-1, 1), (0,0, 1), ( 1, 0,0), ( 0,-1,0) )
    lst += helpA( ( 1, 1,-1), (0,0,-1), ( 1, 0,0), ( 0, 1,0) )
    lst.append( [Vec3(0,0,1),Vec3(f,f,1),Vec3(1,f,f),Vec3(1,0,0)] )
    lst.append( [Vec3(0,1,0),Vec3(f,1,f),Vec3(f,f,1),Vec3(0,0,1)] )
    lst.append( [Vec3(1,0,0),Vec3(1,f,f),Vec3(f,1,f),Vec3(0,1,0)] )
    lst.append( [Vec3(f,1,f), Vec3(1,f,f), Vec3(f,f,1)] )
    return Polyhedron(lst)

def polyB(l = 1.) -> Polyhedron:
    """ Constructs a cube of length l Polyhedron with opposite vertices at (0,0,0) and (l,l,l).
    Length l defaults to 1."""
    lst = []
    #xy faces
    lst.append( [Vec3(0,0,0), Vec3(l,0,0), Vec3(l,l,0), Vec3(0,l,0)] )
    lst.append( [Vec3(0,0,l), Vec3(0,l,l), Vec3(l,l,l), Vec3(l,0,l)] )
    #xz faces
    lst.append( [Vec3(0,0,0), Vec3(0,0,l), Vec3(l,0,l), Vec3(l,0,0)] )
    lst.append( [Vec3(0,l,0), Vec3(l,l,0), Vec3(l,l,l), Vec3(0,l,l)] )
    #yz faces
    lst.append( [Vec3(0,0,0), Vec3(0,l,0), Vec3(0,l,l), Vec3(0,0,l)] )
    lst.append( [Vec3(l,0,0), Vec3(l,0,l), Vec3(l,l,l), Vec3(l,l,0)] )
    return Polyhedron(lst)

def polyhedron_debug(p: Polyhedron):
    """
    Debugging feature for p. Prints all vertices, edges, and faces of p. 
    """
    print( f"Vertices: {len(p.vertices)}" )
    for i, item in enumerate(p.vertices, 1):
        print(f"{i}. {item}")

    print()
    print( f"Edges: {len(p.edges)}" )
    for i, tuple_item in enumerate(p.edges, 1):
        print(f"{i}. {tuple_item[0]} -- {tuple_item[1]}")

    print()
    print( f"Faces: {len(p.faces)}" )
    for i, inner_list in enumerate(p.faces, 1):
        print(f"{i}. " + " --> ".join(str(obj) for obj in inner_list))

    print()
    print( f"Euler Characteristic: {p.euler_characteristic()}")

    return None






p_original = polyA(0.5)
# p_original = polyB(2).translate(Vec3(-1,-1,-1))
p_original.rotate(0,-np.pi*0.695,np.pi*0.25)
p_original.translate(Vec3(0,0,cam_distance))
#p_original.rotate(0,0,np.pi*0.25), Vec3(0,0,cam_distance)

# polyhedron_debug(p_original)





#Pygame rasterization
import pygame

temp = pygame.Color((100,100,100))
print(temp.hsva)

pygame.init()
screen = pygame.display.set_mode(window_resolution)
pygame.display.set_caption("Polyhedron Demo")
# Following line doesn't seem to work on Linux for some reason
# bg = pygame.transform.scale(pygame.image.load("green_gradient.png"),window_resolution)
delta_time = 0.1
clock = pygame.time.Clock()
frame_rate = 60
angle = 0
t=0

running=True
while running:
    screen.fill((60,0,40))
    # screen.blit(bg)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    t+=delta_time
    # Frame building process begins here





    # Wireframe code
    
    p = p_original.copy()
    p.rotate(4*np.sin(0.05*t)+0.5*np.sin(0.49*t),t*0.21,t*0.5, Vec3(0,0,cam_distance))
    p = perspective_map(p)


    for e in p.edges:
        pygame.draw.line(screen,"white", (e[0].x,e[0].y), (e[1].x,e[1].y),line_wgt)
        
    """
    # Solid face code
    for f in pm.face_render_order( p.faces ):
        f_coords = list(map(lambda v: (int(v.x), int(v.y)), f))
        color = normal2color( Vec3.cross(perspective_map_undo(f[0].copy()),perspective_map_undo(f[1].copy()),perspective_map_undo(f[2].copy())), 1 )
        pygame.draw.polygon(screen,color,f_coords,0)
    """


    # Frame building process ends here
    pygame.display.flip()
    delta_time = clock.tick(frame_rate)/1000
    delta_time = max(0.001, min(0.1, delta_time))
    

















