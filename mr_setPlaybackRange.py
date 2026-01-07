"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_setPlaybackRange.py
# VERSION: 0001

# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Set the start and end frame of the playback range.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_setPlaybackRange
importlib.reload(mr_setPlaybackRange)

mr_setPlaybackRange.main('start')

OR

mr_setPlaybackRange.main('end')


# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def main(to='start'):
    current_frame = cmds.currentTime(query=True)

    if to == 'start':
        cmds.playbackOptions(min=current_frame)

    elif to == 'end':
        cmds.playbackOptions(max=current_frame)

    else:
        raise ValueError("Argument 'to' must be either 'start' or 'end'.")