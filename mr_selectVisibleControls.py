"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_selectVisibleControls.py
# VERSION: 0010
#
# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Select one of several object types, based on their visibility in the current panel
# (whichever model panel the mouse cursor is pointing over at the time).
#
# EXAMPLE USES:
# ---------------------------------------
# Useful when extra or unneccessary control are hidden, so controls you're focusing
# on can be quickly keyed.
#
# When working with temp locators often, NURBs curves + keyed locators might be helpful.
# 
# Example hotkeys to assign to:
#   ALT + A
# 
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------

import importlib
import mr_selectVisibleControls
importlib.reload(mr_selectVisibleControls)

# USE ANY OF THE FOLLOWING FUNCTIONS
cmds.select(mr_selectVisibleControls.get_visible_NURBS_curves_in_panel(only_keyed=False))
cmds.select(mr_selectVisibleControls.get_visible_locators_in_panel(only_keyed=False))
mr_selectVisibleControls.select_visible_curves_and_keyed_locators_in_panel()

# ---------------------------------------
# REQUIREMENTS: 
# ---------------------------------------
# This script uses functions from mr_utilities.py.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

import importlib
import mr_utilities
importlib.reload(mr_utilities)

# ------------------------------------------------------------------------------ #
def get_visible_NURBS_curves_in_panel(only_keyed=False):
    """
    Get a list of visible NURBS curve transform nodes in the current Maya modelPanel.
    
    :param only_keyed: If True, only return nodes that have keys on them.
    :type only_keyed: bool
    :return: List of visible NURBS curve transform nodes.
    :rtype: list (str)
    """
    # Check the mouse cursor is over a modelPanel.
    modelPanel = mr_utilities.is_current_panel_modelPanel()
    if not modelPanel:
        return []

    # Check if Display NURB Curves is enabled in the modelPanel.
    if not cmds.modelEditor(modelPanel, query=True, nurbsCurves=True):
        return []
   
   # Get all visible nurb curves.
    visible_transforms = cmds.ls(type='transform', visible=True, dag=True)
    visible_nurbs_curve_transforms = (
        node 
        for node in visible_transforms
        if (
            # Check the node.
            mr_utilities.is_nurbs_curve(node) and
            mr_utilities.is_visible(node) and

            # Check if at least one its shapes are visible.
            any(
                mr_utilities.is_visible(shape) 
                for shape in cmds.listRelatives(node, shapes=True) or ()
            # Check if at least one of its shapes have their Drawing Override set to Normal.
            ) and all(
                cmds.getAttr(f"{shape}.overrideDisplayType") != 0 
                for shape in cmds.listRelatives(node, shapes=True) or ()
            ) and
            # Check its parent's visibility.
            mr_utilities.are_parents_visible(node)
        )
    )


    # OPTIONAL - Select only keyed visible NURBS curves.
    if only_keyed:
        return mr_utilities.get_keyed_nodes(visible_nurbs_curve_transforms)

    else:
        return visible_nurbs_curve_transforms
        # print(f'Found {len(visible_nurbs_curve_transforms)} valid NURBS curves.')

# ------------------------------------------------------------------------------ #
def get_visible_locators_in_panel(only_keyed=False):
    """
    Get a list of visible locators in the current Maya modelPanel.
    
    :param only_keyed: If True, only return nodes that are keyed.
    :type only_keyed: bool
    :return: Generator of visible locator transform nodes.
    :rtype: generator (str)
    """
    # Check the mouse cursor is over a modelPanel.
    modelPanel = mr_utilities.is_current_panel_modelPanel()
    if not modelPanel:
        return []

    # Check if Display Locators is enabled in the modelPanel.
    if not cmds.modelEditor(modelPanel, query=True, locators=True):
        return []

    # Get transforms of visible locators.
    visible_locator_shapes = cmds.ls(type="locator", visible=True)
    visible_locator_shapes = (
        shape for shape in visible_locator_shapes
        if (
            mr_utilities.is_visible(shape)
        )
    )

    for shape in visible_locator_shapes:
        loc_transform = cmds.listRelatives(shape, parent=True)[0]
        
        # OPTIONAL - Select only keyed visible locators.
        if only_keyed:
            if cmds.keyframe(loc_transform, query=True):
                yield loc_transform
        else:
            yield loc_transform

# ------------------------------------------------------------------------------ #
def select_visible_curves_and_keyed_locators_in_panel():
    """
    Selects visible NURBS curves and visible keyed locators in the current Maya model panel.

    """
    curves = get_visible_NURBS_curves_in_panel(only_keyed=False)

    keyed_locators = get_visible_locators_in_panel(only_keyed=True)

    cmds.select(curves, replace=True)
    cmds.select(keyed_locators, add=True)

"""
##################################################################################################################################################
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-05-27 - 0010:
#   - get_visible_NURBS_curves_in_panel()
#       - Edits based on working with unfinished rigs (that had part of its control shapes hidden).
#           - Check if at least one of the node's shapes is visible.
#           - Check if at least one of the node's shapes have their Drawing Override set to Normal.
#
# 2023-01-16 - 0009:
#   - get_visible_NURBS_curves_in_panel()
#       - Add check for if all parents are visible.
#
# 2023-01-15 - 0008:
#   - Add check for if a NURBS curve has its shape's Drawing Override Display Type set to normal.
#       - This should help avoid NURBS curves in rigs that shouldn't be touched.
#
# 2023-01-14 - 0007:
#   - Updating script to use mr_utilities functions.
#       - Check for lodVisibility as well.
#   - Learnt how amazing Python generators are!
#       - Replaced some lists with generators to speed things up.
#           - e.g. one test of selecting 2000 locators that took 48 secs before now takes 2 secs.
#
# 2023-12-30 - 0006:
#   - Rename.
#
# 2023-12-29 - 0005:
#   - Adding function for selecting only keyed objects.
#
# 2023-12-29 - 0004:
#   - Simplifying script, and adding more checks to avoid NoneType errors.
#
# 2023-04-11 - 0003:
#   - Worked to make script more flexible, separating logic into more functions while learning Python.
#
# 2023-04-11 - 0002:
#   - Added option to select locators that have keys on unlocked channels.
# -  For when animating with temp locators.
# ---------------------------------------
##################################################################################################################################################
"""