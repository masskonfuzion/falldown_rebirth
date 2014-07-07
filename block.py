""" This module contains the FalldownBlock class

This class is the "atom" of the Falldown world.  Blocks make rows.
"""

__author__ = 'Mass KonFuzion'

import pygame
from MKFMath.Vector2D import *

class FalldownBlock:
    """ Block class
    """
    def __init__(self, blockWidth = 50.0, blockHeight = 30.0, blocksPerRow = 16.0):
        """ Initialize the FalldownBlock

        The block's width and height are initialize relative to the screen's dimensions.  By default, the blocks are
        set to a width of 50 pixels, and a height of 30 pixels, based on a screen size of 800 x 600.  This makes 16
        blocks across.
        """
        self.position = Vector2D()
        self.width = blockWidth
        self.height = blockHeight

    def setWidth(self, blockWidth):
        """ Set the width of the blocks
        """
        self.width = blockWidth

    def setHeight(self, blockHeight):
        """ Set the height of the blocks
        """
        self.height = blockHeight

    def setPosition(self, x, y):
        """ Set the position of the FalldownBlock
        """
        Vector2D_setxy(self.position, x, y)

    def draw(self, screen):
        """ Draw the FalldownBlock
        """
        # Create a Pygame Rect object to draw
        # Note:  We're not actually creating a Rect object; we're simply creating a 4-tuple.  Pygame defines a Rect
        # object as a 4-tuple, with the following elements:  x, y, w, h.  Thus, Pygame
        # uses the 4-tuple/Rect object to draw a rectangle at screen position (x,y), with width = w and height = h.
        myRect = (self.position[0], self.position[1], self.width, self.height)

        pygame.draw.rect(screen, (200,0,0), myRect, 2)