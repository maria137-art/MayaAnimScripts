"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_selectNURBSCurvesInbetween.py
# VERSION: 0003
#
# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A script to help make selecting controls in hierarchies faster.
#
# EXAMPLE USES:
# ---------------------------------------
#   - Selecting tail controls
#   - Selecting spine controls
#
# INSTRUCTIONS:
# ---------------------------------------
# Select two NURB controls, and run the script to also select any inbetween NURB controls.
#   e.g. select tail_01_ctrl and tail_12_ctrl to also select every tail_ctrl inbetween them.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

import importlib
import mr_selectNURBSCurvesInbetween
importlib.reload(mr_selectNURBSCurvesInbetween)

mr_selectNURBSCurvesInbetween.main(always_select_top_to_bottom=False)

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-15 - 0003:
#   - Renaming from mr_select_inbetween_nurb_controls.py to mr_selectNURBSCurvesInbetween.py.
#   - Added option to always select from top to bottom, regardless of selection order.
#
# 2023-07-09 - 0002:
#   - Cleaning comments.
#   - Removing unneeded check for constraints.
#
# 2023-07-09 - 0002:
#   - Finished second pass of script, to work in both top-to-bottom and bottom-to-top hierarchies.
#
# 2023-07-03 - 0001: 
#   - First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

def main(always_select_top_to_bottom=False):
    # ------------------------------------------------------------------- 
    # 01. CHECK IF ONLY TWO OBJECTS ARE SELECTED.
    # ------------------------------------------------------------------- 
    selection = cmds.ls(selection=True)

    if len(selection) != 2:
        cmds.warning("Please select exactly two objects.")
        return

    # ------------------------------------------------------------------- 
    # 01. CHECK IF SELECTED CONTROLS ARE NURBS CURVE TRANSFORMS.
    # ------------------------------------------------------------------- 
    for obj in selection:
        shape = cmds.listRelatives(obj, shapes=True)
        if shape and cmds.nodeType(shape[0]) == "nurbsCurve":
            continue
        else:
            cmds.warning("Both selected objects must be NURB Curve transforms.")
            return

    # ------------------------------------------------------------------- 
    # 01. CHECK IF OBJECTS SHARE SAME HIERARCHY.
    # -------------------------------------------------------------------
    first_item = selection[0]
    second_item = selection[1]

    first_fullpath = cmds.ls(first_item, long=True)[0]
    second_fullpath = cmds.ls(second_item, long=True)[0]

    first_object_hierarchy = first_fullpath.split('|')       
    second_object_hierarchy = second_fullpath.split('|')       

    hierarchy_objects = []
    order = []

    if first_item in second_object_hierarchy:
        order = "top-to-bottom"
        for obj in second_object_hierarchy[1:]:
            hierarchy_objects.append(obj)
        
    elif second_item in first_object_hierarchy:
        order = "bottom-to-top"
        for obj in first_object_hierarchy[1:]:
            hierarchy_objects.append(obj)
    else:
        cmds.warning("Must select two objects in the same hierarchy branch.")
        return

    # ------------------------------------------------------------------- 
    # 01. SELECT ONLY NURBS CURVES INBETWEEN THE SELECTION.
    # -------------------------------------------------------------------
    # Find the index of the selected objects in hierarchy_objects.
    index1 = hierarchy_objects.index(first_item)
    index2 = hierarchy_objects.index(second_item)

    inbetween_objects = hierarchy_objects[min(index1, index2):max(index1, index2) + 1]

    # Filter out unwanted transform types in inbetween_objects.
    selected_transforms = [obj for obj in inbetween_objects if cmds.nodeType(obj) == "transform"]

    # Create list of only NURBS curve transforms from selected_transforms.
    nurbs_curve_transforms = [
        transform 
        for transform in selected_transforms 
        if cmds.listRelatives(transform, shapes=True) and 
        cmds.nodeType(cmds.listRelatives(transform, shapes=True)[0]) == "nurbsCurve"]

    if not nurbs_curve_transforms:
        cmds.warning("No NURBS curve transforms found between the selected objects.")
        return

    # ------------------------------------------------------------------- 
    # 01. FINSH WITH FOUND NURBS CURVE TRANSFORMS SELECTED.
    # -------------------------------------------------------------------
    if order == "top-to-bottom":
        cmds.select(nurbs_curve_transforms, replace=True)
    else:
        if always_select_top_to_bottom:
            cmds.select(nurbs_curve_transforms, replace=True)
        else:
            reversed_nurbs_curve_transforms = nurbs_curve_transforms[::-1] 
            cmds.select(reversed_nurbs_curve_transforms, replace=True)

    # End with the Translate manipulator on.
    mel.eval("buildTranslateMM;")
    mel.eval("destroySTRSMarkingMenu MoveTool;")