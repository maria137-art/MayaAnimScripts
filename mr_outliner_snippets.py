"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_outliner_snippets.py
# VERSION: 0004
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of scripts to work in the Outliner panel faster.
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------
import importlib
import mr_outliner_snippets
importlib.reload(mr_outliner_snippets)

# e.g.
mr_outliner_snippets.outliner_collapse_all_except_selected()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-29 - 0004:
#   - Updating function names.
#
# 2023-07-09 - 0003:
#   - Updating functions, so that the mouse cursor doesn't have to be
#     above the Outliner, in order to trigger.
#   - Adding outliner_expand_children_of_selected()
#
# 2023-07-09 - 0002:
#   - Realised that Maya has default hotkeys for Outliner scripts in MEL.
#   - Oh well, at least have Python versions now, in case.
#
# 2023-07-08 - 0001 :
#   - First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

def get_visible_outliner_panels():
    outliner_panels = cmds.getPanel(type='outlinerPanel')
    visible_panels = cmds.getPanel(visiblePanels=True)
    
    visible_outliner_panels = [panel for panel in outliner_panels if panel in visible_panels]
    return visible_outliner_panels

# ------------------------------------------------------------------- 
# 00. FOR ALL ITEMS.
# ------------------------------------------------------------------- 
def outliner_expand_all():
    visible_outliner_panels = get_visible_outliner_panels()
    [cmds.outlinerEditor(outliner, edit=True, expandAllItems=True) for outliner in visible_outliner_panels]     

# ------------------------------------------------------------------- 
def outliner_collapse_all():    
    visible_outliner_panels = get_visible_outliner_panels()
    [cmds.outlinerEditor(outliner, edit=True, expandAllItems=False) for outliner in visible_outliner_panels]     

# ------------------------------------------------------------------- 
# 00. FOR SELECTED ITEMS.
# ------------------------------------------------------------------- 
def outliner_expand_selected():
    visible_outliner_panels = get_visible_outliner_panels()
    [cmds.outlinerEditor(outliner, edit=True, expandAllSelectedItems=True) for outliner in visible_outliner_panels]         

# ------------------------------------------------------------------- 
def outliner_collapse_selected():
    visible_outliner_panels = get_visible_outliner_panels()
    [cmds.outlinerEditor(outliner, edit=True, expandAllSelectedItems=False) for outliner in visible_outliner_panels]         

# ------------------------------------------------------------------- 
def outliner_expand_children_of_selected():
    # Get visible outliners
    visible_outliner_panels = get_visible_outliner_panels()
    [cmds.outlinerEditor(outliner, edit=True, expandAllItems=False) for outliner in visible_outliner_panels]       
    
    # Get children of selected
    sel = cmds.ls(selection=True)
    children = [child for obj in sel for child in cmds.listRelatives(obj, children=True, type='transform') or [] ]
    
    # Filter out constraints from the selection
    constraint_types = {"pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "parentConstraint"}
    transform_children = [obj for obj in children if cmds.nodeType(obj) == "transform" and not cmds.listRelatives(obj, type=list(constraint_types))]
    
    cmds.select(transform_children)
    
    [cmds.outlinerEditor(outliner, edit=True, showSelected=True) for outliner in visible_outliner_panels]      

# ------------------------------------------------------------------- 
# 00. FOR ALL EXCEPT SELECTED ITEMS.
# -------------------------------------------------------------------
def outliner_collapse_all_except_selected():
    visible_outliner_panels = get_visible_outliner_panels()
    [cmds.outlinerEditor(outliner, edit=True, expandAllItems=False) for outliner in visible_outliner_panels]         

    [cmds.outlinerEditor(outliner, edit=True, showSelected=True) for outliner in visible_outliner_panels]