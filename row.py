""" This module contains the FalldownRow Class

This class manages rows.  Rows contain blocks.  Check it.
"""

__author__ = 'Mass KonFuzion'

import random
from block import *
from MKFCollision.primitives import *
from MKFCollision.intersectiontools import *

class FalldownRow:
    """ Row class -- holds a row of blocks
    """
    def __init__(self, yPos, numBlocks = 16, blockWidth = 50.0, blockHeight = 30.0, yVel = -200):
        """ Initialize FalldownRow

        By default, the number of blocks per row is 16.
        """
        # Number of blocks in this row
        self.numBlocks = numBlocks
        # List of blocks
        self.blocks = []
        # Block width
        self.blockWidth = blockWidth
        # Block height
        self.blockHeight = blockHeight
        # Set the gap index (-1 means uninitialized)
        self.gap = -1
        # Set y position of this row on the screen
        self.yPos = yPos
        # Set y-velocity of the row(in pixels / second)
        # NOTE:  At xyz difficulty level that I haven't decided yet, one row should clear the screen in 3 seconds.
        # By default, on a 800x600 screen, that's 600 pixels in 3 seconds; 200px/sec
        self.yVel = yVel

        # Collision geometry array.  This will have at least 1, and at most 2
        # items in it
        #    Each FalldownRow will have up to 2 CollisionGeoms.  A row will have only 1 CollisionGeom if the gap is
        # either at the very beginning or end of the row.  It will have 2 CollisionGeoms if the gap is at any other
        # position in the row (i.e. there is at least one block at either edge of the screen.
        # We populate this list now, because we know that we will only ever have
        # 1 or 2 collisionGeoms.
        self.collisionGeoms = [None, None]


        # Create a row
        self.createRow(self.yPos)

    def __str__(self):
        """ Return a string representation of the row
        """
        ret = ""
        # Test whether the blocks list has anything in it
        if len(self.blocks) > 0:
            # If it has blocks, then print out the row
            for i in xrange(0,len(self.blocks)):
                if self.blocks[i] != None:
                    ret = ret + "-"
                else:
                    ret = ret + " "
        else:
            ret = "(Uninitialized)"
        ret = ret + " " + str(self.gap)

        return ret

    def __repr__(self):
        return self.__str__()

    def createCollisionGeoms(self):
        """ Create the collisionGeoms for the row

        NOTE:  This function is called in createRow().  The programmer will not
        need to call this function explicitly (in C++, this would be a private
        function).
        """
        # There will be 1 collisionGeom if gapIndex == 0 or gapIndex == self.numBlocks - 1
        # Otherwise, there will be 2 collisionGeoms

        width = 0.0
        height = self.blockHeight # Height is always the same, no matter what the CollisionGeom widths are

        # Case 1:  gapIndex is at the left-most edge of screen/row
        if (self.gap == 0):
            width = (self.numBlocks - 1) * self.blockWidth # (width + 2 == janky hack to correct for faulty collision detection

            # Set the position to match the position of blocks[1] (i.e. the 2nd
            # block position, which is actually the first block when gap == 0)
            cgPos = self.blocks[1].position #Vector2D reference/pointer

            self.collisionGeoms[0] = CCollisionAABB2D(int(cgPos[0] + (width * .5)), int(cgPos[1] + (height *.5)), int(width *.5), int(height * .5))

            # For good measure, make sure the 2nd collisionGeom is None
            # TODO:  Verify whether or not this is necessary -- we only need to
            # explicitly set collisionGeoms[1] to None if FalldownRows are
            # recycled by the Game Object
            self.collisionGeoms[1] = None

        elif (self.gap == self.numBlocks - 1):
            width = (self.numBlocks - 1) * self.blockWidth

            # Set the position to match the position of blocks[0] (i.e. the 1st
            # block position)
            cgPos = self.blocks[0].position

            self.collisionGeoms[0] = CCollisionAABB2D(int(cgPos[0] + (width * .5)), int(cgPos[1] + (height * .5)), int(width * .5), int(height * .5))
            self.collisionGeoms[1] = None

        else: # self.gap > 0 and self.gap < self.numBlocks - 1
            # Do the first collision geom
            # Width = blockWidth * gap
            # Position = blocks[0].position
            width = self.blockWidth * self.gap
            cgPos = self.blocks[0].position

            self.collisionGeoms[0] = CCollisionAABB2D(int(cgPos[0] + (width * .5)), int(cgPos[1] + (height * .5)), int(width * .5), int(height * .5))

            # Do the second collision geom
            # Width = blockWidth * (numBlocks - gap + 1)
            # Position = blocks[gap + 1].position
            width = self.blockWidth * (self.numBlocks - self.gap + 1)
            cgPos = self.blocks[self.gap + 1].position

            self.collisionGeoms[1] = CCollisionAABB2D(int(cgPos[0] + (width * .5)), int(cgPos[1] + (height * .5)), int(width * .5), int(height * .5))


    def createRow(self, yPos, gapIndex = -1):
        """ Create a new row of blocks

        gapIndex is an integer.
            If gapIndex == -1, then the function will randomly assign the gap location
            If gapIndex is any other number, the function will assign the gap to that number
        """

        # Assign gap index
        self.gap = gapIndex
        # If gapIndex is -1, then randomly assign gap
        if self.gap == -1:
            # Generate a random gap index
            self.gap = random.randint(0, self.numBlocks - 1)
            # NOTE:  randint(a, b) generates a number between (but also possibly including) a and b.  Here, we set the
            # range as self.numBlocks-1, because self.numBlocks - 1 is the last legal index where the gap could be.
            # i.e. we can't set the gap index to self.numBlocks, because that is out of bounds.. doing so would create
            # a row with no gap in it.

        # Create the row
        for i in xrange(0, self.numBlocks):
            if i != self.gap:
                # Create a new block
                newBlock = FalldownBlock(self.blockWidth, self.blockHeight)
                # Set the block's position
                newBlock.setPosition(i * newBlock.width, yPos)
                # Add it to the row
                # TODO determine:  Should we always append? (This assumes that the row is new.. should we program this to clear the list and start fresh every time?
                self.blocks.append(newBlock)
            else:
                # Append a "null pointer" at this spot in the list
                # Note for C++ -- if you were to write this game in C/C++, the blocks list would be a list/vector of
                # pointers to individual blocks.
                self.blocks.append(None)

        # Create the collisionGeoms
        self.createCollisionGeoms()

##    def resetRow(self, yPos, gapIndex = -1):
##        """ Re-initialize an already-existing row of blocks
##        Here, we assume that all of the key properties of the row have already
##        been created (e.g. # of blocks per row, block height,
##        """
##        # Assign gap index
##        self.gap = gapIndex
##        # If gapIndex is -1, then randomly assign gap
##        if self.gap == -1:
##            # Generate a random gap index
##            self.gap = random.randint(0, self.numBlocks - 1)
##            # NOTE:  randint(a, b) generates a number between (but also possibly including) a and b.  Here, we set the
##            # range as self.numBlocks-1, because self.numBlocks - 1 is the last legal index where the gap could be.
##            # i.e. we can't set the gap index to self.numBlocks, because that is out of bounds.. doing so would create
##            # a row with no gap in it.
##
##        for i in xrange(0, self.numBlocks):
##            if i != self.gap:
##                # Create a new block
##                self.blocks[i] = FalldownBlock(self.blockWidth, self.blockHeight)
##                # Set the block's position
##                self.blocks[i].setPosition(i * self.blocks[i].width, yPos)
##
##                #NOTE: Here, instead of appending a new block, we are assigning
##                #the block to an existing item in the array
##                #NOTE 2: I think this function is redundant. The resetRow
##                #function is redundant. In initLevel, we can do the same thing
##                #that we're doing here (i.e., initLevel does not need to append
##                #blocks to a row. It can create the space needed beforehand, and
##                #then allocate blocks.
##                #
##                #The one advantage of doing it this way is for dynamic
##                #allocation and deletion of blocks?  I think?  Revisit this
##
##            else:
##                # Append a "null pointer" at this spot in the list
##                # Note for C++ -- if you were to write this game in C/C++, the blocks list would be a list/vector of
##                # pointers to individual blocks.
##                self.blocks[i] = None
##
##        # Create the collisionGeoms
##        self.createCollisionGeoms()

    def draw(self, screen):
        """ Draw the row
        """
        for i in xrange(0, self.numBlocks):
            if self.blocks[i] != None:
                self.blocks[i].draw(screen)

        # Draw collision geometry
##        for i in xrange(0, len(self.collisionGeoms)):
##             if self.collisionGeoms[i] != None:
##                 self.collisionGeoms[i].draw(screen)

    def moveRow(self, deltaT):
        """ Move the row up the screen
        """

        # Calculate the new yPos for this row
        self.yPos = self.yPos + int(self.yVel * deltaT)

        # Update this row's collision geometry
        for j in xrange(0, len(self.collisionGeoms)):
            if self.collisionGeoms[j] != None:
                # Assign a reference to the CollisionGeom's center
                posRef = self.collisionGeoms[j].getCenter()
                self.collisionGeoms[j].setCenter(posRef[0], self.yPos + (self.blockHeight * .5))


        # Step through the blocks in this row
        for i in xrange(0, self.numBlocks):
            blk = self.blocks[i]
            # If the block exists, then move it (if not, ignore it)
            if blk != None:
                # Update the Y position of each block in the row
                # NOTE:  Technically speaking, we should calculate new x and y positions, but because Falldown only cares
                # about the vertical movement of rows, we only calculate y
                # NOTE ^ 2:  Hmmm, maybe we could add side-to-side movement of rows as a feature of the game?
                blk.setPosition(blk.position[0], self.yPos)

    def setBlockWidth(self, sizeX):
        """ Compute the block width, given a width

        The purpose of this function is to calculate the width of blocks, using the screen width (as passed in by the
        PygameApplication object).

        This function should be called when initializing the game, and also after any window resize events
        """
        self.blockWidth = int(sizeX / self.numBlocks)