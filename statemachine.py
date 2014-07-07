#-------------------------------------------------------------------------------
# Name:        StateMachine
# Purpose: Provide code for game state management
#
# Author:      lherard
#
# Created:     30/04/2014
# Copyright:   (c) lherard 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


### NOTE:  There should be a CEvent class (or otherwise, an Event type).  In C++,
### we would simply typedef to make "Events" the same as Integers. That would
### allow us to define Events that the program can raise to the State Machine, for
### the State Machine to process (e.g., transition Events to change from state to
### state).
##
##class CStateTransition:
##    """ State Transition Object
##    """
##    def __init__(self, id = -1, myName = "", nxtState = None):
##        self.eventID = id # eventID should be an integer, 0 or higher; -1 means uninitialized
##        self.transName = myName
##        self.nextState = nxtState # Reference to the next state
##
##
##    def __str__(self):
##        return "ID: %s, Name: %s,
##
##
##class CState:
##    """ State: The individual states used in the state machine.
##    Each CState object contains one or more CStateTransition, which contains the
##    information necessary to move from one state to the next.
##    """
##    def __init__(self, id = -1, myName = ""):
##        self.stateID = id # stateID should be an integer, 0 or higher; -1 means uninitialized
##        self.stateName = myName # The state's name (I'm undecided on whether this class REALLY needs this member)
##        self.transitions = [] # transitions is an array of StateTransitionObjects


class CStateMachine:
    """ State Machine: Container of states, with their state transitions, as
    well as the controls to move from state to state.
    """
    def __init__(self):
        """ Initialize the states dictionary

        Note:  Currently, this class is a simple placeholder.  It's so simple,
        it almost doesn't deserve its own module.  More mature versions should
        have, e.g., member functions that add/remove states, transition from
        state to state, and provide error checking.

        When using this state machine, make sure that the state names (keys) are
        strings, and the values are integers.
        """
        self.states = {} # dictionary: Key = statename; Value = An INTEGER!
        self.currentState = -1 # -1 means uninitialized

    def setState(self, stateName):
        """ Set self.currentState to the value of the state indexed by
        stateName.

        For example, call function as setState('MainMenu')

        Note:  Currently, this function does not provide error checking.
        Also, the design of this state machine requires the programmer to
        know the state names in the dictionary.
        """
        self.currentState = self.states[stateName]
