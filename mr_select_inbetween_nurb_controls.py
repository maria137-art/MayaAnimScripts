"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_select_inbetween_nurb_controls.py
# VERSION: 0003
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A script to help make selecting controls in hierarchies faster.

# EXAMPLE USES:
# ---------------------------------------
#   - Selecting tail controls
#   - Selecting spine controls
#
# INSTRUCTIONS:
# ---------------------------------------
# Select two NURB controls, and run the script to also select any inbetween NURB controls.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
e.g.

import importlib
import mr_select_inbetween_nurb_controls
importlib.reload(mr_select_inbetween_nurb_controls)

mr_select_inbetween_nurb_controls.mr_select_inbetween_nurb_controls()

# ---------------------------------------
# WISHLIST:
# ---------------------------------------
# - Get it working properly so it respects only one hierarchy path
#   e.g. when root and a head is selected, it must only select them, not everything else
# - Work when controls are selected backwards
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
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

def mr_select_inbetween_nurb_controls():

    # ------------------------------------------------------------------- 
    # 01. CHECK IF ONLY TWO OBJECTS ARE SELECTED
    # ------------------------------------------------------------------- 
    sel = cmds.ls(selection=True)

    if len(sel) != 2:
        cmds.warning("Please select exactly two objects.")
        return

    # ------------------------------------------------------------------- 
    # 01. CHECK IF SELECTED CONTROLS ARE NURB CURVE TRANSFORMS
    # ------------------------------------------------------------------- 
    for obj in sel:
        shape = cmds.listRelatives(obj, shapes=True)
        if shape and cmds.nodeType(shape[0]) == "nurbsCurve":
            continue
        else:
            cmds.warning("Both selected objects must be NURB Curve transforms.")
            return

    # ------------------------------------------------------------------- 
    # 01. CHECK IF OBJECTS SHARE SAME HIERARCHY
    # -------------------------------------------------------------------
    # Declare and initialize variables.
    first_item = sel[0]
    second_item = sel[1]

    first_fullpath = cmds.ls(first_item, long=True)[0]
    second_fullpath = cmds.ls(second_item, long=True)[0]

    first_object_hierarchy = first_fullpath.split('|')       
    second_object_hierarchy = second_fullpath.split('|')       

    hierarchy_objects = []
    order = []

    # If objects are in same hierarchy, add them to hierarchy_objects variable.
    if first_item in second_object_hierarchy:
        order = "top-to-bottom"
        for obj in second_object_hierarchy[1:]:
            hierarchy_objects.append(obj)
        
    elif second_item in first_object_hierarchy:
        order = "bottom-to-top"
        for obj in first_object_hierarchy[1:]:
            hierarchy_objects.append(obj)
    else:
        cmds.warning("Must select two objects in same branch")
        return

    # ------------------------------------------------------------------- 
    # 01. SELECT ONLY OBJECTS INBETWEEN SELECTION
    # -------------------------------------------------------------------
    # Find the index of the selected objects in hierarchy_objects.
    index1 = hierarchy_objects.index(first_item)
    index2 = hierarchy_objects.index(second_item)

    inbetween_objects = hierarchy_objects[min(index1, index2):max(index1, index2) + 1]

    # Filter out unwanted transform types in inbetween_objects.
    selected_transforms = [obj for obj in inbetween_objects if cmds.nodeType(obj) == "transform"]

    # Create list of only NURBS curve transforms from selected_transforms.
    nurbs_curve_transforms = [transform for transform in selected_transforms if cmds.listRelatives(transform, shapes=True) and cmds.nodeType(cmds.listRelatives(transform, shapes=True)[0]) == "nurbsCurve"]

    if not nurbs_curve_transforms:
        cmds.warning("No NURBS curve transforms found between the selected objects.")
        return

    # ------------------------------------------------------------------- 
    # 01. FINISH SCRIPT WITH FOUND NURB CURVE TRANSFORMS SELECTED
    # -------------------------------------------------------------------
    if order == "top-to-bottom":
        cmds.select(nurbs_curve_transforms, replace=True)
    else:
        reversed_nurbs_curve_transforms = nurbs_curve_transforms[::-1] 
        cmds.select(reversed_nurbs_curve_transforms, replace=True)

    # End with the Translate manipulator on.
    mel.eval("buildTranslateMM;")
    mel.eval("destroySTRSMarkingMenu MoveTool;")