""" This module contains the PygameApplication class.
"""

# Import pygame and sys modules
import pygame
import time
#Note:  In Windows, the high-res timer is time.clock() -- the precision is
#in microseconds (roughly).  In UNIX, the high-res timer is time.time().
#Remember that for porting code
#TODO:  Implement a Timer class capable of hi-res cross-platform timing

# TODO: Update ALL of this code so that the Application Class only overloads
# function calls, e.g. to draw in OpenGL vs SDL/Pygame, or to call the correct
# system time measurement function, depending on Windows/Linux/Mac.


import sys

# Import the GameObject class
from gameobj import *

# This is some ish I downloaded
#import vidcap

class PygameApplication:
    def __init__(self):
        # Placeholder for screen surface
        self.gameWindow = None
        self.font = None
        self.sizeX = 0
        self.sizeY = 0

        self.gameObj = GameObject()

        # Timer stuff
        self.currentTimeS = 0.0
        self.previousTimeS = 0.0
        self.deltaTimeS = 0.0
        self.accumulatorS = 0.0
        #self.fixedDeltaTimeS = .016 # Corresponds to 62.5 FPS
        self.fixedDeltaTimeS = .01 # Corresponds to 100 FPS
        #self.fixedDeltaTimeS = 0.0125 # Corresponds to 80 FPS
        #self.fixedDeltaTimeS = 0.01667 # Corresponds to 60 FPS

        # Should we record video, using vidcap?
        #self._recordVideo = False

    def initializeGraphics(self, sizeX, sizeY):
        """ Initialize graphics system using Pygame
        """
        # Call Pygame initialization function
        pygame.init()

        # Set the dimensions of the application
        self.sizeX = sizeX
        self.sizeY = sizeY

        # Set the dimensions of my GameObject's playing area
        self.gameObj.setScreenSize(self.sizeX, self.sizeY)

        # Create window surface
        self.gameWindow = pygame.display.set_mode((self.sizeX, self.sizeY))
        pygame.display.set_caption("Falldown Rebirth")

        #Get a font object, for writing to the screen (using the
        #system-default font
        self.font = pygame.font.SysFont(None, 16)

    def draw(self):
        """ Draw the game
        """
        # Clear screen
        self.gameWindow.fill( (0,0,0) )

        # Draw the game
        self.gameObj.draw(self.gameWindow)

        # Update the screen
        pygame.display.update()

##        # If we're recording video
##        if self._recordVideo:
##            vidcap.cap()

    def doControllerInput(self, ballRef):
        """ Handle controller input

        ballRef is a reference to the ball
        """

        # Process keyboard inputs (mutually exclusively)
        # Process what to do if left key is pressed
        if ballRef.controlState.leftKeyPressed:
            ballRef.setDirection(-1)
        elif ballRef.controlState.rightKeyPressed:
            ballRef.setDirection(1)
        elif ballRef.controlState.leftKeyPressed == False and ballRef.controlState.rightKeyPressed == False:
            ballRef.setDirection(0)

        # Respond to user input
        ballRef.respondToControllerInput()


    def doPlayingState(self):
        """ Do the stuff that's supposed to happen in the 'Playing' game state
        """
        # Set previous time
        self.previousTimeS = time.clock()

        # Set time accumulator
        self.accumulatorS = 0.0

        ballRef = self.gameObj.ball

        # Stay in this function/state for as long as the state doesn't change
        # (that sounds circular.. :-D)
        while self.gameObj.stateMachine.currentState == self.gameObj.stateMachine.states['PlayingGame']:

            # Variable used for debugging -- if true, pauses the whole frame
            DEBUG_RUN_FRAME = True

            # Check for Pygame events (e.g. process input)
            for event in pygame.event.get():
                # Quit
                if event.type == pygame.QUIT:
                    self.gameObj.stateMachine.setState('Exit')

                elif event.type == pygame.KEYDOWN:
                    # Left arrow key
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_j):
                        ballRef.controlState.setLeftKeyPressedTrue()
                    # Right arrow key
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                        ballRef.controlState.setRightKeyPressedTrue()
                elif event.type == pygame.KEYUP:
                    #DEBUGGING stuff
                    if event.key == pygame.K_RETURN:
                        DEBUG_RUN_FRAME = True

                    if (event.key == pygame.K_LEFT or event.key == pygame.K_j):
                        ballRef.controlState.setLeftKeyPressedFalse()
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                        ballRef.controlState.setRightKeyPressedFalse()

            # NOTE To return the game to normal (without pausing at each frame),
            # remove all lines that contain DEBUG_RUN_FRAME -- un-indent the
            # portions that follow this if DEBUG_RUN_FRAME statement
            if DEBUG_RUN_FRAME:
                # Handle controller
                self.doControllerInput(ballRef)


                # Get hi-res time from the system
                self.currentTimeS = time.clock()

                # Calculate delta time
                self.deltaTimeS = self.currentTimeS - self.previousTimeS

                # Store previous time
                self.previousTimeS = self.currentTimeS



                # Update physics
                # --------------
                # If the frame takes longer than .25s to draw and process input and all that, then pretend it took .25 sec
                # (4 FPS)
                if self.deltaTimeS > .25:
                    self.deltaTimeS = .25

    ##                # USE THESE LINES FOR DEBUGGING FRAME-BY-FRAME
    ##                if self.deltaTimeS > self.fixedDeltaTimeS:
    ##                    self.deltaTimeS = self.fixedDeltaTimeS

                # Add to the accumulator
                self.accumulatorS = self.accumulatorS + self.deltaTimeS

                # If the amount of time collected in the accumulator is greater than the target fixedDeltaTime value, then
                # crunch the numbers.
                # NOTE:  The purpose of this timing code is to ensure that we can keep a fixed dt for our level/physics
                # simulation.  In detail, deltaTimeS tells us how fast the game is actually running on the system.
                # fixedDeltaTimeS tells us how fast we want our simulation steps to be (for physics and what not).  So, if
                # deltaTimeS < fixedDeltaTimeS, then that means our game is running faster than the target speed.  In that
                # case, we don't process physics/level updates; instead, we add deltaTimeS to the accumulatorS variable.
                # Once the accumulatorS variable exceeds the target fixed time, only then do we process physics/level
                # updates.
                # NOTE:  We need to add 'state' tracking, for interpolation of states (refer to my Verlet Sim and also to
                # the gafferongames tutorials.)

                while self.accumulatorS >= self.fixedDeltaTimeS:
                    # Copy current physics state into previous state
                    copyPhysicsState(ballRef.prevPhysState, ballRef.currPhysState)

                    # Update the ball
                    # NOTE:  This function has the code that processes the effect of
                    # forces (including gravity) on the ball
                    # DOUBLE NOTE: A better way to handle the level updates is
                    # to make all objects derive from a base object, and
                    # "integrate" or update all objects.
                    ballRef.moveBall(self.fixedDeltaTimeS)

                    # After moving the ball, check to see if we've been crushed
                    # We're crushed if the center of the ball reaches the top of
                    #the screen
                    if int(ballRef.getPosition()[1]) < 0:
                        # If we've gotten crushed, then we need to change the game
                        # state to process the crushing.
                        self.gameObj.stateMachine.setState('GotCrushed')


                    # Update the level
                    self.gameObj.moveLevel(self.fixedDeltaTimeS)

                    # Constrain the ball to the screen
                    self.gameObj.constrainBallToScreen()

                    # Accumulate forces acting on the ball
                    ballRef.accumulateForces(self.fixedDeltaTimeS)

                    # Detect Collisions & Generate a contact
                    self.gameObj.collision_GenerateContacts()

                    # Process collisions
                    # NOTE:  This function has the code that removes the effect of
                    # gravity on the ball
                    self.gameObj.collision_ProcessCollisions()


                    # DEBUG - print accumulator
                    #print "Accumulator: %f" % (self.accumulatorS)
                    self.accumulatorS -= self.fixedDeltaTimeS


    ##            # k = left-over time / fixed dt
    ##            k = self.accumulatorS / self.fixedDeltaTimeS
    ##
    ##            # "rewind" back into the last truly known physics state
    ##            interpolatePhysicsState(ballRef.prevPhysState, ballRef.currPhysState, k)
    ##
    ##            # Update Collision / Contact info after interpolation
    ##            self.gameObj.collision_GenerateContacts()

                # Draw the application
                self.draw()


    def doIntroState(self):
        """ Do the stuff that's supposed to happen in the Introduction
        e.g. intro video/animation, or whatever
        """

        # Temporary placeholder for the real introduction
        strTxt = "MassKonFuzion Presents: Falldown Rebirth"
        strTxt2 = "Press Any Key to Continue"

        # Initialize the text color
        textColor = (255, 255, 255)

        #text is a surface -- pygame renders a string to the surface I've
        #called "text"
        text = self.font.render(strTxt, True, textColor)
        text2 = self.font.render(strTxt2, True, textColor)

        # Initialize the Text Position
        textPos = (0, 0)
        text2Pos = (0, 30)


        # Wait here until the user presses a key
        while self.gameObj.stateMachine.currentState == self.gameObj.stateMachine.states['Intro']:
            # Clear screen
            self.gameWindow.fill ( (0,0,0) )

            #Blit the "text surface" onto the "screen" surface
            self.gameWindow.blit(text, textPos)
            self.gameWindow.blit(text2, text2Pos)

            pygame.display.update()

            # Process Pygame events
            for event in pygame.event.get():
                # If the user presses any key, then change the state
                if event.type == pygame.KEYDOWN:
                    self.gameObj.stateMachine.setState('MainMenu')
                elif event.type == pygame.QUIT:
                    self.gameObj.stateMachine.setState('Exit')



    def doMainMenuState(self):
        """ Do main menu
        """
        # Temporary placeholder for the real introduction
        strTxt = "Pretend this is a main menu..."

        # Initialize the text color
        textColor = (255, 255, 255)

        #text is a surface -- pygame renders a string to the surface I've
        #called "text"
        text = self.font.render(strTxt, True, textColor)

        # Initialize the Text Position
        textPos = (0, 0)


        # Wait here until the user presses a key
        while self.gameObj.stateMachine.currentState == self.gameObj.stateMachine.states['MainMenu']:
            # Clear screen
            self.gameWindow.fill ( (0,0,0) )

            #Blit the "text surface" onto the "screen" surface
            self.gameWindow.blit(text, textPos)

            pygame.display.update()

            # Process Pygame events
            for event in pygame.event.get():
                # If the user presses any key, then change the state
                if event.type == pygame.KEYDOWN:
                    self.gameObj.stateMachine.setState('PlayingGame')
                elif event.type == pygame.QUIT:
                    self.gameObj.stateMachine.setState('Exit')

    def doGameOver(self):
        pass


    def doGotCrushedState(self):
        # Temporary placeholder for the real introduction
        strTxt = "Oh snap, you got crushed!  Press a key to try again."

        # Initialize the text color
        textColor = (255, 255, 255)

        #text is a surface -- pygame renders a string to the surface I've
        #called "text"
        text = self.font.render(strTxt, True, textColor)

        # Initialize the Text Position
        textPos = (0, 0)


        # Wait here until the user presses a key
        while self.gameObj.stateMachine.currentState == self.gameObj.stateMachine.states['GotCrushed']:
            # Clear screen
            self.gameWindow.fill ( (0,0,0) )

            #Blit the "text surface" onto the "screen" surface
            self.gameWindow.blit(text, textPos)

            pygame.display.update()

            # Process Pygame events
            for event in pygame.event.get():
                # If the user presses any key, then change the state
                if event.type == pygame.KEYDOWN:
                    #TODO: Update this resetLevel() call to take into account
                    #difficulty level, user game progress, etc.
                    self.gameObj.resetLevel()
                    self.gameObj.stateMachine.setState('PlayingGame')
                elif event.type == pygame.QUIT:
                    self.gameObj.stateMachine.setState('Exit')

    def doGameLoop(self):
        """ Run the game loop

        In this large function, we check the game state and act accordingly
        """

        # Run the game loop until the user exits
        while self.gameObj.stateMachine.currentState != self.gameObj.stateMachine.states['Exit']:

            # Handle the various states of being for the game
            if self.gameObj.stateMachine.currentState == self.gameObj.stateMachine.states['Intro']:
                self.doIntroState()
            elif self.gameObj.stateMachine.currentState == self.gameObj.stateMachine.states['MainMenu']:
                self.doMainMenuState()
            elif self.gameObj.stateMachine.currentState == self.gameObj.stateMachine.states['PlayingGame']:
                self.doPlayingState()
            elif self.gameObj.stateMachine.currentState == self.gameObj.stateMachine.states['GotCrushed']:
                self.doGotCrushedState()


        # If we reached this code, then the user clicked the X on the window (to
        # exit the program)
        pygame.quit()
        sys.exit()