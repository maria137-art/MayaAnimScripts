"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_select_inbetween_nurb_controls.py
# VERSION: 0002
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
#   - Finished second pass of script, to work in both top-to-bottom and bottom-to-top hierarchies
#
# 2023-07-03 - 0001: 
#   - First pass
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def mr_select_inbetween_nurb_controls():

    ##################################################################
    # Check if only two objects are selected
    sel = cmds.ls(selection=True)

    if len(sel) != 2:
        cmds.warning("Please select exactly two objects.")
        return
    ##################################################################
    # Check if selected controls are NURB curves

    # For every selected object
    for obj in sel:
        # Check if it is a transform node of a NURB curve
        shape = cmds.listRelatives(obj, shapes=True)
        if shape and cmds.nodeType(shape[0]) == "nurbsCurve":
            continue
        else:
            cmds.warning("Both selected objects must be NURB Curve transforms.")
            return
    ##################################################################

    # Check if objects are in same hierarchy
    first_item = sel[0]
    second_item = sel[1]

    if len(sel) != 2:
        cmds.warning("Please select exactly two objects.")
        return
            
    first_fullpath = cmds.ls(first_item, long=True)[0]
    second_fullpath = cmds.ls(second_item, long=True)[0]

    first_object_names = first_fullpath.split('|')       
    second_object_names = second_fullpath.split('|')       

    # If objects are in same hierarchy, append them to variable
    found_objects = []
    transforms_nodes = []    
    mode = []
    if first_item in second_object_names:
        mode = "top-to-bottom"
        for obj in second_object_names[1:]:
            found_objects.append(obj)
        
    elif second_item in first_object_names:
        mode = "bottom-to-top"
        for obj in first_object_names[1:]:
            found_objects.append(obj)
    else:
        cmds.warning("Must select two objects in same branch")
        return
    #####################################################

    # Select only stuff inbetween the two items

    # Find the index of the selected objects in the list
    index1 = found_objects.index(first_item)
    index2 = found_objects.index(second_item)

    # Select the objects between the two selected objects
    inbetween_objects = found_objects[max(index1, index2):min(index1, index2) - 1:-1]  # Reverse the selection order
    # reverse selection
    inbetween_objects = inbetween_objects[::-1] 

    # Filter out constraints from the selection
    constraint_types = {"pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "parentConstraint"}
    selected_transforms = [obj for obj in inbetween_objects if cmds.nodeType(obj) == "transform" and not cmds.listRelatives(obj, type=list(constraint_types))]

    # Select only the NURBS curve transforms from the list
    nurbs_curve_transforms = [transform for transform in selected_transforms if cmds.listRelatives(transform, shapes=True) and cmds.nodeType(cmds.listRelatives(transform, shapes=True)[0]) == "nurbsCurve"]

    if not nurbs_curve_transforms:
        cmds.warning("No NURBS curve transforms found between the selected objects.")
        return

    if mode == "top-to-bottom":
        cmds.select(nurbs_curve_transforms, replace=True)
    else:
        reversed_nurbs_curve_transforms = nurbs_curve_transforms[::-1] 
        cmds.select(reversed_nurbs_curve_transforms, replace=True)