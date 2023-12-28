"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_pivot_worldspace.py
# VERSION: 0004
#
# CREATORS: Maria Robertson 
# CREDIT: Daniel Fotheringham
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Based on Daniel Fotheringham's demo: https://youtu.be/MjYXR0Ts1sE?t=3087 at [51:27 - 54:00]
#
# Bake objects in the parent space of a worldspace pivot.
# Makes it easier to clean curves when travelling in different directions.
#
# e.g. if a character travels diagonally in a straight line, the movement is represented in trans x and z axis.
# But if baked inside a pivot pointing in the same direction, it will be represented by just trans z.
#
# ---------------------------------------
# INSTRUCTIONS:
# ---------------------------------------
# This scripts works differently depending when it is run and what is selected at the time. It has 3 phases.
#
# PHASE 1 - CREATE THE PIVOT:
#     If it doesn't already exist, create a locator to be the pivot.
#          - If nothing is selected, the pivot will be created at origin.
#          - If one or more objects are selected, the pivot will be created at the average position and orientation that
#            the object/s are travelling in, between the current and next frame.
#
# PHASE 2 - SELECT OBJECTS TO BE PIVOTED:
#     If TEMP_PIVOT_loc exists with no children, create baked offset locators inside the pivot
#     for each selected object.
#     
#     Position TEMP_PIVOT_loc as wanted.
#
# PHASE 3 - BAKE EVERYTHING CONNECTED TO THE PIVOT:
#     If TEMP_PIVOT_loc contains children, bake the originally selected objects to offset, and delete the pivot.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

import importlib
import mr_pivot_worldspace
importlib.reload(mr_pivot_worldspace)

# USE ONE OF THE FOLLOWING COMMANDS:
mr_pivot_worldspace.main("all")
mr_pivot_worldspace.main("current_frame")

# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# Why current time didn't work - https:#forums.cgsociety.org/t/using-getattr-t-to-do-time-delay/805166/2
# 
# WISH LIST:
# ---------------------------------------
# - Save control keys + tangents, and apply it to the bake
# - Delete redundant keys
# - Bake everything into the new pivot at once, rather one at a time
# 
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-28 - 0004:
# - Adjusting check for valid run command inputs.
#
# 2023-12-09 - 0003:
# - Adding new functions to skip constraining locked attributes.
# - Locators have irrelevant attributes hidden.
#
# 2023-12-09 - 0002:
# - Added option to bake temp_pivots for just the current frame or the whole playback range.
#
# 2023-12-09 - 0001:
# - Converting mr_pivot_worldspacePivot.mel to Python
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.mel as mel

import importlib
import mr_find_constraint_targets_and_drivers
importlib.reload(mr_find_constraint_targets_and_drivers)


def main(bake_range=None):
    # -------------------------------------------------------------------
    # 01. CHECK IF bake_range IS CORRECT.
    # -------------------------------------------------------------------
    if bake_range not in ["current_frame", "all"]:
        cmds.warning("Please specify in the run command if the script should run on only the \"current_frame\" or \"all\" of the playback range.")
        return

    # -------------------------------------------------------------------
    # 01. INITIALIZE VARIABLES.
    # -------------------------------------------------------------------
    sel = cmds.ls(selection=True)
    temp_pivot = "TEMP_PIVOT_loc"
    pivot_locators = []

    startTime = cmds.playbackOptions(query=True, min=True)
    endTime = cmds.playbackOptions(query=True, max=True)

    # -------------------------------------------------------------------
    # 01. IF temp_pivot ALREADY EXISTS.
    # -------------------------------------------------------------------
    if cmds.objExists(temp_pivot):

        pivot_children = cmds.listRelatives(temp_pivot, children=True, type="transform")
        # -------------------------------------------------------------------
        # 02. IF temp_pivot HAS CHILDREN, BAKE THE ORIGINAL TARGETS AND DELETE PIVOT.
        # -------------------------------------------------------------------
        if pivot_children:
            cmds.select(pivot_children)
            mr_find_constraint_targets_and_drivers.mr_find_targets_of_selected()

            if bake_range == "current_frame":
                bake_current_frame(pivot_children)
            elif bake_range == "all":
                bake_and_delete_constraints(startTime, endTime)

            cmds.delete(temp_pivot)

        # -------------------------------------------------------------------
        # 02. IF temp_pivot HAS NO CHILDREN, CREATE PIVOT LOCATORS.
        # -------------------------------------------------------------------
        else:
            # -------------------------------------------------------------------
            # 03. WARN IF NOTHING IS SELECTED.
            # -------------------------------------------------------------------
            if not sel:
                cmds.warning("Select objects to pivot.")
                return

            # -------------------------------------------------------------------
            # 03. WARN IF temp_pivot IS SELECTED.
            # -------------------------------------------------------------------
            if temp_pivot in sel:
                # stop the script.
                cmds.warning("Select objects to pivot.")
                return

            # -------------------------------------------------------------------
            # 03. SET-UP OFFSET LOCATORS
            # -------------------------------------------------------------------
            for item in sel:
                # Create a locator.
                loc = cmds.spaceLocator(name=f"{item}_pivot_loc")[0]
                cmds.setAttr(loc + ".localScaleX", 18)
                cmds.setAttr(loc + ".localScaleY", 18)
                cmds.setAttr(loc + ".localScaleZ", 18)

                pivot_locators.append(loc)

                # Hide irrelevant attributes.
                attributes_to_lock_hide = ["scaleX", "scaleY", "scaleZ", "visibility"]
                for attr in attributes_to_lock_hide:
                    lock_hide_attribute(loc, attr)

                # Match the position and orientation of the locator to temp_pivot.
                cmds.pointConstraint(temp_pivot, loc)
                cmds.orientConstraint(temp_pivot, loc)
                cmds.delete(loc, constraints=True)

                # Constrain controls to the offset locators.
                cmds.pointConstraint(item, loc)
                cmds.orientConstraint(item, loc, maintainOffset=True)

                # Place offset locator inside temp pivot.
                cmds.parent(loc, temp_pivot)

            # -------------------------------------------------------------------
            # 03. BAKE OFFSET LOCATORS
            # -------------------------------------------------------------------
            cmds.select(pivot_locators)
            if bake_range == "current_frame":
                bake_current_frame(pivot_locators)
            elif bake_range == "all":
                bake_and_delete_constraints(startTime, endTime)

            """
            # Constrain controls to baked offset locators.
            for i in range(len(pivot_locators)):
                cmds.pointConstraint(pivot_locators[i], sel[i])
                cmds.orientConstraint(pivot_locators[i], sel[i], mo=True)
            """
            # Constrain controls to baked offset locators.
            for i in range(len(pivot_locators)):
                constrain_unlocked_translates(pivot_locators[i], sel[i])
                constrain_unlocked_rotates(pivot_locators[i], sel[i])   

            cmds.select(temp_pivot)

    # -------------------------------------------------------------------
    # 01. IF temp_pivot DOES NOT EXIST.
    # -------------------------------------------------------------------
    else:
        # -------------------------------------------------------------------
        # 02. IF ONE OR MORE OBJECTS ARE SELECTED.
        # -------------------------------------------------------------------
        if sel:
            # Create a variable from the last item selected.
            cmds.select(sel)
            last_in_selected = cmds.ls(selection=True, tail=1)[0]

            # Create locator.
            temp_pivot = cmds.spaceLocator(name=temp_pivot)[0]
            cmds.setAttr(f"{temp_pivot}.localScaleZ", 100)
            cmds.setAttr(f"{temp_pivot}.localScaleX", 100)
            cmds.setAttr(f"{temp_pivot}.localScaleY", 100)

            # Average position and rotation of temp_pivot between selected.
            for item in sel:
                cmds.pointConstraint(item, temp_pivot)
                cmds.orientConstraint(item, temp_pivot)

            # Declare time.
            current_frame = cmds.currentTime(q=True)
            next_frame = current_frame + 1

            # -------------------------------------------------------------------
            # 03. AIM PIVOT LOCATOR IN DIRECTION OF MOVEMENT, BASED ON CURRENT FRAME
            # -------------------------------------------------------------------
            # Research for using vector data: 
            # https://forums.cgsociety.org/t/find-position-between-2-points/1286034/4
            # Research on error "An array expression element must be a scalar value"
            # https://forums.cgsociety.org/t/n-array-expression-element-must-be-a-scalar-value/1203879

            # Get coordinates of worldspace locator attached to object.
            a1 = cmds.getAttr(temp_pivot + ".translateX", time=current_frame)
            a2 = cmds.getAttr(temp_pivot + ".translateY", time=current_frame)
            a3 = cmds.getAttr(temp_pivot + ".translateZ", time=current_frame)

            b1 = cmds.getAttr(temp_pivot + ".translateX", time=next_frame)
            b2 = cmds.getAttr(temp_pivot + ".translateY", time=next_frame)
            b3 = cmds.getAttr(temp_pivot + ".translateZ", time=next_frame)

            cmds.delete(temp_pivot, constraints=True)

            # Convert to MVector.
            v1 = om.MVector(a1, a2, a3)
            v2 = om.MVector(b1, b2, b3)

            # Calculate direction vector.
            d = v1 - v2

            # Normalise.
            normalized_d = d.normal()

            # Convert back to float.
            new_p = [normalized_d.x, normalized_d.y, normalized_d.z]

            # Aim based on World Up Vector on next frame.
            cmds.currentTime(next_frame)

            cmds.aimConstraint(
                last_in_selected,
                temp_pivot,
                aimVector=(1, 0, 0),
                upVector=(0, 1, 0),
                worldUpType="vector",
                worldUpVector=new_p
            )
            cmds.delete(temp_pivot, constraints=True)
            cmds.currentTime(current_frame)

            cmds.select(sel)
            print("Run mr_changeWorldspacePivot again when ready, to bake selected objects under the pivot.\n")

        # -------------------------------------------------------------------
        # 03. IF NOTHING IS SELECTED.
        # -------------------------------------------------------------------
        else:
            # Create a temp_pivot.
            cmds.warning("No temp pivot locator exists. Creating one now.")
            loc = cmds.spaceLocator(name=temp_pivot)[0]

            # Set locator scale.
            cmds.setAttr(loc + ".localScaleZ", 100)
            cmds.setAttr(loc + ".localScaleX", 100)
            cmds.setAttr(loc + ".localScaleY", 100)

            cmds.select(loc)

##################################################################################################################################################

########################################################################
#                                                                      #
#                         SUPPORTING FUNCTIONS                         #
#                                                                      #
########################################################################

def bake_and_delete_constraints(startTime, endTime):
    cmds.refresh(suspend=True)

    cmds.bakeResults(
        simulation=True,
        time=(startTime, endTime),
        sampleBy=1,
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        removeBakedAnimFromLayer=False,
        bakeOnOverrideLayer=False
    )

    cmds.delete(staticChannels=True)
    cmds.filterCurve()
    cmds.delete(constraints=True)
    cmds.refresh(suspend=False)

##################################################################################################################################################

def bake_current_frame(objects_to_bake):
    # Set key on just current range.
    mel.eval("SetKeyTranslate")
    mel.eval("SetKeyRotate")

    cmds.delete(staticChannels=True)
    cmds.filterCurve()
    cmds.delete(objects_to_bake, constraints=True)

##################################################################################################################################################

def lock_hide_attribute(source, attr):
    source_attr = source + "." + attr
    cmds.setAttr(source_attr, keyable=False)
    cmds.setAttr(source_attr, lock=True)

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