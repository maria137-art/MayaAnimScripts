import maya.cmds as cmds

"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_select_visible_controls.py
# VERSION: 0003
#
# CREATORS: Maria Robertson
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Selects one of the following object types, based on their visibility in the current 
# panel (whichever model panel the mouse cursor is pointing over at the time).
#
# - Option A: NURB curves
# - Option B: NURB curves and locators 
# - Option C: NURB curves, and locators with keys on unlocked channels
#
# EXAMPLE USES:
# ---------------------------------------
# Useful when extra or unneccessary control are hidden, so controls you're focusing
# on can be quickly keyed.
# 
# Example hotkeys to assign to:
#   ALT + A
#
# INSTRUCTIONS: 
# ---------------------------------------
# Copy and paste the Run Commands into a hotkey, using a letter corresponding to
# the Option you'd like to use.
#
# e.g. 
# mr_select_visible_controls("A")
# mr_select_visible_controls("B")
# mr_select_visible_controls("C")
# 
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------

import importlib

import mr_select_visible_controls
importlib.reload(mr_select_visible_controls)

mr_select_visible_controls.mr_select_visible_controls("C")

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
# 2023-04-11 - 0003
# Worked to make script more flexible, separating logic into more functions while learning Python.
#
# 2023-04-11 - 0002
# Added option to select locators that have keys on unlocked channels.
# For when animating with temp locators.
# ------------------------------------------------------------------------------ #
"""

def mr_select_visible_controls(option):

    # get the current panel
    panel = cmds.getPanel(withFocus=True)

    # check if the current panel is a modelPanel
    if cmds.getPanel(typeOf=panel) != "modelPanel":
        print("The current panel is not a 3D view panel.")
    
    else: 
        # ------------------------------------------------------------------------------ #
        # Functions to define objects to search for.
        def look_for_visible_NURB_curves():

            visible_nurbs_curves = []
            visible_nurbs_transforms = []

            # For every NURB curve that exists, check if its visible in the current panel.
            for curve in cmds.ls(type="nurbsCurve", visible=True, long=True):
                if cmds.modelEditor(panel, query=True, nurbsCurves=True):
                    visible_nurbs_curves.append(curve)

            # Create a list of their transform nodes.
            for curve in visible_nurbs_curves:
                visible_nurbs_transforms.append(cmds.listRelatives(curve, parent=True)[0])

            # If there are any in the list, select them
            if visible_nurbs_transforms:
                cmds.select(visible_nurbs_transforms)

            return visible_nurbs_transforms

        def look_for_visible_locators():

            visible_locators = []
            visible_locators_transforms = []

            # For every locator, check if it's visible in the current panel
            for locator in cmds.ls(type="locator", visible=True, long=True):
                if cmds.modelEditor(panel, query=True, locators=True):
                    visible_locators.append(locator)  

            # Create a list of their transform nodes.
            for loc in visible_locators:
                visible_locators_transforms.append(cmds.listRelatives(loc, parent=True)[0])

            return visible_locators_transforms

        def look_for_keyed_visible_locators(visible_locators_transforms):

            keyed_visible_locator_transforms = []

            # Iterate through each locator
            for loc in visible_locators_transforms:

                # Get a list of all the keyable and visible attributes in the transform node
                attributes = cmds.listAttr(loc, keyable=True, visible=True, unlocked=True)
            
                # Check if any of the attributes have set keys
                for attr in attributes:
                    if cmds.keyframe(loc, q=True, at=attr):
                        keyed_visible_locator_transforms.append(loc)  
                        break

            return keyed_visible_locator_transforms
        
        # ------------------------------------------------------------------------------ #
        # Call functions. (Naming these with the same as their local variable that it returns inside their function.)
        visible_nurbs_transforms = look_for_visible_NURB_curves()
        visible_locators_transforms = look_for_visible_locators()
        keyed_visible_locator_transforms = look_for_keyed_visible_locators(visible_locators_transforms)      

        # ------------------------------------------------------------------------------ #
        # Functions for selection.

        def option_A_select_visible_NURB_curves(visible_nurbs_transforms):

            # Select transform nodes of all visible NURBS curves in the current panel.
            if visible_nurbs_transforms:
                cmds.select(visible_nurbs_transforms)
            # debug
            print("Option A")
            
        def option_B_select_visible_NURB_curves_and_locators(visible_nurbs_transforms, visible_locators_transforms):
            # Select transform nodes of all visible NURBS curves in the current panel.
            if visible_nurbs_transforms:
                cmds.select(visible_nurbs_transforms)
            
            # Select transform nodes of all visible locators in the current panel
            if visible_locators_transforms:
                cmds.select(visible_locators_transforms, add=True)
            # debug
            print("Option B")

        def option_C_select_visible_NURB_curves_and_keyed_locators(visible_nurbs_transforms, keyed_visible_locator_transforms):

            # Select transform nodes of all visible NURBS curves in the current panel.
            if visible_nurbs_transforms:
                cmds.select(visible_nurbs_transforms)
            
            # Select transform nodes of all visible locators in the current panel that have keys on unlocked channels.
            if keyed_visible_locator_transforms:
                cmds.select(keyed_visible_locator_transforms, add=True)
            # debug
            print("Option C")

        # ------------------------------------------------------------------------------ #
        # Add selection functions to a dictionary

        options = {
            "A": lambda: option_A_select_visible_NURB_curves(visible_nurbs_transforms), 
            "B": lambda: option_B_select_visible_NURB_curves_and_locators(visible_nurbs_transforms, visible_locators_transforms),
            "C": lambda: option_C_select_visible_NURB_curves_and_keyed_locators(visible_nurbs_transforms, keyed_visible_locator_transforms)
        }

        # Run one of the option functions
        options[option]()