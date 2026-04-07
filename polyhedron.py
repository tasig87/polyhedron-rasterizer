
# Creator: Tasnim Islam
"""
A mini-library containing Primitives, Vec3, and Polyhedron

Primitives: A collection of useful functions in computational geometry, particularly pertaining
  to orientation and intersection functions on polygons and lines in 3D.
Vec3: A run-of-the-mill R3 vector class, which is useful for representing coordinates or colors in 3D.
Polyhedron: A class used for storing and modifying Polyhedrons. Vertices are stored as Vec3 objects,
  and faces/edges are stored as collections of Vec3 objects.
"""





import numpy as np
import networkx as nx

class Primitives:
    """
    Niche functions associated with Vec3 and Polyhedron classes.
    """
    def __init__(self):
        return True

    def left_test(a:Vec3, b:Vec3, c:Vec3, right_test = False, strict=False) -> bool:
        """ Given three points a,b,c, returns true if the z component in ab x ac
        is positive. Alternatively, returns True when... \n
        - a>b>c is in CCW winding order from top-down perspective, or when normal is facing Z+. \n
        - a>b>c is in CW winding order when normal is facing Z- (out of the screen). \n
        right_test: Flips parity of test. \n
        strict: If True, collinear points won't pass the left test.
        """
        z = Vec3.cross(a,b,c).z
        if right_test:
            z*=-1
        if strict:
            return z > 0
        return z >= 0
    
    def polygon_overlap(p_a: list[Vec3], p_b: list[Vec3], strict = True) -> bool:
        """
        For a convex polygon, p_a, and a set of Vec3, p_b, returns True if the projection
        of these sets onto the xy-plane, p_a' and p_b', share a common area. \n
        While p_b is expected to be a convex polygon, it can also be a singular vertex
        in the form [v], or an arbitrary set of points with no particular restriction. \n
        strict: If True, then adjacent/tangential sets are NOT considered to be overlapping. \n
        """

        z_up = Primitives.left_test(p_a[0],p_a[1],p_a[2], True)

        for i in range(len(p_a)):
            a_c, a_n = p_a[i], p_a[(i+1)%len(p_a)]

            for j in range(len(p_b)):
                b_c = p_b[j]
                if Primitives.left_test(a_c,a_n,b_c,z_up,strict): break
                if j == len(p_b)-1:
                    return False #If code ever reaches this point, then a separating axis has been found

        return True #If code reaches this point, then no separating axis was found.

    def get_plane(p: list[Vec3]) -> function:
        """
        Given a list of 3+ points or a polygon p, returns the planar function in the form f(x,y)=z.
        This function assumes that the first 3 vertices are linearly independent and does NOT
        verify if the additional vertices are coplanar.
        """
        n = Vec3.cross(p[0],p[1],p[2])
        return lambda x,y: -(n.x*(x-p[0].x) + n.y*(y-p[0].y))/n.z + p[0].z

    def intersection_test(a1:Vec3, a2:Vec3, b1:Vec3, b2:Vec3, strict = True) -> bool:
        """
        Given two lines, a and b, defined by their endpoints, returns True if the projected
        lines share any common point. \n
        strict: If True, then the intersection point must be unique/singular (no line overlap),
        and may not be any of the endpoints themselves.
        """
        # Not even gonna bother explaining this boolean logic it just works okay
        b1L = Vec3.cross(a1,a2,b1).z
        b2R = Vec3.cross(a1,a2,b2).z
        a1L = Vec3.cross(b1,b2,a1).z
        a2R = Vec3.cross(b1,b2,a2).z

        for i in [a1L, a2R, b1L, b2R]:
            if i<0:    i=1  #Right
            elif i==0: i=0  #On
            else:      i=-1 #Left
        
        if a1L==0 or a2R==0: a1L = not strict
        else: a1L = (a1L != a2R)
        if b1L==0 or b2R==0: b1L = not strict
        else: b1L = (b1L != b2R)

        return a1L and b1L
                
    def get_intersection(a1:Vec3, a2:Vec3, b1:Vec3, b2:Vec3) -> tuple[float,float]:
        """
        Assuming the projection of line a and line b strongly intersect, finds the (x,y)
        point at which it happens.
        """
        x1,x2,x3,x4,y1,y2,y3,y4 = a1.x,a2.x,b1.x,b2.x,a1.y,a2.y,b1.y,b2.y
        d = (y2-y1)*(x3-x4) - (y4-y3)*(x1-x2)
        xn = (x1*y2-x2*y1)*(x3-x4) - (x3*y4-x4*y3)*(x1-x2)
        yn = (x3*y4-x4*y3)*(y2-y1) - (x1*y2-x2*y1)*(y4-y3)
        return (xn/d,yn/d)

    def piercing_ray(p_a: list[Vec3], p_b: list[Vec3]) -> tuple[float,float]:
        """
        Given two polygons with the assumption they are convex and their projections onto the xy-plane
        strongly overlap, Identifies a ray parallel to Z that pierces p_a and p_b at two distinct
        z-levels, returned as a tuple representing (x,y) coordinates.
        """
        # Case 1: Vertex of A found in B
        for v in p_a:
            if Primitives.polygon_overlap(p_b,[v], True):
                return (v.x, v.y)
        # Case 2: Vertex of B found in A
        for v in p_b:
            if Primitives.polygon_overlap(p_a,[v], True):
                return (v.x, v.y)
        # Case 3: No vertex of one in other, look at intersections
        for i in range(len(p_a)):
            edge_a = p_a[i], p_a[(i+1)%len(p_a)]
            for j in range(len(p_b)):
                edge_b = p_b[j], p_b[(j+1)%len(p_b)]
                if Primitives.intersection_test(*edge_a, *edge_b, True):
                    return Primitives.get_intersection(*edge_a, *edge_b)
        # Case 4: A and B are (somehow) perfectly coincident, super unlikely
        for v_a in p_a:
            for v_b in p_b:
                if v_a.x == v_b.x and v_a.y == v_b.y and v_a.z != v_b.z:
                    return (v_a.x, v_a.y)
        # Case 5: Failsafe, use the weighted average of the vertices for a best guess
        x_avg, y_avg = 0, 0
        for v in p_a + p_b:
            x_avg += v.x
            y_avg += v.y
        print("Piercing Ray failed to find a proper point!")
        return v_a.x/(len(p_a)+len(p_b)) , v_a.y/(len(p_a)+len(p_b))

    def face_render_order( input_faces: list[list[Vec3]] ) -> list[list[Vec3]]:
        """
        Given the projection of a Polyhedron, proj_p, returns the faces in order of highest to lowest
        priority render order. The projection on Polyhedron p is expected to already be in a
        format where the x,y values of it's internal vertices are what will be directly output to
        a display. If given a Polyhedron as is, then this will default to a orthographic projection. 
        """
        d = {}
        priority_graph = nx.DiGraph()

        d_len = 0
        #Cull unseen faces (backside of object) based on if normal is facing screen (Z-)
        for f in input_faces:
            if Primitives.left_test(f[0],f[1],f[2], True, True):
                d[d_len] = f
                priority_graph.add_node(d_len)
                d_len+=1


        #For every unique pair of faces in faces
        for i in range(d_len):
            for j in range(i+1, d_len):
                #Skip case if priority between i and j as already been resolved by ancestry
                if priority_graph.has_edge(i,j) or priority_graph.has_edge(j,i):
                    continue
                if Primitives.polygon_overlap(d[i],d[j]):
                    
                    plane_i, plane_j = Primitives.get_plane(d[i]), Primitives.get_plane(d[j])
                    x,y = Primitives.piercing_ray(d[i],d[j])
                    
                    if plane_i(x,y) > plane_j(x,y): p_G, p_L = i, j
                    else:                           p_L, p_G = i, j

                    priority_graph.add_edge(p_G, p_L)
                    for p_ancestor in nx.ancestors(priority_graph,p_G):
                        priority_graph.add_edge(p_ancestor,p_L)
                    for p_descendant in nx.descendants(priority_graph,p_L):
                        priority_graph.add_edge(p_G,p_descendant)

        ordered_faces = []
        for i in list(nx.topological_sort(priority_graph)):
            ordered_faces.append(d[i])
        return ordered_faces


class Vec3:
    """
    Your run of the mill Vec3 class, needs 3 float values for initialization. \n
    Supports the following operators: { + , - , \\* , ==, iter }. \n
    Standard functions include:
    cross(), dot(), copy(), unit(), length() \n
    Self transformation functions include:
    translate(), scale(), transform(), f_transform() 
    """
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    # +, -, *, ==, != operators
    def __add__(self, other):
        return Vec3( self.x+other.x, self.y+other.y, self.z+other.z )
    def __sub__(self, other):
        return Vec3( self.x-other.x, self.y-other.y, self.z-other.z )
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vec3( self.x*other, self.y*other, self.z*other )
        elif isinstance(other, Vec3):
            return Vec3.dot(self,other)
        elif isinstance(other, (list, np.ndarray)):
            return Vec3(self.x, self.y, self.z).transform(other)
        else:
            return NotImplemented
    def __rmul__(self, c):
        return self * c
    def __neg__(self):
        return self * -1
    def __eq__(self, other):
        return (self.x==other.x) and (self.y==other.y) and (self.z==other.z)
    def __ne__(self, other):
        return not self == other
    def __str__(self):
        return f"[{self.x:.3f}, {self.y:.3f}, {self.z:.3f}]"
    def __hash__(self):
        return hash((self.x,self.y,self.z))
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def length(self) -> float:
        """Returns vector norm as float."""
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def unit(self, rescale:float=1) -> Vec3:
        """
        Scales self to become a unit vector.\n
        rescale: Defaults to 1 for unit vector, but can rescale vector to be of designated length instead.
        """
        if (self.x==0) and (self.y==0) and (self.z==0): return 0
        self*=rescale/self.length()
        return self

    def translate(self, v:Vec3):
        """
        Translates self by shifting by Vector v. Also achieved by using '+='
        operator.
        """
        self.x += v.x
        self.y += v.y
        self.z += v.z
        return self

    def scale(self, c:float):
        """
        Scales self by a linear factor of c. Also achieved by using '*='
        operator.
        """
        self.x*=c
        self.y*=c
        self.z*=c
        return self

    def transform(self, M):
        """
        Transforms self by matrix multiplcation with M.
        Also achieved with '\\*=' operator.
        If you wish to return a separate instance, use '*' operator instead.
        """
        self.x, self.y, self.z = tuple(np.array(tuple(self)) @ np.array(M))
        return self

    def f_transform(self, fx: function, fy: function, fz: function):
        """
        Transforms self using three input functions that each
        take in x, y, and z. Eg: x' = fx(x,y,z).
        """
        self.x = fx(self.x, self.y, self.z)
        self.y = fy(self.x, self.y, self.z)
        self.z = fz(self.x, self.y, self.z)
        return self

    def rotate(self, x0:float=0, y0:float=0, z0:float=0):
        """
        Rotates self with angles x0, y0, and z0 which
        each rotate CCW about the respective axis.
        """
        a,b,g,s,c = x0, y0, z0, np.sin, np.cos
        rotation_matrix = np.array([
            [c(b)*c(g), s(a)*s(b)*c(g) - c(a)*s(g), c(a)*s(b)*c(g)+s(a)*s(g)],
            [c(b)*s(g), s(a)*s(b)*s(g) + c(a)*c(g), c(a)*s(b)*s(g)-s(a)*c(g)],
            [-s(b), s(a)*c(b), c(a)*c(b)]
        ])
        return self.transform(rotation_matrix)

    def cross(a: Vec3, b: Vec3, c: Vec3 = None) -> Vec3:
        """
        Returns a x b.
        If a third Vector, c, is included, returns ab x ac. 
        """
        if c is None:
            u, v = a, b
        else:
            u, v = b-a, c-a
        return Vec3( u.y*v.z-u.z*v.y, u.z*v.x-u.x*v.z, u.x*v.y-u.y*v.x )
    
    def dot(u: Vec3, v: Vec3) -> float:
        """
        Returns dot product of Vec3s u and v. Also achieved by using '*' operator.
        """
        return u.x*v.x + u.y*v.y + u.z*v.z

    def copy(self):
        """Returns copy of self."""
        return Vec3(self.x,self.y,self.z)


class Polyhedron:
    """
    Intialized using a list[list[Vec3]], which represent the faces of the
    polyhedron. Each sublist represents a face with
    the vertices going in CCW wrt an outward facing normal. \n
    vertices: A list of all unique vertices used in the polyhedron's faces and edges. \n
    edges: A list of unique, unordered tuplets that contain all
    pairs of vertices that share an edge. \n
    faces: A copy of the instantiation argument, but uses the internal vertices. \n
    Self transformation functions include:
    translate(), scale(), transform(), f_transform(), rotate()
    """

    def get_vector(self, v) -> Vec3:
        """
        Returns Vec3 from Polyhedron instance's internal library
        with designated coordinates. Will return False if not found. \n
        WARNING: modifying an individual vector will no longer guarantee
        that the faces are planar.
        """
        key = tuple(v)
        if key not in self._vec3_cache:
            return False
        return self._vec3_cache[key]

    def _get_vector(self, v: Vec3) -> Vec3:
        key = tuple(v)
        if key not in self._vec3_cache:
            self._vec3_cache[key] = Vec3(key[0], key[1], key[2])
        return self._vec3_cache[key]
    
    def __init__(self, faces: list[list[Vec3]]):
        self._vec3_cache = {}
        self.faces: list[list[Vec3]] = []
        self.vertices: list[Vec3] = []
        self.edges: list[tuple[Vec3,Vec3]] = []

        for f in faces:
            internal_f = []
            for i in range(len(f)):
                # Create/access copies of vectors within class cache
                v_c = self._get_vector( f[i] )
                v_n = self._get_vector( f[(i+1)%len(f)] )
                # Add vertices to internal list
                if v_c not in self.vertices: self.vertices.append(v_c)
                # Add UNIQUE (hence the condition) edges to internal list
                if hash(v_c) <= hash(v_n): self.edges.append( (v_c,v_n) )
                # Construct face
                internal_f.append(v_c)
            self.faces.append(internal_f)
        return None
    
    def euler_characteristic(self) -> int:
        """ Returns the Euler characteristic of the polyhedron (F+V-E), useful
        for debugging incomplete polyhedrons or incorrectly oriented faces.
        For a polyhedron without holes, this is expected to be equal to 2.
        """
        return len(self.faces) + len(self.vertices) - len(self.edges)

    def copy(self):
        """Returns a copy of self; Vec3 instances in copy are distinct."""
        return Polyhedron(self.faces)

    def scale(self, c:float, origin:Vec3=None):
        """ Scales self by a linear factor of c.
        Origin changes center of scaling."""
        if origin is None:
            for v in self.vertices: v.scale(c)
            return self
        else:
            self.translate(-origin)
            for v in self.vertices: v.scale(c)
            self.translate(origin)
            return self
    
    def translate(self, t_v:Vec3):
        """ Translates all vectors in self by Vector t_v."""
        for v in self.vertices: v.translate(t_v)
        return self

    def transform(self, M, origin:Vec3=None):
        """ Transforms self by matrix multiplcation with M.
        Origin changes center of transform."""
        if origin is None:
            for v in self.vertices: v.transform(M)
            return self
        else:
            self.translate(-origin)
            for v in self.vertices: v.transform(M)
            self.translate(origin)
            return self
    
    def f_transform(self, fx: function, fy:function, fz:function, origin:Vec3=None):
        """ Transforms self using three input functions that each take in
        x, y, and z. (Ex: x' = fx(x,y,z).)
        Origin changes center of functional transform."""
        if origin is None:
            for v in self.vertices: v.f_transform(fx, fy, fz)
            return self
        else:
            self.translate(-origin)
            for v in self.vertices: v.f_transform(fx, fy, fz)
            self.translate(origin)
            return self
    
    def rotate(self, x0: float=0, y0: float=0, z0: float=0, origin:Vec3=None):
        """
        Rotates self with angles x0, y0, and z0 which
        each rotate CCW about their respective axis.
        Origin changes center of rotation.
        """
        a,b,g,s,c = x0, y0, z0, np.sin, np.cos
        M = np.array([
            [c(b)*c(g), s(a)*s(b)*c(g) - c(a)*s(g), c(a)*s(b)*c(g)+s(a)*s(g)],
            [c(b)*s(g), s(a)*s(b)*s(g) + c(a)*c(g), c(a)*s(b)*s(g)-s(a)*c(g)],
            [-s(b), s(a)*c(b), c(a)*c(b)]
        ])
        if origin is None:
            for v in self.vertices: v.transform(M)
            return self
        else:
            self.translate(-origin)
            for v in self.vertices: v.transform(M)
            self.translate(origin)
            return self