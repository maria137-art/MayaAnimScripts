"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_selectVisibleControls.py
# VERSION: 0005
#
# CREATORS: Maria Robertson
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Select one of several object types, based on their visibility in the current 
# panel (whichever model panel the mouse cursor is pointing over at the time).
#
# Current function options are:
# - NURB curves
# - Locators
# - Key Locators
# - NURBs curves + keyed locators
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
import mr_select_visible_controls
importlib.reload(mr_select_visible_controls)

# USE ONE OF THE FOLLOWING
mr_select_visible_controls.select_visible_curves_in_panel(select_keyed_only=False)
mr_select_visible_controls.select_visible_locators_in_panel(select_keyed_only=False)
mr_select_visible_controls.select_visible_locators_in_panel(select_keyed_only=True)
mr_select_visible_controls.select_visible_curves_and_keyed_locators_in_panel()

# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# For learning more how dictionaries can work with functions.
# https://stackoverflow.com/a/9168387
#
# Dictionary examples
# https://www.w3schools.com/python/python_dictionaries.asp
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
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
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def select_visible_curves_in_panel(select_keyed_only=False):
    # -------------------------------------------------------------------
    # 01. CHECK IF CURRENT PANEL IS VALID.
    # -------------------------------------------------------------------
    modelPanel = check_current_panel_is_valid()
    if not modelPanel:
        return

    # -------------------------------------------------------------------
    # 01. SELECT ONLY TRANSFORMS OF VISIBLE NURBS CURVES IN THE CURRENT PANEL.
    # -------------------------------------------------------------------
    visible_curves = cmds.ls(type="nurbsCurve", visible=True, long=True)
    visible_curves_in_panel = []
    visible_curves_transforms_in_panel = [] 

    if visible_curves:

        for curve in visible_curves:
            # Check if visible in the current panel.
            if cmds.modelEditor(modelPanel, query=True, nurbsCurves=True):
                visible_curves_in_panel.append(curve)
    
        if visible_curves_in_panel:
            for curve in visible_curves_in_panel:
                visible_curves_transforms_in_panel.append(cmds.listRelatives(curve, parent=True)[0])

            # -------------------------------------------------------------------
            # 01. CHECK WHETHER TO SELECT ONLY KEYED OBJECTS.
            # -------------------------------------------------------------------
            if select_keyed_only:
                keyed_visible_curves_transforms_in_panel = select_keyed_objects_from_selection(visible_curves_transforms_in_panel)
                return keyed_visible_curves_transforms_in_panel
            else:
                cmds.select(visible_curves_transforms_in_panel)
                return visible_curves_transforms_in_panel

# ------------------------------------------------------------------------------ #

def select_visible_locators_in_panel(select_keyed_only=False):
    # -------------------------------------------------------------------
    # 01. CHECK IF CURRENT PANEL IS VALID.
    # -------------------------------------------------------------------
    modelPanel = check_current_panel_is_valid()
    if not modelPanel:
        return

    # -------------------------------------------------------------------
    # 01. SELECT ONLY TRANSFORMS OF VISIBLE LOCATORS IN THE CURRENT PANEL.
    # -------------------------------------------------------------------
    visible_locators = cmds.ls(type="locator", visible=True, long=True)
    visible_locators_in_panel = []
    visible_locators_transforms_in_panel = []

    if visible_locators:
        for loc in visible_locators:
            if cmds.modelEditor(modelPanel, query=True, locators=True):
                visible_locators_in_panel.append(loc)  

        # Create a list of their transform nodes.
        for loc in visible_locators_in_panel:
            visible_locators_transforms_in_panel.append(cmds.listRelatives(loc, parent=True)[0])

        # -------------------------------------------------------------------
        # 01. CHECK WHETHER TO SELECT ONLY KEYED OBJECTS.
        # -------------------------------------------------------------------
        if select_keyed_only:
            keyed_visible_locator_transforms_in_panel = select_keyed_objects_from_selection(visible_locators_transforms_in_panel)
            return keyed_visible_locator_transforms_in_panel
        else:
            cmds.select(visible_locators_transforms_in_panel)
            return visible_locators_transforms_in_panel


# ------------------------------------------------------------------------------ #

def select_visible_curves_and_keyed_locators_in_panel():
    curves = select_visible_curves_in_panel(select_keyed_only=False)
    keyed_locators = select_visible_locators_in_panel(select_keyed_only=True)

    cmds.select(curves, replace=True)
    cmds.select(keyed_locators, add=True)

# ------------------------------------------------------------------------------ #

def check_current_panel_is_valid():
    # Check the panel where the mouse cursor is over.
    modelPanel = cmds.getPanel(withFocus=True)

    # Check if the current panel is a modelPanel.
    if cmds.getPanel(typeOf=modelPanel) != "modelPanel":
        cmds.warning("The current panel is not a 3D view panel.")
    else:
        return modelPanel

# ------------------------------------------------------------------------------ #

def select_keyed_objects_from_selection(selection):
    keyed_objects = []

    for obj in selection:
        attributes = cmds.listAttr(obj, keyable=True, unlocked=True)

        if attributes:
            for attr in attributes:
                if cmds.keyframe(obj, query=True, attribute=attr):
                    keyed_objects.append(obj)

    if keyed_objects:
        return keyed_objects