import maya.cmds as cmds

"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_select_visibleNURBCurves.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# DESCRIPTION: 
# Select all visible NURB curves in the current panel.
#
# EXAMPLE USES:
# Useful when extra or unneccessary control are hidden, so you can quickly grab main ones to key.
# 
# Example hotkeys to assign to:
#   ALT + A
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------

import importlib

import mr_select_visibleNURBCurves
importlib.reload(mr_select_visibleNURBCurves)

mr_select_visibleNURBCurves.mr_select_visibleNURBCurves()

# ------------------------------------------------------------------------------ #
"""

def mr_select_visibleNURBCurves():

    # get the current panel
    panel = cmds.getPanel(withFocus=True)

    # check if the current panel is a modelPanel
    if cmds.getPanel(typeOf=panel) != "modelPanel":
        print("The current panel is not a 3D view panel.")
    
    else: 
        visible_nurbs_curves = []

        # for every NURBS curve that exists
        for curve in cmds.ls(type="nurbsCurve", visible=True, long=True):
            
            # check if it is visible in the current panel
            if cmds.modelEditor(panel, query=True, nurbsCurves=True):

                visible_nurbs_curves.append(curve)

        # get the transform nodes of all visible NURBS curves in the scene
        visible_nurbs_transforms = []

        for curve in visible_nurbs_curves:
            visible_nurbs_transforms.append(cmds.listRelatives(curve, parent=True)[0])

        # select the transform nodes of all visible NURBS curves in the current panel
        if visible_nurbs_transforms:
            cmds.select(visible_nurbs_transforms)

        """
        else:
            print("No visible NURBS curves in current panel.")
        """


def mr_select_visibleNURBCurves_and_keyedVisibleLocators():

    # get the current panel
    panel = cmds.getPanel(withFocus=True)

    # check if the current panel is a modelPanel
    if cmds.getPanel(typeOf=panel) != "modelPanel":
        print("The current panel is not a 3D view panel.")
    
    else: 
        visible_nurbs_curves = []
        visible_locators = []
              
        visible_nurbs_transforms = []
        visible_locators_transforms = []
        
        keyed_visible_locator_transforms = []
        
        # for every NURBS curve that exists, check if its visible in the current panel
        for curve in cmds.ls(type="nurbsCurve", visible=True, long=True):
            if cmds.modelEditor(panel, query=True, nurbsCurves=True):
                visible_nurbs_curves.append(curve)
        
        # for every locator, check if it's visible in the current panel
        for locator in cmds.ls(type="locator", visible=True, long=True):
            if cmds.modelEditor(panel, query=True, locators=True):
                visible_locators.append(locator)        
     
        # list the transform nodes
        for curve in visible_nurbs_curves:
            visible_nurbs_transforms.append(cmds.listRelatives(curve, parent=True)[0])  
              
        for loc in visible_locators:
            visible_locators_transforms.append(cmds.listRelatives(loc, parent=True)[0])            


        # Iterate through each locator
        for loc in visible_locators_transforms:

            # Get a list of all the keyable and visible attributes in the transform node
            attributes = cmds.listAttr(loc, keyable=True, visible=True, unlocked=True)
        
            # Check if any of the attributes have set keys
            for attr in attributes:
                if cmds.keyframe(loc, q=True, at=attr):
                    keyed_visible_locator_transforms.append(loc)  
                    break

        # select the transform nodes of all visible NURBS curves in the current panel
        if visible_nurbs_transforms:
            cmds.select(visible_nurbs_transforms)
            
        if keyed_visible_locator_transforms:
            cmds.select(keyed_visible_locator_transforms, add=True)        

        """
        else:
            print("No visible NURBS curves or keyed locators in current panel.")
        """