"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_swapObjectsInWorldspace.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Swap the position and rotation of two objects in worldspace.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_swapObjectsInWorldspace
importlib.reload(mr_swapObjectsInWorldspace)

mr_swapObjectsInWorldspace.main(translate=True, rotate=True)

# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def main(translate=True, rotate=True):
    selection = cmds.ls(selection=True)
    
    if len(selection) != 2:
        cmds.warning("Please select exactly two objects.")
        return None

    a, b = selection
    has_keyframes_a = cmds.keyframe(a, query=True, keyframeCount=True)
    has_keyframes_b = cmds.keyframe(b, query=True, keyframeCount=True)

    # Swap positions.
    if translate:
        pos_a = cmds.xform(a, query=True, worldSpace=True, translation=True)
        pos_b = cmds.xform(b, query=True, worldSpace=True, translation=True)
   
        cmds.xform(a, translation=pos_b, worldSpace=True)
        cmds.xform(b, translation=pos_a, worldSpace=True)

        translate_attributes = ['.translateX', '.translateY', '.translateZ']         
        if has_keyframes_a:
            for attr in translate_attributes:
                cmds.setKeyframe(a, attribute=attr)    
        if has_keyframes_b:
            for attr in translate_attributes:
                cmds.setKeyframe(b, attribute=attr)
    
    # Swap rotations.
    if rotate:   
        rot_a = cmds.xform(a, query=True, worldSpace=True, rotation=True)
        rot_b = cmds.xform(b, query=True, worldSpace=True, rotation=True)
        
        cmds.xform(a, rotation=rot_b, worldSpace=True)
        cmds.xform(b, rotation=rot_a, worldSpace=True)

        rotate_attributes = ['.rotateX', '.rotateY', '.rotateZ']
        if has_keyframes_a:
            for attr in rotate_attributes:
                cmds.setKeyframe(a, attribute=attr)           
        if has_keyframes_b:
            for attr in rotate_attributes:
                cmds.setKeyframe(b, attribute=attr)


"""
##################################################################################################################################################
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-20- 0001:
#   - First pass.
# ---------------------------------------
##################################################################################################################################################
"""