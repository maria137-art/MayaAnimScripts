"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_bakeToWorldspace.py
# VERSION: 0007
#
# CREATORS: Maria Robertson
# CREDIT: Richard Lico (for workflow)
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Bake selected objects to worldspace translation and rotation.
# Also bake follow locators. 
#
# INSTRUCTIONS:
# ---------------------------------------
# Select objects you would like to bake to worldspace, and run the function in one of the three modes:
#   - "both"          :   Convert to both worldspace translation and rotation.
#   - "translate"     :   Convert to just worldspace translation.
#   - "rotate"        :   Convert to just worldspace rotation (locator will follow objects translation).
#
#
# EXAMPLE USES:
# On a shelf button, single-click to create a worldspace locator constraint. Double-click to just create a follow locator.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_bakeToWorldspace
importlib.reload(mr_bakeToWorldspace)

# USE ONE OF THE FOLLOWING COMMANDS:

# Use these for the default settings.
mr_bakeToWorldspace.main("both")
mr_bakeToWorldspace.main("translate")
mr_bakeToWorldspace.main("rotate")

# Slower version for baking dynamic objects:
mr_bakeToWorldspace.main(mode="both", constrain=True, simulate_bake=True)
mr_bakeToWorldspace.main(mode="both", constrain=True, simulate_bake=True)
mr_bakeToWorldspace.main(mode="both", constrain=True, simulate_bake=True)

# To create locators without constraining anything to them:
# Faster version:
mr_bakeToWorldspace.main(mode="both", constrain=False, simulate_bake=False)
mr_bakeToWorldspace.main(mode="both", constrain=False, simulate_bake=False)
mr_bakeToWorldspace.main(mode="both", constrain=False, simulate_bake=False)

# Slower version for baking dynamic objects:
mr_bakeToWorldspace.main(mode="both", constrain=False, simulate_bake=True)
mr_bakeToWorldspace.main(mode="both", constrain=False, simulate_bake=True)
mr_bakeToWorldspace.main(mode="both", constrain=False, simulate_bake=True)


# ---------------------------------------
# REQUIREMENTS:
# ---------------------------------------
# The mr_utilities.py file, for support functions:
# https://github.com/maria137-art/MayaAnimScripts/blob/main/mr_utilities.py
#
# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# Richard Lico's "Space Switching for Animators" course on Animation Sherpa.
#
# WISH LIST:
# ---------------------------------------
#   - Give warning if selected object has its relevant attributes constrained.
#
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

import importlib
import mr_utilities
importlib.reload(mr_utilities)

def main(mode=None, constrain=True, simulate_bake=False):
    # -------------------------------------------------------------------
    # 01. DEFINE TIMESLIDER RANGE.
    # -------------------------------------------------------------------
    start_time = cmds.playbackOptions(query=True, min=True)
    end_time = cmds.playbackOptions(query=True, max=True)
    
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.confirmDialog(title="Confirm", message="You need to select something first")
        return
    
    locators = []
    constraints = []

    # Store the lock state of the BaseAnimation animation layer.
    if cmds.objExists("BaseAnimation"):
        is_baseAnimation_locked = cmds.getAttr("BaseAnimation" + ".lock")  

        if is_baseAnimation_locked:
            cmds.animLayer("BaseAnimation", edit=True, lock=False)

    # -------------------------------------------------------------------
    # 01. CREATE A LOCATOR PER OBJECT.
    # -------------------------------------------------------------------
    for item in selection:
        locator_name = item + "_temp_worldspace_locator"
        locators.append(locator_name)
        
        locator = cmds.spaceLocator(name=locator_name)[0]
        cmds.setAttr(locator + ".localScale", 18, 18, 18)
        
        point_constraint = cmds.pointConstraint(item, locator)
        orient_constraint = cmds.orientConstraint(item, locator)
        
        constraints.append(point_constraint)
        constraints.append(orient_constraint)
 
    # -------------------------------------------------------------------
    # 01. SELECT OBJECTS THAT ONLY HAVE KEYFRAMES.
    # -------------------------------------------------------------------
    cmds.refresh(suspend=True)

    attributes = ["translateX", "translateY", "translateZ","rotateX", "rotateY", "rotateZ"]

    cmds.bakeResults(
        locators,
        attribute = attributes,
        simulation=simulate_bake,
        time=(start_time, end_time),
        sampleBy=1,
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        minimizeRotation=True
    )
    # Delete static channels.
    cmds.delete(locators, sc=True)
    
    # Filter curves and delete constraints.
    for constraint in constraints:
        cmds.filterCurve(constraint)
        cmds.delete(constraint)
    cmds.refresh(suspend=False)

    if constrain == True:   
        # -------------------------------------------------------------------
        # 01. REVERSE CONSTRAINTS
        # -------------------------------------------------------------------
        for i, item in enumerate(selection):
            locator = locators[i]
            if mode == "both":
                mr_utilities.constrain_unlocked_translates(locator, item)
                mr_utilities.constrain_unlocked_rotates(locator, item)

            if mode == "translate":  
                mr_utilities.constrain_unlocked_translates(locator, item)

                # End with the Translate manipulator on.
                mel.eval("buildTranslateMM ;")
                mel.eval("destroySTRSMarkingMenu MoveTool ;")

            if mode == "rotate":
                mr_utilities.constrain_unlocked_rotates(locator, item)
                cmds.pointConstraint(item, locator)

                # End with Rotate manipulator active.
                mel.eval("buildRotateMM ;")
                mel.eval("destroySTRSMarkingMenu RotateTool ;")

            # Lock and hide attributes on the locator if corresponding ones on the target are locked.
            mr_utilities.set_corresponding_attribute_states(locator, item, mode, keyable=False, lock=True)

    # End with the locators selected.
    cmds.select(locators)

    # Restore original lock state of BaseAnimation.
    if cmds.objExists("BaseAnimation"):
        if is_baseAnimation_locked:
            cmds.animLayer("BaseAnimation", edit=True, lock=True)
            

"""
##################################################################################################################################################
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-20- 0007:
#   - Checking if the BaseAnimation animation layer is locked before running tool, to avoid potential bugs.
#   - Moving changelog to the bottom.
#   - Moving support functions to mr_utilities.py.
#       - Renaming lock_and_hide_corresponding_attributes() inside it, to set_corresponding_attribute_states().
#
# 2023-12-28 - 0006:
#   - Adding option to just bake a worldspace locator, without reversing constraints.
#   - Adding option to bake with or without simulation, depending on needing to bake fast vs baking physics.
#
# 2023-12-17 - 0005:
#   - End script with relevant manipulators active.
#
# 2023-12-06 - 0004:
#   - Fixed lock_and_hide_corresponding_attributes to lock and hide attributes on multiple objects.
#
# 2023-12-06 - 0003:
#   - Adding functions to hide and ignore locked and unkeyable attributes on targests, avoiding errors.
#
# 2023-07-10 - 0002:
#   - Fixing issue with locking constrained attributes.
#
# 2023-06-30 - 0001:
#   - First pass of workflow in Python, to bake all objects at once.
#   - Provide 3 options.
# ---------------------------------------
##################################################################################################################################################
"""