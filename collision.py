""" Collision Detection for Falldown Rebirth
"""

from MKFMath.Vector2D import *
from MKFMath.MKFMath2D import *
import copy
import pygame

__author__ = 'Mass KonFuzion'

class CollisionGeomAABB:
    """ The CollisionGeomAABB is simply a rectangle.

    Collisions will be handled by creating an axis-aligned bounding box rectangle,

    """
    def __init__(self, rx = 0.0, ry = 0.0):
        """ Initialize CollisionGeom (axis-aligned bounding box)
        """

        # The dimensions of the CollisionGeom
        self.center = Vector2D()
        self.r = [float(rx), float(ry)]

    def setPosition(self, x, y):
        """ Set the position of the CollisionGeom
        """
        Vector2D_setxy(self.center, x, y)

    def setDimensions(self, rx, ry):
        """ Set the Collision dimensions (width, height)
        """

        self.r[0] = float(rx)
        self.r[1] = float(ry)

    def getMinPoint(self):
        """ Get the top-left point of the CollisionGeom (as a Vector2D())
        """
        ret = Vector2D(self.center[0] - self.r[0], self.center[1] - self.r[1])
        return ret

    def getMaxPoint(self):
        """ Get the bottom-right point of the CollisionGeom (as a Vector2D())
        """
        ret = Vector2D(self.center[0] + self.r[0], self.center[1] + self.r[1])
        return ret

    def draw(self, screen):
        """ Draw the CollisionGeom

        This function is used primarily for debugging purposes
        """
        # Create a Pygame Rect object to draw
        # Note:  We're not actually creating a Rect object; we're simply creating a 4-tuple.  Pygame defines a Rect
        # object as a 4-tuple, with the following elements:  x, y, w, h.  Thus, Pygame
        # uses the 4-tuple/Rect object to draw a rectangle at screen position (x,y), with width = w and height = h.
        # corners[0][0] is actually corners[0].x, and corners[0][1] is actually corners[1].y
        # In the Vector2D class, the x and y components are stored in an array.  Item [0]
        # is the x component, and item [1] is the y component
        #myRect = (int(self.corners[0][0]), int(self.corners[0][1]), self.width, self.height)

        topLeft = Vector2D(int(self.center[0] - self.r[0]), int(self.center[1] - self.r[1]))
        myRect = (topLeft[0], topLeft[1], int(self.r[0] * 2), int(self.r[1] * 2))

        pygame.draw.rect(screen, (200, 200, 200), myRect, 1)

class CollisionGeomSphere:
    """ Sphere collision geometry
    """
    def __init__(self, radius = 0.0):
        self.center = Vector2D(0.0, 0.0)
        self.r = float(radius)

    def setPosition(self, x, y):
        Vector2D_setxy(self.center, x, y)

    def setRadius(self, radius):
        self.r = float(radius)

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 200, 200), (int(self.center[0]), int(self.center[1])), int(self.r), 1)

class CollisionGeomCapsule:
    """ Capsule collision geometry

    A "capsule" is a sphere-swept line segment
    """

    def __init__(self):
        self.a = Vector2D()
        self.b = Vector2D()
        self.r = 0.0

    def setPointA(self, x, y):
        Vector2D_setxy(self.a, x, y)

    def setPointB(self, x, y):
        Vector2D_setxy(self.b, x, y)

    def setRadius(self, radius):
        self.r = float(radius)

class CollisionGeomSegment:
    """ Line segment collision geometry
    """

    def __init__(self):
        self.a = Vector2D()
        self.b = Vector2D()

    def setPointA(self, x, y):
        Vector2D_setxy(self.a, x, y)

    def setPointB(self, x, y):
        Vector2D_setxy(self.b, x, y)



#=================================================
# Essential Distance Functions
#=================================================

def sqDist_Point_AABB(p, b):
    """ Return the square of the distance between a point p and AABB b
    (i.e. the closest distance)
    """

    sqDist = 0.0

    b_min = b.getMinPoint()
    b_max = b.getMaxPoint()

    for i in xrange(0, 2):
        v = p[i]

        if v < b_min[i]:
            sqDist = sqDist + ((b_min[i] - v) * (b_min[i] - v))
        if v > b_max[i]:
            sqDist = sqDist + ((v - b_max[i]) * (v - b_max[i]))

    return sqDist


def sqDist_Point_Segment(segA, segB, ptC):
    """ Return the distance from point C to segment AB
    """

    vAB = Vector2D()
    Vector2D_sub(segB, segA, vAB)

    vAC = Vector2D()
    Vector2D_sub(ptC, segA, vAC)

    vBC = Vector2D()
    Vector2D_sub(ptC, segB, vBC)

    e = Vector2D_dot(vAC, vAB)

    # Handle cases where c projects outside ab
    if e <= 0.0:
        return Vector2D_dot(vAC, vAC)

    f = Vector2D_dot(vAB, vAB)

    if e >= f:
        return Vector2D_dot(vBC, vBC)

    # Handle cases where c projects onto ab
    return Vector2D_dot(vAC, vAC) - e * e / f

def closestPt_Point_Segment(segA, segB, p):
    """ Return the point on the line segment [segA, segB] that is closest to p
    """
    #TODO: Change the parameter order -- segA, segB, p
    #TODO: Change parameter type? to Segment?
    # Compute the vector from segA to segB
    vAB = Vector2D()
    Vector2D_sub(segB, segA, vAB)

    # Compute the vector from segA to point p
    vAC = Vector2D()
    Vector2D_sub(p, segA, vAC)

    # project p onto vAB; compute t so that 0 <= t <= 1
    # TODO:  Test for zero
    t = Vector2D_dot(vAC, vAB) / Vector2D_dot(vAB, vAB)

    # If the projection of p falls outside the segment A - B (i.e. if t < 0 or t > 1), then clamp t to the nearest
    # extremity (either 0 or 1)
    if t < 0.0:
        t = 0.0

    if t > 1.0:
        t = 1.0

    # Compute the point on segment [segA, segB] that is closest to p
    ret = Vector2D()
    Vector2D_scale(t, vAB, ret) # First, scale vAB by t
    Vector2D_add(ret, segA, ret) # Add the scaled vector to the point, segA
    return ret



def clamp(n, min, max):
    """ Clamp n to lie within the range (min, max)
    """
    if n < min:
        return min
    if n > max:
        return max
    return n


def closestPt_Segment_Segment(p1, q1, p2, q2):
    """ Computes closest points C1 and C2 of S1(s)=P1+s*(Q1-P1) and
    S2(t)=P2+t*(Q2-P2), returning c1 and c2

    i.e. S1 = segment 1, with points p1 and q1
    S2 = segment 2, with points p2 and q2

    Returns a tuple, (c1, c2)
    """

    d1 = Vector2D() # Direction vector of segment S1
    d2 = Vector2D() # Direction vector of segment S2
    r = Vector2D()

    a = Vector2D_dot(d1, d1) # Squared length of segment S1, always non-negative
    e = Vector2D_dot(d2, d2) # Squared length of segment S2, always non-negative
    f = Vector2D_dot(d2, r)

    # Initialize return values, s and t
    # Force them to be floats
    s = float(0.0)
    t = float(0.0)

    # Initialize return values
    c1 = Vector2D()
    c2 = Vector2D()


    # Check if either or both segments degenerate into points
    if a <= EPSILON_E5 and e <= EPSILON_E5:
        # The vector lengths are both zero, so both segments degenerate into points
        c1 = p1
        c2 = p2
        return c1, c2
    if a <= EPSILON_E5:
        # Second segment degenerates into a point
        s = float(0.0)
        t = f / e
        t = clamp(t, float(0.0), float(1.0)) # t = 0 => s = (b*t - c) / a = -c / a

    else:
        c = Vector2D_dot(d1, r)
        if e <= EPSILON_E5:
            # Second segment degenerates into a point
            t = float(0.0)
            s = clamp (-c / a, float(0.0), float(1.0))
        else:
            # The general non-degenerate case starts here
            b = Vector2D_dot(d1, d2)
            denom = (a * e) - (b * b) # Always non-negative

            # If segments not parallel, compute closest point on L1 to L2 and clamp to segment S1. Else pick
            # arbitrary s (here 0)
            if denom != 0.0:
                s = clamp((b*f) - (c*e) / denom, 0.0, 1.0)
            else:
                s = 0.0

            # Compute point on L2 closest to S1(s), using
            # t = Dot((P1 + D1*s) - P2,D2) / Dot(D2,D2) = (b*s + f) / e
            t = ((b * s) + f) / e

            # If t in [0,1] done. Else clamp t, recompute s for the new value
            # of t using s = Dot((P2 + D2*t) - P1,D1) / Dot(D1,D1)= (t*b - c) / a
            # and clamp s to [0, 1]
            if t < 0.0:
                t = 0.0
                s = clamp(-c/a, 0.0, 1.0)
            elif t > 1.0:
                t = 1.0
                s = clamp((b-c) / a, 0.0, 1.0)

    # Compute c1
    d1_s = Vector2D()
    Vector2D_scale(s, d1, d1_s)
    Vector2D_add(p1, d1_s, c1)

    # Compute c2
    d2_t = Vector2D()
    Vector2D_scale(t, d2, d2_t)
    Vector2D_add(p2, d2_t, c2)

    return c1, c2



def closestPt_Point_AABB(p, b):
    """ Return the closest point on AABB b to point p
    """

    b_min = b.getMinPoint()
    b_max = b.getMaxPoint()

    # For each coordinate axis, if the point coordinate value is
    # outside box, clamp it to the box, else keep it as is

    ret = Vector2D()

    for i in xrange(0, 2):
        ret[i] = p[i]

        if p[i] < b_min[i]:
            ret[i] = b_min[i]

        if p[i] > b_max[i]:
            ret[i] = b_max[i]



def minimumPenetrationDepthAndNormal_Sphere_AABB(s, b):
    """ Return the smallest penetration depth of a sphere into an AABB, and also the normal vector

    NOTE:  This function assumes that the sphere is already colliding with the AABB
    """
    b_min = b.getMinPoint()
    b_max = b.getMaxPoint()

    n = Vector2D() # Surface normal vector to return
    retn = Vector2D()
    d = 0.0

    # Get the vector that points from the center of the box to the center of the sphere
    v = Vector2D()
    Vector2D_sub(s.center, b.center, v)


    # NOTE:  In normal circumstances, we would calculate a surface normal.
    # But since we're working with axis-aligned boxes, we already know the normal, so fuggit :-)

    # Do Top Side First
    # In Pygame, "top side" is (b_min[0], b_min[1]) --> (b_max[0], b_min[1])
    Vector2D_setxy(n, 0, -1)
    d = b.r[1] - (Vector2D_dot(v, n) - s.r)
    Vector2D_setxy(retn, n[0], n[1])
    #print "depth: %f, v: %s" % (d, n)

    # Do left side
    Vector2D_setxy(n, -1, 0)
    tmp = b.r[0] - (Vector2D_dot(v, n) - s.r)
    #print "depth: %f, v: %s" % (tmp, n)

    if tmp < d:
        d = tmp
        Vector2D_setxy(retn, n[0], n[1])

    # Do bottom side
    Vector2D_setxy(n, 0, 1)
    tmp = b.r[1] - (Vector2D_dot(v, n) - s.r)
    #print "depth: %f, v: %s" % (tmp, n)

    if tmp < d:
        d = tmp
        Vector2D_setxy(retn, n[0], n[1])

    # Do right side
    Vector2D_setxy(n, 1, 0)
    tmp = b.r[0] - (Vector2D_dot(v, n) - s.r)
    #print "depth: %f, v: %s" % (tmp, n)

    if tmp < d:
        d = tmp
        Vector2D_setxy(retn, n[0], n[1])

    return d, retn




def isColliding_Circle_Rect(urkel, ralph):
    # TODO:  You may end up deleting this function
    """ Test for collision between a circle (urkel) and a rectangle (ralph)

    This function tests for collisions happening "right now" (i.e. in the current frame) and also collisions that will
    occur in the next frame.

    The circle is called urkel because urkel rhymes with circle.  And also... Steve Urkel from the TV show, Family
    Matters was funny, and I was in a loopy mood when I wrote this function.  The rectangle is called Ralph because, a
    rectangle is a rect.  And Ralph used to Wreck-it.  So after Ralph came through, things would be wrecked.
    Rect <-> wrecked... See what I did there? :-D
    """

    # Step 1 - Test Circle + Radius (i.e., test for collision 'right now')


    # If Step 1 did not produce a collision, then go to:
    # Step 2 - Test Circle + Velocity (i.e. test for prospective collision 'in this simulation step')
    # Get points p1 and p2 to feed into findIntersectionIndex (which is a function in the MKFMath library)
    p1 = urkel.position
    p2 = Vector2D()
    Vector2D_add(p1, urkel.velocity, p2)

    # Step through the sides of the rectangle; set points p3 and p4 for findIntersectionIndex
    # TODO:  Finish this function

#=================================================
# AABB / AABB
#=================================================

def intersect_Segment_Capsule(seg, cap):
    """ Calculate point of intersection of a line segment and capsule (i.e. sphere-swept line)
    """




def isIntersecting_AABB_AABB(cgA, cgB):
    """ Perform broad collision test.  Return True if 2 CollisionGeoms are colliding.
    NOTE:  If the collision test returns True, then go for more refined collision
    testing and response.
    """

    # Perform axis-aligned bounding box test
    # Note--this is a "right-now" test; it does not detect collisions between 2 moving objects that will collide this
    # frame
    if ( abs(cgB.center[0] - cgA.center[0]) > (cgA.r[0] + cgB.r[0]) ):
        return False

    if ( abs(cgB.center[1] - cgA.center[1]) > (cgA.r[1] + cgB.r[1]) ):
        return False
    return True


def willIntersectMoving_AABB_AABB(cgA, velA, cgB, velB):
    """ Test for a collision that may occur in the next frame

    If 2 moving objects' paths intersect during the next frame, find the point of intersection of the 2 paths, and
    then evaluate the collision at that point (as if the 2 objects were actually there).

    returns (0,0) or (tFirst, tLast) if the collision is valid
    returns (None, None) if the collision is invalid

    NOTE:  This function returns 2 variables (this is ported from C++ code that uses variables passed by reference)
    The 2 variables are tFirst (time of first contact) and tLast (time of last contact).
    To test for a valid collision, the programmer will need to make sure that the returned variables are between 0.0
    and the timestep of the simulation.
    """
    #TODO:  Make this a bool -- or otherwise rename it to something sensible
    tContact = [0.0, 0.0]

    # Exit early if cgA and cgB are already overlapping
    if isIntersecting_AABB_AABB(cgA, cgB):
        return tContact

    # Subtract velocity of A from velocity of B.  Effectively treat A as stationary
    v = Vector2D()
    Vector2D_sub(velB, velA, v)

    a_max = cgA.getMaxPoint()
    a_min = cgA.getMinPoint()

    b_max = cgB.getMaxPoint()
    b_min = cgB.getMinPoint()

    for i in xrange(0, 2):
        if v[i] < 0.0:
            if b_max[i] < a_min[i]:
                # There is no time of intersection -- the geoms are non-intersecting and moving apart
                return [None, None]
            if a_max[i] < b_min[i]:
                tContact[0] = max((a_max[i] - b_min[i]) / v[i], tContact[0])
            if b_max[i] > a_min[i]:
                tContact[1] = min((a_min[i] - b_max[i]) / v[i], tContact[1])
        if v[i] > 0.0:
            if b_min[i] > a_max[i]:
                return [None, None]
            if b_max[i] < a_min[i]:
                tContact[0] = max((a_min[i] - b_max[i]) / v[i], tContact[0])
            if a_max[i] > b_min[i]:
                tContact[1] = min((a_max[i] - b_min[i]) / v[i], tContact[1])

        # No overlap is possible if time of first contact occurs after time of last contact
        if tContact[0] > tContact[1]:
            tContact[0] = None
            tContact[1] = None

        return tContact

def getContactPoint (cgA, velA, cgB, velB):

    """ Handle collision

    The collision _response_ should use the actual geometry of the objects involved (as opposed to the _collision_
    geometry).  However, in this case, because the collision geometry of the row is easier to work with than the
    individual blocks themselves, we will use the collision geometry of the row.

    We will still use the actual geometry of the ball (circle)

    NOTE:  This is technically a test for collision of circle vs AABB -- except it's not even REALLY that..
    Fix it, and then move this code into the collision library
    """

    #TODO:  Finish this--for AABBs, we'll need to code a way to figure out which way to push out the penetrating AABBs

    # NOTE:  This code tests the midpoints of the sides of cgB against the sides of cgA
    # This is a janky hack to test a ball (which, technically, should have a "sphere" collision geom
    # It just so happens that I haven't written any sphere/circle collisoin geom code

    # Subtract velA from velB -- treat A as stationary
    v = Vector2D()
    Vector2D_sub(velB, velA, v)


    # Test penetration depth in 4 directions
    # First, test the bottom cgB against the top of cgA
    # TODO:  Change AABB class from height/width to 'radius' -- get rid of the divisions by 2
    ptA = Vector2D(cgB.center[0], cgB.center[1] + (cgB.height /2 ))
    ptB = Vector2D()
    Vector2D_add(ptA, v, ptB)

    # Get the min and max points of the AABB
    a_min = cgA.getMinPoint()
    a_max = cgA.getMaxPoint()

    # Define the points on the top side of the AABB
    topsideSegStart = Vector2D(a_min[0], a_min[1])
    topsideSegEnd = Vector2D(a_max[0], a_min[1])

    t = findIntersectionIndex(ptA, ptB, topsideSegStart, topsideSegEnd)

    contactPoint = None
    if t >= 0.0 and t <= 1.0:
        # Get the contact point
        contactPoint = getPointOnRay(ptB, velB, t)
        # Because the actual contact point is shifted from center, shift the actual return value back to center
        contactPoint[1] = contactPoint[1] - (cgB.height / 2)

    return contactPoint


#=================================================
# Sphere / AABB
#=================================================

def isIntersecting_Sphere_AABB(sphere, box):
    """ Perform broad collision test.  Return True if 2 CollisionGeoms are colliding.
    NOTE:  If the collision test returns True, then go for more refined collision
    testing and response.
    """

    # Compute squared distance between sphere center and AABB
    sqDist = sqDist_Point_AABB(sphere.center, box)

    # Sphere and AABB intersect if the (squared) distance between the sphere center and AABB is less than the (squared)
    # sphere radius
    return (sqDist <= sphere.r * sphere.r)


def intersect_Ray_AABB(p, d, a):
    """ Return the time (or index) t where a ray, starting at point p, in direction d, intersects with AABB a
    """

    tmin = 0.0
    tmax = FLT_MAX

    a_min = a.getMinPoint()
    a_max = a.getMaxPoint()

    for i in xrange(0,2):
        if abs(d[i]) < EPSILON_E5:
            # Ray is parallel to slab. No hit if origin not within slab
            if p[i] < a_min[i] or p[i] > a_max[i]:
                return None
        else:
            # Compute intersection of t value of ray with near and far plane of slab
            ood = 1.0 / d[i]
            t1 = (a_min[i] - p[i]) * ood
            t2 = (a_max[i] - p[i]) * ood
            # Make t1 the intersection with near plane; t2 is intersection of far plane
            if t1 > t2:
                # Swap t1 and t2
                t1, t2 = t2, t1
            # Compute the intersection of slab intersection intervals
            if t1 > tmin:
                tmin = t1

            if t2 > tmax:
                tmax = t2
            # Exit with no collision as soon as slab intersection becomes empty
            if tmin > tmax:
                return None
    # Ray intersects all 3 slabs.  Return the time t of intersection (tmin)
    return tmin

def willIntersectMoving_Sphere_AABB(s, svel, b, bvel):
    """ Intersect a moving sphere with a moving AABB
    The sphere is s
    The direction of movement of the sphere is given by d
    The box is b

    Return time t of intersection (or None if no intersection)
    """
    # TODO:  Make this a bool -- or otherwise rename it to something sensible
    # TODO: Do we test for current intersection? Or do we keep it as 2 separate tests
    # TODO: If so, then do we also get rid of the is-intersecting test from willIntersect_AABB_AABB?

    # Subtract the velocity of the box from the ball (Treat the box as stationary and the ball as moving)
    # i.e. compute the relative velocity of the sphere to the box
    rvel = Vector2D()
    Vector2D_sub(svel, bvel, rvel)

    # Create a copy of b, to extend the boundaries by the radius of r
    e = CollisionGeomAABB()
    e.setPosition(b.center[0], b.center[1])
    e.setDimensions(b.r[0] + s.r, b.r[1] + s.r)

    #NOTE:  Technically, the most accurate way to do this function is to use a sphere-swept rectangle (lozenge)

    # Intersect ray against expanded AABB e. Exit with no intersection if ray misses e; otherwise, get the intersection
    # point p and time t as a result
    tIntersection = intersect_Ray_AABB(s.center, svel, e)

    return tIntersection