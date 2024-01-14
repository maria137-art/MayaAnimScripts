"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_toggleDisplay.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A script to toggle the display of different objects in the current modelPanel.
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------

import importlib
import mr_toggleDisplay
importlib.reload(mr_toggleDisplay)

# USE ANY OF THE FOLLOWING:
mr_toggleDisplay.nurbsCurves()
mr_toggleDisplay.locators()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-12-01 - 0001:
#   - Added two possible options to pivot with.
# ------------------------------------------------------------------------------ //
"""

import maya.cmds as cmds

########################################################################
#                                                                      #
#                                PRESETS                               #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def nurbsCurves():
    main("nurbsCurves")

# ------------------------------------------------------------------------------ #
def locators():
    main("locators")
 
 ########################################################################
#                                                                      #
#                                MAIN FUNCTION                         #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def main(option):
    my_panel = cmds.getPanel(withFocus=True)
    
    if cmds.getPanel(typeOf=my_panel) == "modelPanel":
        current_state = cmds.modelEditor(my_panel, query=True, **{option: True})
        cmds.modelEditor(my_panel, edit=True, **{option: not current_state})
