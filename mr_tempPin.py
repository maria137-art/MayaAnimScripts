"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_tempPin.py
# VERSION: 0011
#
# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# This script has two main functions:
#
#   single:
#       - Pin selected objects to a single worldspace locator.
#       - The locator will be at the objects' average positon and orientation.
#       - When the script runs again, its constrained objects are keyed on current frame, and temp locators get deleted.
#
#   multiple:
#       - Pin selected objects to a worldspace locator each.
#       - All new locators get parented under one null. Use it to pivot all objects at once.
#       - The null will be created at the objects average positon and orientation.
#       - When the script runs again, constrained objects are keyed on the current frame, and temp locators get deleted.
#
# The script has options to chose what type of constraints and pivot position is wanted.
#
# EXAMPLE USES:
# ---------------------------------------
# - Temporarily hold controls in place for on-frame adjustments.
#
# INSTRUCTIONS:
# ---------------------------------------
# To choose the type of constraints used, pick one of the three modes:
#   - "both" - constrain translate and rotate attributes
#   - "translate"
#   - "rotate"
#
# To choose where the pivot positon should be made when using the "multiple" function, use either:
#   - "average"
#   - "last_selected"
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------
import importlib
import mr_tempPin
importlib.reload(mr_tempPin)

# USE ONE OF THE FOLLOWING COMMANDS.
mr_tempPin.single("both")
mr_tempPin.single("translate")
mr_tempPin.single("rotate")

mr_tempPin.multiple("both", "average")
mr_tempPin.multiple("translate", "average")
mr_tempPin.multiple("rotate", "average")

mr_tempPin.multiple("both", "last_selected")
mr_tempPin.multiple("translate", "last_selected")
mr_tempPin.multiple("rotate", "last_selected")

# ---------------------------------------
# REQUIREMENTS: 
# ---------------------------------------
# Must have mr_find_constraint_targets_and_drivers.py in order to use mr_find_targets_of_selected()
#
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

import importlib
import mr_find_constraint_targets_and_drivers
importlib.reload(mr_find_constraint_targets_and_drivers)

##################################################################################################################################################

def single(mode=None):
    temp_pin = "TEMP_worldspace_locator"

    # -------------------------------------------------------------------
    # 00. CHECK IF THE USER'S COMMAND INPUTS ARE VALID.
    # -------------------------------------------------------------------
    if mode not in ["both", "translate", "rotate"]:
        cmds.warning("Please specify in the run command if the script should constrain only \"translate\" or \"rotate\", or \"both\".")
        return

    # -------------------------------------------------------------------
    # 00. CHECK IF TEMP PIN ALREADY EXISTS.
    # -------------------------------------------------------------------
    if cmds.objExists(temp_pin):
        key_targets(temp_pin)
        cmds.delete(temp_pin)

        # Refresh the viewport.
        # This helps when using the script to reposition objects on animation layers, while BaseAnimation is locked.
        current_time = cmds.currentTime(query=True)
        cmds.currentTime(current_time)

    # -------------------------------------------------------------------
    # 00. CREATE TEMP PIN FOR EACH SELECTED OBJECT.
    # -------------------------------------------------------------------
    else:
        sel = cmds.ls(selection=True)

        # Create a locator.
        loc = cmds.spaceLocator(name=temp_pin)[0]
        cmds.setAttr(loc + "Shape.localScaleX", 10)
        cmds.setAttr(loc + "Shape.localScaleY", 10)
        cmds.setAttr(loc + "Shape.localScaleZ", 10)

        match_average_position_of_objects(sel, loc)

        for item in sel:
            constrain_unlocked_attributes(loc, item, mode)
            lock_and_hide_same_attributes(loc, item, mode)

        # Set a blank keyframe, to remember the frame the loc was created on.
        cmds.setKeyframe(loc)
        cmds.select(loc)


##################################################################################################################################################

def multiple(mode=None, position=None):
    temp_pin_group = "TEMP_worldspace_locator_grp"

    # -------------------------------------------------------------------
    # 00. CHECK IF THE USER'S COMMAND INPUTS ARE VALID.
    # -------------------------------------------------------------------
    if mode not in ["both", "translate", "rotate"]:
        cmds.warning("Please specify in the run command if the script should constrain only \"translate\" or \"rotate\", or \"both\".")
        return
    if position not in ["average", "last_selected"]:
        cmds.warning("Please specify in the run command if the pivot position should be at \"average\" or \"last_selected\".")
        return

    # -------------------------------------------------------------------
    # 00. CHECK IF TEMP GROUP ALREADY EXISTS.
    # -------------------------------------------------------------------
    if cmds.objExists(temp_pin_group):
        children = cmds.listRelatives(temp_pin_group, children=True)
        key_targets(children)
        cmds.delete(temp_pin_group)

    # -------------------------------------------------------------------
    # 00. CREATE TEMP PIN FOR EACH SELECTED OBJECT.
    # -------------------------------------------------------------------
    else:
        sel = cmds.ls(selection=True)

        # If nothing is selected,
        if not sel:
            # reminds user to select something.
            # Make sure title is unique, otherwise dialog won't trigger.
            cmds.warning("Select objects to pin.")

        else:
            # Create a group.
            cmds.group(empty=True, name=temp_pin_group)

            if position == "average":
                match_average_position_of_objects(sel, temp_pin_group)
            if position == "last_selected":
                match_position_of_object(sel[-1], temp_pin_group)

            for item in sel:
                # Create a locator.
                loc = cmds.spaceLocator(name=("TEMP_worldspace_" + item + "_loc"))[0]
                cmds.setAttr(loc + "Shape.localScaleX", 10)
                cmds.setAttr(loc + "Shape.localScaleY", 10)
                cmds.setAttr(loc + "Shape.localScaleZ", 10)

                # Position and orient it at its target.
                cmds.pointConstraint(item, loc)
                cmds.orientConstraint(item, loc)
                cmds.delete(loc, constraints=True)

                # Parent into temp_pin_group.
                cmds.parent(loc, temp_pin_group)

                constrain_unlocked_attributes(loc, item, mode)
                lock_and_hide_same_attributes(loc, item, mode)

            # Set a blank keyframe, to remember the frame the temp_pin_group was created on.
            cmds.setKeyframe(temp_pin_group)
            cmds.select(temp_pin_group)

            # End with rotate manipulator active.
            mel.eval("buildRotateMM ;")
            mel.eval("destroySTRSMarkingMenu RotateTool ;")

##################################################################################################################################################

########################################################################
#                                                                      #
#                         SUPPORTING FUNCTIONS                         #
#                                                                      #
########################################################################

# Place the target at the average position and orientation of source objects.
def match_average_position_of_objects(sources, target):
    constraints = []
    for item in sources:
        point_constraint = cmds.pointConstraint(item, target)
        orient_constraint = cmds.orientConstraint(item, target)

        constraints.extend(point_constraint)
        constraints.extend(orient_constraint)
    # Delete with variables instead of cmds.delete(constraints=True), because if the target it a null, it gets deleted when constraints are removed.
    cmds.delete(constraints)

##################################################################################################################################################

# Place the target at the average position and orientation of source objects.
def match_position_of_object(source, target):
    constraints = []

    point_constraint = cmds.pointConstraint(source, target)
    orient_constraint = cmds.orientConstraint(source, target)

    constraints.extend(point_constraint)
    constraints.extend(orient_constraint)
    # Delete with variables instead of cmds.delete(constraints=True), because if the target it a null, it gets deleted when constraints are removed.
    cmds.delete(constraints)


##################################################################################################################################################

def key_targets(drivers):
    cmds.select(drivers)
    mr_find_constraint_targets_and_drivers.mr_find_targets_of_selected()
    mel.eval("SetKeyTranslate;")
    mel.eval("SetKeyRotate;")

##################################################################################################################################################

# Lock and hide attributes on the locator if corresponding ones on the target are locked.
def lock_and_hide_same_attributes(source, target, mode):
    main_attributes_to_lock_hide = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
    extra_attributes_to_lock_hide = ["scaleX", "scaleY", "scaleZ", "visibility"]

    def lock_hide_attribute(source, attr):
        source_attr = source + "." + attr
        cmds.setAttr(source_attr, keyable=False)
        cmds.setAttr(source_attr, lock=True)

    # Hide attributes on target that are locked and / or unkeyable on source. 
    for attr in main_attributes_to_lock_hide:
        target_attr = target + "." + attr

        target_lock = cmds.getAttr(target_attr, lock=True)
        target_keyable = cmds.getAttr(target_attr, keyable=True)

        if target_lock or not target_keyable:
            lock_hide_attribute(source, attr)

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

def constrain_unlocked_attributes(driver, target, mode):
    if mode == "both":
        constrain_unlocked_translates(driver, target)
        constrain_unlocked_rotates(driver, target)

    elif mode == "translate":
        constrain_unlocked_translates(driver, target)

    elif mode == "rotate":
        constrain_unlocked_rotates(driver, target)

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

    if skip_trans_axes:
        if skip_trans_axes == ['x', 'y', 'z']:
            return
        else:
            # Apply point constraint with skipping specified axes
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

    if skip_rot_axes:
        if skip_rot_axes == ['x', 'y', 'z']:
            return
        else:
            # Apply orient constraint with skipping specified axes
            cmds.orientConstraint(driver, item, maintainOffset=True, weight=1, skip=skip_rot_axes)
    else:
        cmds.orientConstraint(driver, item, maintainOffset=True, weight=1)


"""
##################################################################################################################################################
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-18 - 0011:
#   - Refresh viewport after deleting tempPin, to reflect changes on animation layers while BaseAnimation is locked.
#   - Moved changlog to the bottom.
#
# 2024-01-14 - 0010:
#   - End multiple() with rotate manipulator active.
#
# 2023-12-28 - 0009:
#   - Adding check for valid command inputs + option to choose where pivot position is for the "multiple" function.
#
# 2023-12-28 - 0008:
#   - Updating script to not point/orient constraint at all if those attributes are all locked.
#
# 2023-12-09 - 0007:
#   - Forgot to update single() function, after making lock_and_hide_same_attributes() and constrain_unlocked_attributes() work for one object at a time.
#
# 2023-12-09 - 0006:
#   - Fixing the multiple() function to respect locked attributes better.
#
# 2023-12-07 - 0005:
#   - Converting and mergnig MEL script "mr_tempPin_createIndividualPins.mel" here.
#
# 2023-12-04 - 0004: 
#   - Converted original MEL script to Python.
#
# 2023-06-28 - 0003:
#   - Updated script to use Python function to find constraint targets.
#
# 0002: Added catch command, to stop script from failing if any translation or rotation attributes are locked.
# ---------------------------------------
##################################################################################################################################################
"""