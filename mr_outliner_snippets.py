"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_outliner_snippets.py
# VERSION: 0002
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
# 2023-07-09: 0002
#   - Realised that Maya has default hotkeys for Outliner scripts in MEL.
#   - Oh well, at least have Python versions now, in case.
#
# 2023-07-08: 0001 
#   - First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

# ------------------------------------------------------------------------------ #
def outliner_expand_all_items():
    panel = mel.eval("getCurrentOutlinerPanel ;")
    if panel:
        cmds.outlinerEditor(panel, edit=True, expandAllItems=True)

# ------------------------------------------------------------------------------ #
def outliner_collapse_all_items():
    panel = mel.eval("getCurrentOutlinerPanel ;")
    if panel:
        cmds.outlinerEditor(panel, edit=True, expandAllItems=False)

# ------------------------------------------------------------------------------ #
def outliner_expand_all_selected_items():
    panel = mel.eval("getCurrentOutlinerPanel ;")
    if panel:
        cmds.outlinerEditor(panel, edit=True, expandAllSelectedItems=True)

# ------------------------------------------------------------------------------ #
def outliner_collapse_all_selected_items():
    panel = mel.eval("getCurrentOutlinerPanel ;")
    if panel:
        cmds.outlinerEditor(panel, edit=True, expandAllSelectedItems=False)

# ------------------------------------------------------------------------------ #
def outliner_collapse_all_items_except_selected():
    sel = cmds.ls(selection=True)
    
    panel = mel.eval("getCurrentOutlinerPanel;")
    if panel:
        cmds.outlinerEditor(panel, edit=True, expandAllItems=False)
    
    cmds.select(sel)
    mel.eval("FrameSelectedWithoutChildren;")

