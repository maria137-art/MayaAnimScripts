"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_bake_to_worldspace.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# CREDIT: Richard Lico (for the workflow)
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Bake selected objects to worldspace translation and rotation.
# 
# INSTRUCTIONS:
# ---------------------------------------
# 
# Select objects you would like to bake to worldspace, and run the function in one of the three modes:
#   - "both"            :   Convert to both worldspace translation and rotation.
#   - "translation"     :   Convert to just worldspace translation.
#   - "rotation"        :   Convert to just worldspace rotation (locator will follow objects translation).
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

mr_bake_to_worldspace("both")
mr_bake_to_worldspace("translation")
mr_bake_to_worldspace("rotation")

# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# Richard Lico's "Space Switching for Animators" course on Animation Sherpa.
#
# WISH LIST:
# ---------------------------------------
#   - Give warning if selected object is already constrained.
#       - But still work for any axis that isn't constrained.
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-06-30 - 0001:
#   - First pass of workflow in Python, to bake all objects at once.
#   - Provide 3 options.
#
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def mr_bake_to_worldspace(constraint_mode=None):
    
    start_time = cmds.playbackOptions(q=True, min=True)
    end_time = cmds.playbackOptions(q=True, max=True)
    
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.confirmDialog(title="Confirm", message="You need to select something first")
        return
    
    locators = []
    constraints = []
    
    for item in selection:
        locator_name = item + "_temp_worldspace_locator"
        locators.append(locator_name)
        
        # Create a locator with the selected item's name with "_temp_worldspace_locator" appended
        locator = cmds.spaceLocator(n=locator_name)[0]
        
        # Set size of locator
        cmds.setAttr(locator + ".localScale", 18, 18, 18)
        
        # Do the constraints between selected item and new locator
        point_constraint = cmds.pointConstraint(item, locator)
        orient_constraint = cmds.orientConstraint(item, locator)
        
        constraints.append(point_constraint)
        constraints.append(orient_constraint)
    
    # Bake results for all locators
    cmds.refresh(suspend=True)
    cmds.bakeResults(
        locators,
        simulation=True,
        time=(start_time, end_time),
        sampleBy=1,
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        removeBakedAnimFromLayer=False,
        bakeOnOverrideLayer=False,
        minimizeRotation=True,
        controlPoints=False
    )
    cmds.delete(locators, sc=True)
    # Filter curves and delete constraints
    for constraint in constraints:
        cmds.filterCurve(constraint)
        cmds.delete(constraint)
    cmds.refresh(suspend=False)
    
    # Do the constraints back to the original items
    for i, item in enumerate(selection):
        locator = locators[i]
        
        if constraint_mode == "both":  
            cmds.pointConstraint(locator, item)
            cmds.orientConstraint(locator, item)
            
        if constraint_mode == "translation":  
            cmds.pointConstraint(locator, item)
            
        if constraint_mode == "rotation":
            cmds.pointConstraint(item, locator)
            cmds.orientConstraint(locator, item)

            # Lock attributes of offset group
            attrs += [".tx", ".ty", ".tz"]
            for attr in attrs:
                cmds.setAttr(locator, lock=True)
            
    cmds.select(locators)
