"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_round_rotations_toNearest360.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Rounds selected rotation values to the nearest multiple of 360.
#
# EXAMPLE USES:
# ---------------------------------------
# Can be helpful when animating spins, and wanting to adjust the pose on the current frame without ruining the animCurve.
#
# INSTRUCTIONS:
# ---------------------------------------
# If no rotate attributes are highlighted in the channel box, the script will round Rotate X, Y and Z to the nearest multiple fo 360.
# Otherwise it will round only highlighted ones.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_round_rotations_toNearest360
importlib.reload(mr_round_rotations_toNearest360)

mr_round_rotations_toNearest360.round_rotation()

# ---------------------------------------
# WISH LIST:
# ---------------------------------------
# - Round only highlighted rotation attributes, if any are selected.
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-07-11: 0001 
#   - First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import math

def get_highlighted_attributes():
    # Fetch Maya's ChannelBox.
    channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')


def round_rotation():
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("No object selected.")
        return
    
    # Get the rotation values for the current frame.
    rotate_x = cmds.getAttr(sel[0] + ".rotateX")
    rotate_y = cmds.getAttr(sel[0] + ".rotateY")
    rotate_z = cmds.getAttr(sel[0] + ".rotateZ")
    
    # Round the rotation values to the nearest multiple of 360.
    rounded_x = round_to_nearest_multiple(rotate_x, 360)
    rounded_y = round_to_nearest_multiple(rotate_y, 360)
    rounded_z = round_to_nearest_multiple(rotate_z, 360)
    
    # Set the rounded rotation values back to the object.
    cmds.setAttr(sel[0] + ".rotateX", rounded_x)
    cmds.setAttr(sel[0] + ".rotateY", rounded_y)
    cmds.setAttr(sel[0] + ".rotateZ", rounded_z)
    
    print("Rotation values rounded successfully.")

def round_to_nearest_multiple(value, multiple):
    return round(value / multiple) * multiple