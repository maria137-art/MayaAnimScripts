"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_smartKeyDelete.py
# VERSION: 0004
#
# CREATORS: Maria Robertson
# CREDIT: Aaron Koressel (for original ackDeleteKey.mel script)
# ---------------------------------------
#
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
# 2023-12-29 - 0004:
#   - Converting from MEL to Python.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

def main():
    selected_keys = cmds.keyframe(query=True, selected=True)
    current_frame = cmds.currentTime(query=True)
    
    # -------------------------------------------------------------------
    # 01. CHECK IF MOUSE CURSOR IS OVER GRAPH EDITOR.
    # -------------------------------------------------------------------  
    current_panel = cmds.getPanel(up=True)
    
    if current_panel != 'graphEditor1':
        mel.eval('timeSliderClearKey')
    
    else:  
        # Check visible curves in the Graph Editor.
        connection = cmds.editor('graphEditor1GraphEd', query=True, mainListConnection=True)
        visible_curves = mel.eval('expandSelectionConnectionAsArray "{}"'.format(connection))
        
        if visible_curves:
            # -------------------------------------------------------------------
            # 01. CHECK IF KEYS ARE SELECTED.
            # -------------------------------------------------------------------  
            key_count = cmds.keyframe(query=True, selected=True, keyframeCount=True)

            if key_count == 0:
                # for every visible curve,
                for curve in visible_curves:
                    # remove its key on the current frame.
                    cmds.cutKey(curve, time=(current_frame, current_frame), clear=True)   

            else:
                cmds.cutKey(animation='keys', clear=True)