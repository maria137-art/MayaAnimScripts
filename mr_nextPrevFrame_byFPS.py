import maya.cmds as cmds
import maya.mel as mel

"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_nextPrevFrame_byFPS.py
# VERSION: 0001
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
importlib.reload(mr_nextPrevFrame_byFPS)

mr_nextPrevFrame_byFPS.mr_nextFrame_oneSixth_FPS()

# ------------------------------------------------------------------------------ #
"""

divide_FPS_by = 6


def mr_nextFrame_oneSixth_FPS():
    
    FPS = mel.eval('currentTimeUnitToFPS')
    frame_jump = (FPS / divide_FPS_by) - 1
    
    currentTime = cmds.currentTime(q=True)
    newTime = currentTime + frame_jump
    
    cmds.currentTime(newTime)


def mr_prevFrame_oneSixth_FPS():
    
    FPS = mel.eval('currentTimeUnitToFPS')
    frame_jump = (FPS / divide_FPS_by) - 1
    
    currentTime = cmds.currentTime(q=True)
    newTime = currentTime - frame_jump
    
    cmds.currentTime(newTime)