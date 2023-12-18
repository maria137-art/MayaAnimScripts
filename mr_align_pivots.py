"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_align_pivots.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Align pivots of selected objects to the last one selected. 
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_align_pivots
importlib.reload(mr_align_pivots)

mr_align_pivots.main()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-17 - 0001:
# 	- First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def main():
    sel = cmds.ls(selection=True)
    if len(sel) >= 2:
        # Get the pivot to match.
        target_pivot = cmds.xform(sel[-1], query=True, worldSpace=True, rotatePivot=True)

        # For every selected object (except the last one),
        for obj in sel[:-1]:
            # match its pivot to the target_pivot.
            cmds.xform(obj, worldSpace=True, rotatePivot=target_pivot)

        # Deselect the target_pivot's object (to make it clearer the script has finished).
        cmds.select(sel[-1], deselect=True)

        cmds.warning("Pivots aligned successfully.")
    else:
        cmds.warning("Please select at least two objects.")