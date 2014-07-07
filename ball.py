""" This module contains the Falldown Ball class and also the BallControlState class.

Ball is the actual 'game ball'.

BallControlState is an object that belongs to the ball; it's used in responding to controller input
"""
__author__ = 'Mass KonFuzion'

from MKFMath.Vector2D import *
from MKFMath.Matrix2D import *
from MKFCollision.primitives import *
from MKFCollision.intersectiontools import *
from physics import *

import pygame

class BallControlState:
    def __init__(self):
        self.leftKeyPressed = False
        self.rightKeyPressed = False

    def setLeftKeyPressedTrue(self):
        self.leftKeyPressed = True

    def setLeftKeyPressedFalse(self):
        self.leftKeyPressed = False

    def setRightKeyPressedTrue(self):
        self.rightKeyPressed = True

    def setRightKeyPressedFalse(self):
        self.rightKeyPressed = False

    def reset(self):
        self.leftKeyPressed = False
        self.rightKeyPressed = False

class Ball:
    """ Ball class
    """
    def __init__(self, rad = 0.0):
        """ Initialize ball
        """
        # TODO:  Once you finish the updates to physics.py, remove the physics-related stuff from this class
        # # Position
        # self.position = Vector2D()
        # # Linear velocity
        # self.velocity = Vector2D()
        # # Acceleration
        # self.acceleration = Vector2D()
        # # Angle
        # self.angle = 0.0
        # # Angular Velocity
        # self.angularVelocity = 0.0
        #
        # # Mass (only for the purpose of doing gravity))
        # self.mass = 10.0
        # self.inverseMass = 1.0 / self.mass
        #
        # # Net force vector (to be used for physics)
        # self.netForce = Vector2D()


        # Max Speed
        self.maxSpeed = 800.0 # By default, the ball should be able to make it all the way across the screen in 1 sec
        # Radius
        # By default, radius should be block height / 2 (so the ball will have the same diameter as block height)
        self.radius = float(rad)

        # Initialize 2 physics states for the ball (current state and previous state)
        # (This is used for 'physics' simulation based on Glenn Fiedler's [gafferongames] approach)
        # For the purpose of this simple game,
        self.currPhysState = EulerState(self.radius)
        self.prevPhysState = EulerState(self.radius)

        # Direction of movement (-1 = left, 0 = stationary, 1 = right)
        self.direction = 0

        # Force vector for gravity
        # Note: For this game, we pre-calculate the force of gravity on the ball, since we're going to re-use it all
        # the time, and given the gravity field in this game, we'll never need to re-calculate it
        self.forceGravity = Vector2D()

        # Ball Control State
        self.controlState = BallControlState()

        # Collision Geometry (basically an axis-aligned bounding box)
        self.collisionGeom = CCollisionSphere2D(0.0, 0.0,self.radius)

        # Balls remaining (a.k.a. "lives" remaining)
        self.ballsRemaining = 3 # Default to 3 'lives'. We can set this via difficulty options

    def initGravity(self, gravity):
        """ Initialize physics properties of this ball.

        This function calculates (well, approximates) the force exerted by gravity on the ball.
        Because the environment in this game has only 1 gravity field (as opposed to a game like
        Angry Birds: Space, which has multiple gravity fields), and because the physics in this
        game is very simple, we may as well calculate and store the force exerted by gravity.

        The parameter, gravity, is a Vector2D() that represents ACCELERATION due to gravity
        i.e. we know that on Earth's surface, the acceleration of just about every object due
        to gravity is 9.8 m/s^2 toward the center of the earth.  That acceleration value is the
        value we plug into this function.
        """

        # F = ma, and we know a_gravity and m_ball; so F_gravity = m_ball * a_gravity
        #Vector2D_scale(self.mass, gravity, self.forceGravity)
        Vector2D_scale(self.currPhysState.mass, gravity, self.forceGravity)


    def setRadius(self, rad):
        """ Set the radius

        This should be used whenever resizing the screen
        """
        self.radius = rad

    def setMaxSpeed(self, maxspd):
        """ Set the ball's max speed

        This should be used when resizing the screen
        """
        self.maxSpeed = maxspd

    def draw(self, screen):
        """ Draw the ball
        """
        color = (0,0,204)

        ref_PhysState = self.currPhysState

        # Draw the circle's "frame" (or rim, or whatever you want to call it)
        pygame.draw.circle(screen, color, (int(ref_PhysState.position[0]), int(ref_PhysState.position[1])), int(self.radius), 0)
        pygame.draw.circle(screen, (int(color[0]*.6), int(color[1]*.6), int(color[2]*.6)), (int(ref_PhysState.position[0]), int(ref_PhysState.position[1])), int(self.radius * .8), 0)

        # TODO:  Fix this - make a way to draw different ball meshes/geometry
        transformationMatrix = Matrix22()
        matRotate = Matrix22()
        matTranslate = Matrix22()

        # ----- Define the ball's geometry -----
        # NOTE:  The ball's geometry should only ever be set one time.  Then, when you draw it, you should transform
        # the geometry, and then render it to the screen
        freckle = Vector2D(0, -self.radius * .6)
        transformedFreckle = Vector2D()

        cross = []
##        cross.append(Vector2D(0, -self.radius * .8))
##        cross.append(Vector2D(0, self.radius * .8))
##        cross.append(Vector2D(-self.radius * .4, 0))
##        cross.append(Vector2D(self.radius * .4, 0))

        cross.append(Vector2D(0, -self.radius * .8))
        cross.append(Vector2D(0, -self.radius * .2))
        cross.append(Vector2D(-self.radius * .1, 0))
        cross.append(Vector2D(self.radius * .1, 0))

        transformedCross = []
        transformedCross.append(Vector2D())
        transformedCross.append(Vector2D())
        transformedCross.append(Vector2D())
        transformedCross.append(Vector2D())


        # ----- Transform geometry -----
        # Rotate first
        Mat22_setRotation(matRotate, ref_PhysState.angle)
        # # Rotate freckle
        # Mat22_multvec(freckle, matRotate, transformedFreckle)
        # Rotate cross
        for i in xrange(0, len(cross)):
            Mat22_multvec(cross[i], matRotate, transformedCross[i])


        # Next, translate
        Mat22_setTranslation(matTranslate, ref_PhysState.position[0], ref_PhysState.position[1])
        # # Translate freckle
        # Mat22_multvec(transformedFreckle, matTranslate, transformedFreckle)
        # Translate cross
        for i in xrange(0, len(cross)):
            Mat22_multvec(transformedCross[i], matTranslate, transformedCross[i])



        # ----- Draw geometry -----
        # Draw cross
        crossCol1 = (204,0,204)
        crossCol2 = (164,0,164)
        pygame.draw.line(screen, crossCol1, (int(transformedCross[0][0]), int(transformedCross[0][1])), (int(transformedCross[1][0]), int(transformedCross[1][1])), 3 )
        pygame.draw.line(screen, crossCol2, (int(transformedCross[2][0]), int(transformedCross[2][1])), (int(transformedCross[3][0]), int(transformedCross[3][1])), 3 )

        # # Draw freckle
        # color2 = (164, 0, 164)
        # pygame.draw.circle(screen, color2, (int(transformedFreckle[0]), int(transformedFreckle[1])), int(self.radius * .3), 0)


        #Draw collision geometry
        #self.collisionGeom.draw(screen)

        # DEBUG CODE
        # TODO:  Remove vector drawing debug code
        #pygame.draw.line(screen, (0,0,255), (int(self.position[0]), int(self.position[1])), (int(self.position[0] + self.velocity[0]), int(self.position[1] + self.velocity[1])))

    def setPosition(self, x, y):
        """ Set position of ball
        """
        #Vector2D_setxy(self.position, x, y)
        Vector2D_setxy(self.currPhysState.position, x, y)

        #self.collisionGeom.setCenter(x, y)
        self.updateCollisionGeom()

    def getPosition(self):
        """ Return the position (the currPhysState position)
        """
        return self.currPhysState.position

    def setVelocity(self, x, y):
        """ Set linear velocity of ball
        """
        #Vector2D_setxy(self.velocity, x, y)
        Vector2D_setxy(self.currPhysState.velocity, x, y)

    def setDirection(self, dir):
        """ Set ball direction

        -1 = left
        0 = not moving
        1 = right

        Any other values are wrong...
        """
        self.direction = dir

    def respondToControllerInput(self):
        """ Set velocity according to user's input

        NOTE:  This function ONLY moves the ball's x/y position.  It does not handle falling due to gravity or
        collisions.
        """

        # NOTE TO SELF:  This is not efficient -- to optimize:  only set the x component
        # if self.direction == -1:
        #     Vector2D_setxy(self.velocity, -self.maxSpeed, self.velocity[1])
        # elif self.direction == 1:
        #     Vector2D_setxy(self.velocity, self.maxSpeed, self.velocity[1])
        # elif self.direction == 0:
        #     Vector2D_setxy(self.velocity, 0, self.velocity[1])

        if self.direction == -1:
            Vector2D_setxy(self.currPhysState.velocity, -self.maxSpeed, self.currPhysState.velocity[1])
        elif self.direction == 1:
            Vector2D_setxy(self.currPhysState.velocity, self.maxSpeed, self.currPhysState.velocity[1])
        elif self.direction == 0:
            Vector2D_setxy(self.currPhysState.velocity, 0, self.currPhysState.velocity[1])


    def accumulateForces(self, dt):
        """ Accumulate forces

        NOTE:  We pass dt in, but we don't necessarily use it in this function (mainly because we are only computing
        instantaneous forces and impulses

        NOTE:  In a more fully-developed physics simulation, we would use gravity and contact generators to "create"
        forces to apply to the ball. The contact generator would be used in a situation where the collision detection
        system has detected a collision. The contact itself would hold a reference/pointer to the 2 contacting objects
        (i.e. the ball and whatever else, in the case of this game, a row), and the force resulting from impact
        """

        # Clear the netForce vector (we're about to calculate it)
        # Vector2D_zero(self.netForce)
        Vector2D_zero(self.currPhysState.netForce)

        # Process gravity
        # NOTE:  This is a hack -- we have already calculated the force due to gravity on this ball, and we are simply
        # adding it to the netForce vector
        # Vector2D_add(self.forceGravity, self.netForce, self.netForce)
        Vector2D_add(self.forceGravity, self.currPhysState.netForce, self.currPhysState.netForce)

        # TODO:  Make this function take in a list of forces (or something) and calculate the other forces acting on
        # the ball.


    def updateCollisionGeom(self):
        """ Update the position of the ball's collision geometry
        """

        # x = self.position[0]
        # y = self.position[1]

        x = self.currPhysState.position[0]
        y = self.currPhysState.position[1]
        self.collisionGeom.setCenter(x, y)


    def moveBall(self, dt):
        """ Move the ball based on gravity, user input, etc.

        NOTE:  The game physics deals only in the y component of velocity (except maybe in the case of collisions of
        the ball with the side of a gap. But even in that scenario, the game will treat that collision as merely a
        constraint on where the ball can travel; not as a collision that generates an impulse on the ball, etc.
        """


        # # Use Euler Integration, because it's easy to compute (even though it may not be totally accurate, based on
        # # true-to-life analog calculations vs computerized digital calculations.  But guess what...  (I don't care :-))
        #
        # # Compute acceleration
        # # Math Note:  Here, we use Fnet = m*a (or, a = Fnet / m).  This formula gives you constant acceleration over
        # # the time interval.  In real life, acceleration may be non-constant over the time integral.. But guess what:
        # # we're simulating real life, and we can cheat, muhahahaha
        # self.acceleration[0] = self.netForce[0] * self.inverseMass
        # self.acceleration[1] = self.netForce[1] * self.inverseMass
        #
        # # Compute velocity
        # # Math Note:  Just kidding, there's no math note here.  But see the position update.
        # self.velocity[0] = self.velocity[0] + (self.acceleration[0] * dt)
        # self.velocity[1] = self.velocity[1] + (self.acceleration[1] * dt)
        #
        # # Compute angular velocity (in radians / sec)
        # # TODO:  Make sure you're doing this angular velocity right
        # # NOTE:  This is one hell of an approximation -- the real math for this is more complex..
        # self.angularVelocity = (self.velocity[0] * dt) / self.radius
        # self.angularVelocity = RAD_TO_DEG(self.angularVelocity)
        # self.angle = self.angle + self.angularVelocity
        #
        #
        # # Update position
        # # Math Note:  The actual formula for position is as follows:
        # # new_pos = curr_pos + (velocity * dt) * (.5 * acceleration * dt * dt)
        # # However, in computer simulations, dt is usually so small that the contribution
        # # by the acceleration component of the equation is negligible.  So we leave it
        # # out of our simulation formula
        # self.position[0] = self.position[0] + (self.velocity[0] * dt)
        # self.position[1] = self.position[1] + (self.velocity[1] * dt)


        integrate(self.currPhysState, dt)
        self.updateCollisionGeom()



