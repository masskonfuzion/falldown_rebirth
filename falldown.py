""" Falldown Rebirth
"""
__author__ = 'Mass KonFuzion'

from application import *

def main():
    """ Main function.  Here is where all the magic happens.
    """
    # Create a new Falldown Game Object
    app = PygameApplication()

    # The game object has a Pygame Application Object in it.  Initialize it
    app.initializeGraphics(800, 600)

    # Set game object's dimensions
    app.gameObj.setScreenSize(app.sizeX, app.sizeY)

    # Initialize the game object
    app.gameObj.initLevel(app.sizeY, 6, 10)
    app.gameObj.initStateMachine()

    # Start the game loop.
    app.doGameLoop()

if __name__ == '__main__':
    main()
