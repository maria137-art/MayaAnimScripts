"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_smartNextPrevKey.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Changes the current time to the previous or next key, depending on the where the mouse pointer is hovering.
# 	- If mouse pointer is NOT above Graph Editor:
#		- Will jump to the next/prev key visible in the Timeslider
# 	- If mouse pointer IS above Graph Editor:
#     	- Will jump to the next/prev key visible in the Graph Editor
#
# EXAMPLE USES:
# ---------------------------------------
# - Having more control over which keys to jump between.
#
# INSTRUCTIONS:
# ---------------------------------------
# Assign the commands to a hotkey for quick flipping between keys.
# e.g. 
# 	- SHIFT + Z: previous key
#	- SHIFT + X: next key
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------
import importlib
import mr_smartNextPrevKey
importlib.reload(mr_smartNextPrevKey)

# USE ONE OF THE FOLLOWING:
mr_smartNextPrevKey.main("next")
mr_smartNextPrevKey.main("previous")

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-28 - 0002:
# - Converting mr_smartNextPrevKey.mel to Python.
# - Combining two functions to one.
#
# 2023-04-03 - 0001:
# - First pass.
#
"""

import maya.cmds as cmds

def main(direction=None):
    if direction not in ["next", "previous"]:
        cmds.warning("Please specify if the script should jump to the \"next\" or \"previous\" keyframe.")
        return

    current_panel = cmds.getPanel(up=True)

    # Using Maya's default Next Key hotkey as a base: currentTime -edit (`playbackOptions -q -slp` ? `findKeyframe -timeSlider -which next` : `findKeyframe -which next`)
    is_time_slider_playback = cmds.playbackOptions(query=True, stepLoop=True)

    if current_panel != "graphEditor1":
        if is_time_slider_playback:
            keyframe = cmds.findKeyframe(timeSlider=True, which=direction)
        else:
            keyframe = cmds.findKeyframe(which=direction)
    else:    
        visible_anim_curves = cmds.animCurveEditor('graphEditor1GraphEd', query=True, curvesShown=True)  
        if is_time_slider_playback:
            keyframe = cmds.findKeyframe(visible_anim_curves, which=direction)     
        else:
            keyframe = cmds.findKeyframe(which=direction)

    # Set the current time to the found keyframe.
    cmds.currentTime(keyframe, edit=True)