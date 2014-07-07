__author__ = 'Mass KonFuzion'

from MKFMath.Vector2D import *

class EulerState:
    """ Euler Integration Physics State
    (see Glenn Fiedler's tutorials at gafferongames.com)
    """

    def __init__(self, m = 10.0, ang = 0.0):
        # Position
        self.position = Vector2D()
        # Linear velocity
        self.velocity = Vector2D()
        # Acceleration
        self.acceleration = Vector2D()
        #Angle (in RADIANS)
        self.angle = 0.0
        # Angular velocity (in radians / sec)
        self.angularVelocity = 0.0

        # Mass
        self.mass = m
        self.inverseMass = 1.0 / self.mass

        # Net force vector
        self.netForce = Vector2D()

    # TODO: Also make Integrate() and Copy() (i.e. copy state A into state B
    # TODO:  Also make Interpolate() (from gafferongames)

def integrate(physState, dt):
    # Compute acceleration
    # Math Note:  Here, we use Fnet = m*a (or, a = Fnet / m).  This formula gives you constant acceleration over
    # the time interval.  In real life, acceleration may be non-constant over the time integral.. But guess what:
    # we're only simulating real life, so we can cheat, muhahahaha
    # Implementation Note:  Here we scale the Fnet vector by 1/mass and store the result in the acceleration vector
    physState.acceleration[0] = physState.netForce[0] * physState.inverseMass
    physState.acceleration[1] = physState.netForce[1] * physState.inverseMass


    # Update position
    # Math Note:  The actual formula for position is as follows:
    # new_pos = curr_pos + (velocity * dt) * (.5 * acceleration * dt * dt)
    # However, in computer simulations, dt is usually so small that the contribution
    # by the acceleration component of the equation is negligible.  So we leave it
    # out of our simulation formula
    physState.position[0] = physState.position[0] + (physState.velocity[0] * dt)
    physState.position[1] = physState.position[1] + (physState.velocity[1] * dt)


    # Update velocity
    physState.velocity[0] = physState.velocity[0] + (physState.acceleration[0] * dt)
    physState.velocity[1] = physState.velocity[1] + (physState.acceleration[1] * dt)


    # Calculate arc length rolled along (using madd shortcuts -- the math
    # simplifies because the surface normal is [0, -1])
    # We're saying that the arc length traveled is the same as the distance that
    # the center of the circle moved in this frame (because -- no friction; so
    # assume that the amount rolled is the same as the amount that the center
    # moved)
    arcLength = physState.velocity[0] * dt
    #arcLength = Vector2D_wedge(physState.velocity, Vector2D(0, -1))


    # NOTE: we invert the angular velocity value because the direction of travel (for the ball) is opposite
    # its corresponding increase in angle.  In other words, consider the scenario: the +x is to the right, and the +y
    # direction is up. So, an increase in the angle corresponds to a counter-clockwise rotation. So, with that type of
    # coordinate system, counter-clockwise rotation (from the viewer's perspective, looking at the screen), corresponds
    # to the object rolling to the left along the screen (in the -x direction.) However, for a ball to roll to the left,
    # its x velocity component must be negative.  See the problem?  "Negative" linear movement corresponds to a
    # "positive" change in angle/orientation.  So, we invert our calculation
    # arcLegnth = rad * theta; so theta = arcLength / radius

    physState.angularVelocity = arcLength / physState.mass


    physState.angle = (physState.angle + physState.angularVelocity) % PI2

    # NOTE: The integrated velocity feeds into the NEXT frame

def copyPhysicsState(dest, src):
    """ Copy physics state from src into dest
    """

    # Copy position vector
    Vector2D_copy(dest.position, src.position)
    # Copy velocity vector
    Vector2D_copy(dest.velocity, src.velocity)
    # Copy acceleration vector
    Vector2D_copy(dest.acceleration, src.acceleration)
    # Copy netForce vector
    Vector2D_copy(dest.netForce, src.netForce)

    # Copy angle
    dest.angle = src.angle
    # Copy angular velocity
    dest.angularVelocity = src.angularVelocity
    # Copy mass
    dest.mass = src.mass
    dest.inverseMass = src.inverseMass

def interpolatePhysicsState(psStart, psEnd, t):
    """ Interpolate between physics states A and B
    """
    psRet = EulerState()

    # Interpolate Position
    psRet.position[0] = floatInterpolate(psStart.position[0], psEnd.position[0], t)
    psRet.position[1] = floatInterpolate(psStart.position[1], psEnd.position[1], t)

    # Interpolate Velocity
    psRet.velocity[0] = floatInterpolate(psStart.velocity[0], psEnd.velocity[0], t)
    psRet.velocity[1] = floatInterpolate(psStart.velocity[1], psEnd.velocity[1], t)

    # Interpolate Acceleration
    psRet.acceleration[0] = floatInterpolate(psStart.acceleration[0], psEnd.acceleration[0], t)
    psRet.acceleration[1] = floatInterpolate(psStart.acceleration[1], psEnd.acceleration[1], t)

    # Interpolate Net Force
    psRet.netForce[0] = floatInterpolate(psStart.netForce[0], psEnd.netForce[0], t)
    psRet.netForce[1] = floatInterpolate(psStart.netForce[1], psEnd.netForce[1], t)

    # Interpolate angle
    psRet.angle = floatInterpolate(psStart.angle, psEnd.angle, t)

    # Interpolate angularVelocity
    psRet.angularVelocity = floatInterpolate(psStart.angularVelocity, psEnd.angularVelocity, t)

    # NOTE:  We do NOT interpolate mass -- for our purposes, mass is constant

    return psRet