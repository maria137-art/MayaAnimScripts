"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_bakeToWorldspace.py
# VERSION: 0005
#
# CREATORS: Maria Robertson
# CREDIT: Richard Lico (for workflow)
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
#   - "translate"     :   Convert to just worldspace translation.
#   - "rotate"        :   Convert to just worldspace rotation (locator will follow objects translation).
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
# 2023-12-28 - 0006:
# - Adding option to just bake a worldspace locator, without reversing constraints.
# - Adding option to bake with or without simulation, depending on needing to bake fast vs baking physics.
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
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

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
                constrain_unlocked_translates(locator, item)
                constrain_unlocked_rotates(locator, item)

            if mode == "translate":  
                constrain_unlocked_translates(locator, item)

                # End with the Translate manipulator on.
                mel.eval("buildTranslateMM ;")
                mel.eval("destroySTRSMarkingMenu MoveTool ;")

            if mode == "rotate":
                constrain_unlocked_rotates(locator, item)
                cmds.pointConstraint(item, locator)

                # End with Rotate manipulator active.
                mel.eval("buildRotateMM ;")
                mel.eval("destroySTRSMarkingMenu RotateTool ;")

            # Lock and hide attributes on the locator if corresponding ones on the target are locked.
            lock_and_hide_corresponding_attributes(locator, item, mode)

    # End with the locators selected.
    cmds.select(locators)

##################################################################################################################################################

########################################################################
#                                                                      #
#                         SUPPORTING FUNCTIONS                         #
#                                                                      #
########################################################################

def lock_and_hide_corresponding_attributes(source, target, mode):
    main_attributes_to_lock_hide = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
    extra_attributes_to_lock_hide = ["scaleX", "scaleY", "scaleZ", "visibility"]

    for attr in main_attributes_to_lock_hide:
        source_attr = source + "." + attr

        target_attr = target + "." + attr
        target_lock = cmds.getAttr(target_attr, lock=True)
        target_keyable = cmds.getAttr(target_attr, keyable=True)

        if target_lock or not target_keyable:
            cmds.setAttr(source_attr, keyable=False)

    def lock_hide_attribute(source, attr):
        source_attr = source + "." + attr
        cmds.setAttr(source_attr, keyable=False)
        cmds.setAttr(source_attr, lock=True)

    for attr in extra_attributes_to_lock_hide:
        lock_hide_attribute(source, attr)

    if mode == "translate":
        rotation_attributes = ["rotateX", "rotateY", "rotateZ"]
        for attr in rotation_attributes:
            lock_hide_attribute(source, attr)

    elif mode == "rotate":
        translation_attributes = ["translateX", "translateY", "translateZ"]
        for attr in translation_attributes:
            lock_hide_attribute(source, attr)

##################################################################################################################################################
    
def constrain_unlocked_translates(driver, item):
    # Check if translate X, Y, Z are locked
    skip_trans_axes = []
    if cmds.getAttr(item + ".translateX", lock=True):
        skip_trans_axes.append("x")
    if cmds.getAttr(item + ".translateY", lock=True):
        skip_trans_axes.append("y")
    if cmds.getAttr(item + ".translateZ", lock=True):
        skip_trans_axes.append("z")

    # Apply point constraint with skipping specified axes
    if skip_trans_axes:
        cmds.pointConstraint(driver, item, maintainOffset=True, weight=1, skip=skip_trans_axes)
    else:
        cmds.pointConstraint(driver, item, maintainOffset=True, weight=1)

##################################################################################################################################################

def constrain_unlocked_rotates(driver, item):
    # Check if rotate X, Y, Z are locked
    skip_rot_axes = []
    if cmds.getAttr(item + ".rotateX", lock=True):
        skip_rot_axes.append("x")
    if cmds.getAttr(item + ".rotateY", lock=True):
        skip_rot_axes.append("y")
    if cmds.getAttr(item + ".rotateZ", lock=True):
        skip_rot_axes.append("z")

    # Apply orient constraint with skipping specified axes
    if skip_rot_axes:
        cmds.orientConstraint(driver, item, maintainOffset=True, weight=1, skip=skip_rot_axes)
    else:
        cmds.orientConstraint(driver, item, maintainOffset=True, weight=1)