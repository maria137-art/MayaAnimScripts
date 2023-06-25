"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_reset_undocked_windows.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Reposition all undocked windows to a corner of the screen.
# Can help when they accidentally move off-screen..
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

mr_reset_undocked_windows_topLeft()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-06-25 - 0002
# Converted from MEL to Python.
#
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds


def mr_reset_undocked_windows_topLeft():  
    windows_to_ignore = {
        "CommandWindow", 
        "ConsoleWindow", 
        "MayaWindow", 
        "ColorEditor"
    }    
    undocked_windows = cmds.lsUI(windows=True)
    windows_to_reset = list(set(undocked_windows) - windows_to_ignore)

    for win in windows_to_reset:
        cmds.window(win, e=True, topLeftCorner=[0, 0])    