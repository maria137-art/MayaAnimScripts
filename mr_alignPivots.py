"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_alignPivots.py
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
import mr_alignPivots
importlib.reload(mr_alignPivots)

mr_alignPivots.main()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-30 - 0002:
#   - Rename from mr_align_pivots.py.
#
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