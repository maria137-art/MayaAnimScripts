"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_outliner_snippets.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of scripts to work in the Outliner panel faster.
# They all currently only work when the mouse cursor is above the Outliner.
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------
import importlib
import mr_outliner_snippets
importlib.reload(mr_outliner_snippets)

mr_outliner_snippets.outliner_collapse_all_items_except_selected

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-07-08: 0001 
#   - First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

def outliner_collapse_all_items():
    panel = mel.eval("getCurrentOutlinerPanel ;")
    if panel:
        cmds.outlinerEditor(panel, edit=True, expandAllItems=False)

def outliner_collapse_all_items_except_selected():
    sel = cmds.ls(selection=True)
    
    panel = mel.eval("getCurrentOutlinerPanel;")
    if panel:
        cmds.outlinerEditor(panel, edit=True, expandAllItems=False)
    
    cmds.select(sel)
    mel.eval("FrameSelectedWithoutChildren;")

def outliner_expand_all_items():
    panel = mel.eval("getCurrentOutlinerPanel ;")
    if panel:
        cmds.outlinerEditor(panel, edit=True, expandAllItems=True)