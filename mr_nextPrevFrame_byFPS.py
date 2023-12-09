"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_nextPrevFrame_byFPS.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# DESCRIPTION: 
# Scripts to jump frames by the same fraction amount, no matter the scene's fps.
#
# EXAMPLE USES:
# Originally made when blocking animation, and keying at the same frame increments.
# 
# Example hotkeys to assign to:
#   ALT + SHIFT + X
#   ALT + SHIFT + Z
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------

import importlib

import mr_nextPrevFrame_byFPS
importlib.reload(nextFrame)

mr_nextPrevFrame_byFPS.nextFrame(7)
# OR
mr_nextPrevFrame_byFPS.prevFrame(7)

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-08 - 0002:
# - Made FPS_division definable outside the script.
#
# 2023-04-14 - 0001:
# - First pass.
#
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel


def nextFrame(FPS_division):
    frame_jump = calculate_frame_jump(FPS_division)
    
    currentTime = cmds.currentTime(q=True)
    newTime = currentTime + frame_jump 
    cmds.currentTime(newTime)


# ------------------------------------------------------------------------------ #
def prevFrame(FPS_division):
    frame_jump = calculate_frame_jump(FPS_division)

    currentTime = cmds.currentTime(q=True)
    newTime = currentTime - frame_jump
    cmds.currentTime(newTime)


# ------------------------------------------------------------------------------ #
def calculate_frame_jump(FPS_division):
    FPS = mel.eval('currentTimeUnitToFPS')
    frame_jump = (FPS // FPS_division) - 1

    return frame_jump