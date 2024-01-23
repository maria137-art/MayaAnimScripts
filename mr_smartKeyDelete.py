"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_smartKeyDelete.py
# VERSION: 0005
#
# CREATORS: Maria Robertson
# CREDIT: Aaron Koressel (for original ackDeleteKey.mel script)
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Delete keys depending on the where the mouse cursor is.
# 
#   - If mouse pointer is NOT above Graph Editor:
#       - delete keys of selected objects on the current frame.
#       - If "Sync Timeline Display" is on in the Channel Box, only keys of highlighted attributes will be deleted.
#
#   - If mouse pointer IS above Graph Editor:
#       - If keys on animation curves are selected:
#           - delete only them.
#       - If NO keys are selected:
#           - delete keys on visible anim curves on the current frame.
# 
#
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_smartKeyDelete
importlib.reload(mr_smartKeyDelete)

mr_smartKeyDelete.main()

# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# - Aaron Koressel's ackDeleteKey.mel script: https://aaronkoressel.com/index.php?nav=tools
# 
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-23 - 0005:
#   - Bug fix:
#       - Ensure keys on current frame are deleted for visible animation curves in the Graph Editor, if the mouse cursor is above it.
#
# 2023-12-29 - 0004:
#   - Converting from MEL to Python.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

def main():
    current_frame = cmds.currentTime(query=True)
    current_panel = cmds.getPanel(up=True)
    
    # If Mouse Cursor is not over the Graph Editor, just clear keys on current frame.
    if current_panel != 'graphEditor1':
        mel.eval('timeSliderClearKey')
    
    # If Mouse Cursor is over the Graph Editor.
    else:  
        # Check visible animation curves.
        visible_animation_curves = cmds.animCurveEditor('graphEditor1GraphEd', query=True, curvesShown=True)
        
        if visible_animation_curves:
            selected_keys = cmds.keyframe(query=True, selected=True, keyframeCount=True)

            # If no keys are selected,
            if selected_keys == 0:
                for curve in visible_animation_curves:
                    cmds.cutKey(curve, time=(current_frame, current_frame), clear=True)   

            # If keys are selected,
            else:
                # delete keys on visible anim curves on the current frame
                cmds.cutKey(animation='keys', clear=True)