""" This module contains the GameObject class

This is the object that actually contains the game
"""

__author__ = 'Mass KonFuzion'

from ball import *
from row import *
from statemachine import *


class GameObject:
    """ Class that defines the "game object" -- that holds the game

    This object contains the level (i.e. a list of FalldownRows that are in play)
    """
    def __init__(self):
        """ Initialize the game object
        """
        # Number of rows
        self.numRows = 3
        # List of FalldownRows
        self.rows = []
        # Blocks per row
        self.blocksPerRow = 16

        self.blockWidth = 0.0

        self.blockHeight = 0.0

        # Screen size -- get this from the PygameApplication class (i.e. the PygameApplication class should pass it
        # into this GameObject)
        self.sizeX = 0
        self.sizeY = 0

        self.ball = Ball(15.0)

        # Contact Object
        self._contactObj = None
        self._contactVel= Vector2D() # Note - consider extending the base class

        # State Machine for managing play states (e.g. Intro, MainMenu, InGame,etc)
        self.stateMachine = CStateMachine()

    def initStateMachine(self):
        """ Initialize game state machine
        """

        # Here, we initialize the state machine's states.  In Python, we can use
        # a dictionary, which allows you to add key/value pairs to the
        # dictionary simply by creating them (i.e., no need to formally
        # add/append items to the dictionary).  In C++, we would likely need to
        # create the dictionary (a.k.a. associative array) using the map type
        # (which is part of the std namespace).

        self.stateMachine.states['Intro'] = 0
        self.stateMachine.states['MainMenu'] = 1
        self.stateMachine.states['PlayingGame'] = 2
        self.stateMachine.states['GotCrushed'] = 3
        self.stateMachine.states['GameOver'] = 4
        self.stateMachine.states['SetHighScore'] = 5
        self.stateMachine.states['Exit'] = 6


        # Here, we set the initial state of the state machine
        self.stateMachine.setState('Intro')


        # Some things to note: This is a super-simple state machine. The states
        # and state transitions will be managed by logic in the game (i.e., we
        # are not using more advanced state machines, such as decision trees or
        # event queues or any of that stuff).



    def addNewRow(self, yPos, gapIndex = -1):
        """ Add new row to the level/game board

        This function appends a row to the rows array of the GameObject.  Thus, addNewRow will only ever be called
        at the beginning of the game, or when the player reaches a newlevel (i.e. we need to add another row to the rows
        list).
        """
        newRow = FalldownRow(yPos, self.blocksPerRow, self.blockWidth, self.blockHeight)
        self.rows.append(newRow)

    def resetRow(self, itemNum, yPos, gapIndex = -1):
        """ Re-initialize an existing row
        """
        newRow = FalldownRow(yPos, self.blocksPerRow, self.blockWidth, self.blockHeight)
        self.rows[itemNum] = newRow


    def draw(self, screen):
        """ Draw the game
        """

        # Draw the rows
        for i in xrange(0, self.numRows):
            self.rows[i].draw(screen)

        # Draw the ball
        self.ball.draw(screen)

    def shiftRows(self, yPos):
        """ Shift rows up one index

        i.e. rows[0] is the topmost row on the screen.  When that topmost row reaches the top of the screen, it will
        disappear.  At that point, we shift row[1] to be row[0] and row[2] to be row[1], etc.  Then, we make a new
        bottom-most row.
        """
        # Store a temp row
        tmp = FalldownRow(yPos, self.blocksPerRow, self.blockWidth, self.blockHeight)

        for i in xrange(0, self.numRows - 1):
            # Shift the row references (e.g. rows[0] now points to rows[1])
            self.rows[i] = self.rows[i + 1]

        # Assign the last row of rows[] to point to tmp
        self.rows[self.numRows - 1] = tmp

    def setScreenSize(self, x, y):
        """ Set the screen size

        NOTE:  This function should only be called by the PygameApplication class -- i.e. the PygameApplication class
        passes its screen dimensions into the GameObject, for the GameObject to use in calculating the proper sizes for
        blocks and the ball.
        """
        self.sizeX = x
        self.sizeY = y



    def initLevel(self, ySize = 600.0, numRows = 3, blocksPerRow = 16):
        """ Initialize the level
        """
        self.numRows = numRows

        # Set # of blocks per row
        self.blocksPerRow = blocksPerRow

        # compute block width
        self.blockWidth = float(self.sizeX / self.blocksPerRow)

        # compute block height
        self.blockHeight = float(self.sizeY / 20.0) # Here, we want a default of height (600 / 20)

        #Initially, the top row should be 2/3 of the way up the screen (or, since Pygame increases y values going DOWN
        #the screen, the top row should be 1/3 of the way down the screen)
        rowSpacing = float ((ySize + self.blockHeight )/ self.numRows )

        # Starting yPos = screen height / 2
        #NOTE:  ySize is hard-coded here.  We'll need to make it respond to the
        #window size
        yPos = ySize / 2

        for i in xrange(0, self.numRows):
            #self.addNewRow( int( ( yPos * i ) + yPos - self.blockHeight) )
            self.addNewRow(yPos + (rowSpacing * i))

        # Set the ball's position
        self.ball.setPosition(self.sizeX / 2, self.ball.radius)

        # Initialize gravity on the ball
        # NOTE:  For Pygame, the Y axis increases down the screen.  Therefore, to animate
        # objects "falling", the "down-facing" vector needs to have a positive Y component.
        #gravity = Vector2D(0.0, 9.8) (note: 9.8 is slooowwww)
        # 2000 pixels / sec * sec -- after 1 sec, the velocity will be 2000 pix
        gravity = Vector2D(0.0, 7000.0)

        # Set the ball's gravity force vector
        self.ball.initGravity(gravity)


    def resetLevel(self, ySize = 600.0):
        """ Reset the level
        i.e., Don't ADD new rows; simply re-initialize the existing rows
        """
        # Starting yPos = screen height / 2
        #NOTE:  ySize is hard-coded here.  We'll need to make it respond to the
        #window size
        yPos = ySize / 2

        #Set Row Spacing.  Initially, the top row should be 2/3 of the way up
        #the screen (or, since Pygame increases y values going DOWN the screen,
        #the top row should be 1/3 of the way down the screen)
        rowSpacing = float ((ySize + self.blockHeight )/ self.numRows )

        #For each row in this level, re-initialize the row
        for i in xrange(0, self.numRows):
            self.resetRow(i, yPos + (rowSpacing * i))

        # Set the ball's position
        self.ball.setPosition(self.sizeX / 2, self.ball.radius)

        # Reset the ball's control state
        self.ball.controlState.reset()

        # This reset is necessary because, without it, there is a bug that
        # occurs when you get crushed while holding down a direction key. The
        # bug is that, when you die while holding down a direction key, you
        # will automatically start the next turn still moving in the same
        # direction.


    def moveLevel(self, deltaT):
        """ Move the platforms in the level
        """

        for i in xrange(0, self.numRows):
            # Update the rows themselves (drawing geometry)
            self.rows[i].moveRow(deltaT)

        # Check to see if we need to add a new row (the whole block needs to have cleared the screen)
        if self.rows[0].yPos <= (0 - int(self.blockHeight)):
            # Shift rows -- create a new row at sizeY (give the block the appearance of coming in from  off-the-screen.)
            # Creating the new block at sizeY will create the very top of the block at the very bottom of the screen.
            self.shiftRows(self.sizeY)

    def constrainBallToScreen(self):
        """ Constrain the position of the ball to the screen
        """
        ballRef = self.ball
        ballPos = ballRef.currPhysState.position

        if int(ballRef.currPhysState.position[0] - ballRef.radius) < int(0):
            ballRef.setPosition(int(ballRef.radius), int(ballPos[1]))

        elif int(ballRef.currPhysState.position[0] + ballRef.radius) > int(self.sizeX):
            ballRef.setPosition(int(self.sizeX - ballRef.radius), int(ballPos[1]))

        if int(ballRef.currPhysState.position[1] + ballRef.radius) > int(self.sizeY):
            ballRef.setPosition(ballPos[0], int(self.sizeY - ballRef.radius))
            Vector2D_setxy(ballRef.currPhysState.velocity, 0, 0)

    def collision_GenerateContacts(self):
        """ Detect collisions btwn ball and row; generate a contact
        Note: At any point in time (in this game in particular), this function
        will generate only 1 contact.

        returns None if no collision, or otherwise returns a contact object
        calculated by GetPenetrationDepth_AABB_Sphere (from MKFCollision)

        Note:  As of today (3/12/2014), this game uses static collision
        detection (i.e. the game only considers the current position of the ball
        and blocks; it does not consider previous positions/velocities).
        Therefore, the accuracy of collision detection is impacted GREATLY by
        the simulation timestep (i.e. the smaller the time step, the more
        accurate the collision detection, but the lower the framerate).
        """
        ballRef = self.ball

        contactRef = None

        # Iterate through the rows
        for i in xrange(0, self.numRows):
            # Check collision Geoms (up to 2 per row)
            for j in xrange(0, 2):
                # If there is a CollisionGeom here, then test for collisions
                if self.rows[i].collisionGeoms[j] != None:
                    CGRef = self.rows[i].collisionGeoms[j]
                    if IsColliding_AABB_Sphere(CGRef, ballRef.collisionGeom):

                        # Get minimum penetration depth and the surface normal for the least-penetrated wall
                        contactRef = GetPenetrationDepth_AABB_Sphere(CGRef, ballRef.collisionGeom)

                        # NOTE: this contactVel assignment is redundant. An improvement would be
                        # to assign the velocity only if it is null (or otherwise outdated, say if
                        # it was storing a 'previous' value, and then for some reason, the
                        # velocity was supposed to increase). But for our purposes,
                        # this assignment is fine
                        Vector2D_setxy(self._contactVel, 0, self.rows[i].yVel)
                        self._contactObj = contactRef

        self._contactObj = contactRef

    def collision_ProcessCollisions(self):
        """ Process Collisions
        Note:  The collision response in this application is crazy-simple.  In
        other games, you might need to make more robust collision handling.
        """
        if self._contactObj == None:
            return

        # DEBUG the contact obj
        #print "Contact Obj: %s" % (self._contactObj)


        ballRef = self.ball

        penNorm = self._contactObj.getNormal()
        penDepth = self._contactObj.getMinDepth()

        # =======================
        # Correct ball's velocity
        # =======================
        # If the ball is on the top side of the row, then adjust the velocity to match the
        # row's velocity
        # NOTE:  This is a janky hack -- a 'better' way to set the velocity would be to use
        # an actual physics/collision engine to calculate impulses/forces/acceleration
        # The problem is that the contact/collision detection does ont adjust the
        # velocity of the ball.  The game treats the ball as if it is always
        # "falling".. so we have to manually set the ball's velocity

        if int(penNorm[0]) == 0 and int(penNorm[1]) == -1:
            #We simply assume that the ball has no bounce (in physics terms,
            #the collision between the ball and the row is completely elastic,
            #or that it has no restitution). So, we just negate the effect of
            #gravity on the ball, and explicitly set the y component of the
            #ball's velocity to 0
            Vector2D_sub(ballRef.currPhysState.netForce, ballRef.forceGravity, ballRef.currPhysState.netForce)
            ballRef.setVelocity(ballRef.currPhysState.velocity[0],0)
##
##            # NOTE:  An optimization for this would be:  Instead of subtracting
##            # the effect of gravity at this point, simply set a flag to tell the
##            # game not to process gravity on the ball (in the
##            # ball.accumulateForces) function.  That would cut out unnecessary
##            # calculations.


        # =======================
        # Correct ball's position
        # =======================
        correctionVec = Vector2D()
        # Correct the position of the ball based on penetration information with the row
        Vector2D_scale(penDepth, penNorm, correctionVec)

        currBallPos = ballRef.getPosition()
        ballRef.setPosition(currBallPos[0] + correctionVec[0], currBallPos[1] + correctionVec[1])

        # DEBUG the position correction vector
        #print "Correction Vector: %s" % (correctionVec)

    # # Get an array with the time of initial and final contacts for the 2 collision geometries
    # scaledYVel = Vector2D()
    # Vector2D_scale(self.fixedDeltaTimeS, Vector2D(0.0, self.gameObj.rows[i].yVel), scaledYVel)
    # #
    # scaledBallVel = Vector2D()
    # Vector2D_scale(self.fixedDeltaTimeS, ballRef.velocity, scaledBallVel)
    # tContact = willIntersectMoving_Sphere_AABB(ballRef.collisionGeom, scaledBallVel, CGRef, scaledYVel)
    #
    # # If the time of first contact is greater than 0, then process the collision
    # # We want to position the ball at the point of first contact on the row's collision geometry
    # if tContact != None:
    #     if tContact > 0.0 and tContact < 1.0:
    #         # Jump the ball to the collision point
    #         newBallPos = Vector2D()
    #         Vector2D_scale(tContact, scaledBallVel, newBallPos)
    #         Vector2D_add(ballRef.position, newBallPos, newBallPos)
    #         ballRef.setPosition(newBallPos[0], newBallPos[1])