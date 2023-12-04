"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_tempPin.py
# VERSION: 0004
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# - Pin selected object/s to a single temp locator, to be moved in worldspace.
# - When script runs again, constrained objects are keyed on current frame, and temp pin deleted.
#
# EXAMPLE USES:
# ---------------------------------------
# - Temporarily hold controls in place for on-frame adjustments.
#
# INSTRUCTIONS:
# ---------------------------------------
# Run the following command with one of the three modes:
#   - "both" - constrain translate and rotate attributes
#   - "translate"
#   - "rotate" 
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_tempPin
importlib.reload(mr_tempPin)

mr_tempPin.mr_tempPin("both")
mr_tempPin.mr_tempPin("translate")
mr_tempPin.mr_tempPin("rotate")


# ---------------------------------------
# REQUIREMENTS: 
# ---------------------------------------
# Must have mr_find_constraint_targets_and_drivers.py in order to use mr_find_targets_of_selected()
# 
# WISH LIST:
# ---------------------------------------
# - Work with Animation Layers.
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-04: 0004: 
# - Converted original MEL script to Python.
#
# 2023-06-28 - 0003:
# - Updated script to use Python function to find constraint targets.
#
# 0002: Added catch command, to stop script from failing if any translation or rotation attributes are locked.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

import importlib
import mr_find_constraint_targets_and_drivers
importlib.reload(mr_find_constraint_targets_and_drivers)


def mr_tempPin(mode=None):
    temp_pin_loc = "TEMP_worldspace_locator"

    if cmds.objExists(temp_pin_loc):
        cmds.select(temp_pin_loc)

        mr_find_constraint_targets_and_drivers.mr_find_targets_of_selected()

        mel.eval("SetKeyTranslate;")
        mel.eval("SetKeyRotate;")

        cmds.delete(temp_pin_loc)

    else:
        sel = cmds.ls(selection=True)

        # Create a locator.
        loc = cmds.spaceLocator(name=temp_pin_loc)[0]
        cmds.setAttr(loc + "Shape.localScaleX", 10)
        cmds.setAttr(loc + "Shape.localScaleY", 10)
        cmds.setAttr(loc + "Shape.localScaleZ", 10)

        # Place the locator at the average position and orientation between selected objects.
        for item in sel:
            cmds.pointConstraint(item, loc)
            cmds.orientConstraint(item, loc)
        cmds.delete(loc, constraints=True)

        for item in sel:
            if mode == "both":
                constrain_unlocked_translates(loc, item)
                constrain_unlocked_rotates(loc, item)

            elif mode == "translate":
                constrain_unlocked_translates(loc, item)

            elif mode == "rotate":
                constrain_unlocked_rotates(loc, item)

        # Lock and hide attributes on the locator if corresponding ones on the target are locked
        lock_and_hide_corresponding_attributes(loc, sel, mode)

        cmds.select(loc)

##################################################################################################################################################

########################################################################
#                                                                      #
#                         SUPPORTING FUNCTIONS                         #
#                                                                      #
########################################################################

def lock_and_hide_corresponding_attributes(source, target, mode):
    main_attributes_to_lock_hide = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
    extra_attributes_to_lock_hide = ["scaleX", "scaleY", "scaleZ", "visibility"]

    # Hide attributes on target that are locked and / or unkeyable on source. 
    for attr in main_attributes_to_lock_hide:
        source_attr = source + "." + attr
        for target_obj in target:
            target_attr = target_obj + "." + attr

            target_lock = cmds.getAttr(target_attr, lock=True)
            target_keyable = cmds.getAttr(target_attr, keyable=True)

            if target_lock or not target_keyable:
                cmds.setAttr(source_attr, keyable=False)
                cmds.setAttr(source_attr, lock=True)


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