"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_createNullOffset.py
# VERSION: 0005
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Place each selected object into its own offset group, under their original parent.
# The Offset group will match the selected object's translation and rotation, to zero out their values.
#
# EXAMPLE USES:
# ---------------------------------------
# Can be helpful when modifying rigs.
# Can't be used with referenced rigs.
#
# INSTRUCTIONS:
# ---------------------------------------
# It's best to run this on the original bind pose of the rig.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

import importlib
import mr_createNullOffset
importlib.reload(mr_createNullOffset)

mr_createNullOffset.mr_createNullOffset_static()
OR
mr_createNullOffset.mr_createNullOffset_keyed()

# ---------------------------------------
# REQUIREMENTS: 
# ---------------------------------------
# mr_bake_to_worldspace.py
# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# For listing relatives: https://forums.cgsociety.org/t/list-all-parents-of-an-object-mel/1806687/2
# 
# The endsWith command: https://help.autodesk.com/cloudhelp/2016/CHS/Maya-LT-Tech-Docs/Commands/endsWith.html
# Learnt it because of this post: https://forums.autodesk.com/t5/maya-programming/selecting-all-polygon-objects-in-the-scene-with-a-certain-prefix/td-p/4240087
#
# ---------------------------------------
# WISHLIST:
# ---------------------------------------
# - Combine the two functions, to avoid repeated logic.
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-07-19 - 0005:
#   - Adding comments to script to make rereading easier.
#   - Made bakeResults bake on both translate and rotate attributes, for mr_createNullOffset_keyed()
#         Decided to have it, while experimenting with Aim Space scripts.
#
# 2023-06-29 - 0004:
#   - For mr_createNullOffset_keyed, added function to set all transform keys on original selection to default values, keeping the original key timings.
#   - Added mr_find_drivers_of_selected and baking for mr_createNullOffset_static to remove temp worldspace locators.
#   - Made bakeResults only bake on translate attributes.
#
# 2023-06-29 - 0003:
#   - Converted to Python
#   - If a selected object has keyframes, bake the null group to match the translation
#
# 2022-12-17 - 0002:
#   - Added checks for if selected object is already in an offset group.
#
# 2022-12-16 - 0001:
#   - First pass of MEL version of script.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import importlib

import mr_bake_to_worldspace
importlib.reload(mr_bake_to_worldspace)
import mr_find_constraint_targets_and_drivers
importlib.reload(mr_find_constraint_targets_and_drivers)

def mr_createNullOffset_keyed():
    sel = cmds.ls(selection=True)
    start_time = cmds.playbackOptions(q=True, min=True)
    end_time = cmds.playbackOptions(q=True, max=True)
    
    valid_objects = []
    keyed_objects = []
    nulls_for_keyed_objects = []
    static_objects = []

    # Organise selected objects into variables.
    for item in sel:
        parent = cmds.listRelatives(item, parent=True)
        
        # If item is an offset group, or is already in an offset group, give an error.
        if parent and parent[0].endswith("_offset_grp"):
            print("NOTE: The selected item is already in an offset_grp.")
            continue
        elif item.endswith("_offset_grp"):
            print("NOTE: The selected item is an offset group.")
            continue

        else:
            valid_objects.append(item)   
            # Unlock attributes for clean parenting.
            attrs = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]
            for attr in attrs:
                cmds.setAttr(item + attr, lock=False)

            # Check if item has keyframes.
            has_keyframes = cmds.keyframe(item, query=True, keyframeCount=True)
            if has_keyframes:
                keyed_objects.append(item)
            else:
                static_objects.append(item)
    
    # If keyed, bake them to spare locators, to hold their worldspace position while placing the item in a parent.
    if keyed_objects:
        cmds.select(keyed_objects)
        mr_bake_to_worldspace.mr_bake_to_worldspace("both")
                  
    # Create null group.
    
    # For each item,
    for item in valid_objects:
        # Create a null group.
        parent = cmds.listRelatives(item, parent=True)
        null = cmds.group(empty=True, name=item + "_offset_grp")
        # Match the position and orientation.
        cmds.parentConstraint(item, null)
        
        # If item is keyed, add it to a variable to be baked later.
        if item in keyed_objects:
            nulls_for_keyed_objects.append(null) 
        # Otherwise, just delete the constraint.
        elif item in static_objects:
            cmds.delete(null + "_parentConstraint1")
               
        # If item has a parent, place the null under it too.
        if parent:
            cmds.parent(null, parent[0])
        # Parent item under the null.
        cmds.parent(item, null)
    
    # For every item with keys, bake their constrained nulls.
    if nulls_for_keyed_objects:
        cmds.refresh(suspend=True)
        cmds.bakeResults(
            nulls_for_keyed_objects,
            simulation=True,
            attribute=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ' ],  # Only key translate attributes
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
        cmds.filterCurve()
        # Delete constraints on the nulls after baking.
        cmds.delete(nulls_for_keyed_objects, constraints=True)
        cmds.refresh(suspend=False)
    
    # Key the original selection, before deleting their drivers
    cmds.setKeyframe(sel, attribute='translateX')
    cmds.setKeyframe(sel, attribute='translateY')
    cmds.setKeyframe(sel, attribute='translateZ')
    cmds.setKeyframe(sel, attribute='rotateX')
    cmds.setKeyframe(sel, attribute='rotateY')
    cmds.setKeyframe(sel, attribute='rotateZ')
    # Delete their drivers.
    cmds.select(sel)
    mr_find_constraint_targets_and_drivers.mr_find_drivers_of_selected()
    cmds.delete()
    
    # Remove keys on original selection (to not double the motion)
    cmds.select(sel)
    set_transform_values_to_default()

    """
    # Finish script by selecting the last item
    last_item = sel[-1]
    cmds.select(last_item, replace=True)
    """
    cmds.select(sel)


def mr_createNullOffset_static():
    sel = cmds.ls(selection=True)
    start_time = cmds.playbackOptions(q=True, min=True)
    end_time = cmds.playbackOptions(q=True, max=True)
    
    keyed_objects = []
    
    for item in sel:
        parent = cmds.listRelatives(item, parent=True)

        if parent and parent[0].endswith("_offset_grp"):
            print("NOTE: The selected item is already in an offset_grp.")
            continue

        elif item.endswith("_offset_grp"):
            print("NOTE: The selected item is an offset group.")
            continue

        else:
            # Unlock attributes for clean parenting
            attrs = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]
            for attr in attrs:
                cmds.setAttr(item + attr, lock=False)

            # Check if the item has keyframes
            has_keyframes = cmds.keyframe(item, query=True, keyframeCount=True)
            if has_keyframes:
                keyed_objects.append(item)            


    if keyed_objects:
        cmds.select(keyed_objects)
        mr_bake_to_worldspace.mr_bake_to_worldspace("both")

    for item in sel:
        if parent and parent[0].endswith("_offset_grp"):
            continue
        elif item.endswith("_offset_grp"):
            continue

        else:
            # Create group
            null = cmds.group(empty=True, name=item + "_offset_grp")

            # Match position and orientation
            cmds.parentConstraint(item, null)
            cmds.delete(null + "_parentConstraint1")

            # Parent nulls
            if parent:
                cmds.parent(null, parent[0])
            cmds.parent(item, null)

            # Lock attributes of offset group
            attrs += [".sx", ".sy", ".sz", ".v"]
            for attr in attrs:
                cmds.setAttr(null + attr, lock=True)
    
    if keyed_objects:
        cmds.refresh(suspend=True)
        cmds.bakeResults(
            keyed_objects,
            simulation=True,
            time=(start_time, end_time),
            attribute=['translateX', 'translateY', 'translateZ'],  # Only key translate attributes
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
        cmds.filterCurve()
        cmds.refresh(suspend=False)

    # Delete drivers
    cmds.select(sel)
    mr_find_constraint_targets_and_drivers.mr_find_drivers_of_selected()
    cmds.delete()

    """
    # Finish script by selecting the last item
    last_item = sel[-1]
    cmds.select(last_item, replace=True)
    """
    cmds.select(sel)

def set_transform_values_to_default():
    selected_objects = cmds.ls(selection=True)
    
    if selected_objects:
        for obj in selected_objects:
            anim_curves = cmds.keyframe(obj, query=True, name=True)

            if anim_curves:
                for curve in anim_curves:
                    keyframes = cmds.keyframe(curve, query=True, timeChange=True)
                    """
                    for frame in keyframes:
                        cmds.setKeyframe(curve, time=(frame, frame), value=0)
                    """
                    for frame in keyframes:
                        if 'translate' in curve or 'rotate' in curve:
                            cmds.setKeyframe(curve, time=(frame, frame), value=0)
                            cmds.keyTangent(curve, edit=True, itt="flat", ott="flat")
                        elif 'scale' in curve:
                            cmds.setKeyframe(curve, time=(frame, frame), value=1)
                            cmds.keyTangent(curve, edit=True, itt="flat", ott="flat")
                            
        cmds.select(selected_objects)