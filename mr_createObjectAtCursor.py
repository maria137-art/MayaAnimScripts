"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_createObjectAtCursor.py
# VERSION: 0003
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Create an object wherever the mouse cursor is.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_createObjectAtCursor
importlib.reload(mr_createObjectAtCursor)

mr_createObjectAtCursor.main("sphere")

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-30 - 0003:
#   Rename from mr_createObjectAtCursor.py.
#
# 2023-12-29 - 0002:
#   - Converting MEL script to Python.
#   - Making more modular.
#
# 2023-04-11 - 0001:
#   - First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def main(object=None):
    if object not in ["sphere"]:
        cmds.warning("Please specify in the run command to create a \"sphere\".")
        return

    if object == "sphere":
        object = create_sphere()     

    # Place the sphere at the cursor position.
    pos = cmds.autoPlace(useMouse=True)
    cmds.move(pos[0], pos[1], pos[2], object)


def create_sphere():
    sphere = cmds.polySphere(
        radius=1, 
        subdivisionsX=20, 
        subdivisionsY=20, 
        axis=[0, 1, 0], 
        createUVs=2, 
        constructionHistory=1
        )[0]

    return sphere