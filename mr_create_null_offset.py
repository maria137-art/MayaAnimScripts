"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_create_null_offset.py
# VERSION: 0003
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
import mr_create_null_offset
importlib.reload(mr_create_null_offset)

mr_create_null_offset.mr_create_null_offset()

# ---------------------------------------
# REQUIREMENTS: 
# ---------------------------------------
# mr_bake_to_worldspace.py
#
# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# For listing relatives: https://forums.cgsociety.org/t/list-all-parents-of-an-object-mel/1806687/2
# 
# The endsWith command: https://help.autodesk.com/cloudhelp/2016/CHS/Maya-LT-Tech-Docs/Commands/endsWith.html
# Learnt it because of this post: https://forums.autodesk.com/t5/maya-programming/selecting-all-polygon-objects-in-the-scene-with-a-certain-prefix/td-p/4240087
# 
# WISH LIST:
# ---------------------------------------
# - Make option to not bake null group.
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
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


def mr_create_null_offset():
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

        if parent and parent[0].endswith("_offset_grp"):
            print("NOTE: The selected item is already in an offset_grp.")
            continue
        elif item.endswith("_offset_grp"):
            print("NOTE: The selected item is an offset group.")
            continue

        else:
            valid_objects.append(item)   

            # Unlock attributes for clean parenting
            attrs = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]
            for attr in attrs:
                cmds.setAttr(item + attr, lock=False)

            # Check if item has keyframes
            has_keyframes = cmds.keyframe(item, query=True, keyframeCount=True)
            if has_keyframes:
                keyed_objects.append(item)
            else:
                static_objects.append(item)
    
    # If keyed, bake them to spare locators, to hold their worldspace position.
    if keyed_objects:
        cmds.select(keyed_objects)
        mr_bake_to_worldspace.mr_bake_to_worldspace("both")
                  
    # Create null group
    for item in valid_objects:
        parent = cmds.listRelatives(item, parent=True)
        null = cmds.group(empty=True, name=item + "_offset_grp")
        cmds.parentConstraint(item, null)

         # Match position and orientation
        if item in keyed_objects:
            nulls_for_keyed_objects.append(null) 
    
        elif item in static_objects:
            cmds.delete(null + "_parentConstraint1")
               
        # Parent nulls
        if parent:
            cmds.parent(null, parent[0])
        cmds.parent(item, null)


    if nulls_for_keyed_objects:
        cmds.refresh(suspend=True)
        cmds.bakeResults(
            nulls_for_keyed_objects,
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
        cmds.filterCurve()
        cmds.delete(nulls_for_keyed_objects, constraints=True)
        cmds.refresh(suspend=False)

    
    if keyed_objects:
        cmds.refresh(suspend=True)
        cmds.bakeResults(
            keyed_objects,
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
        cmds.filterCurve()
        cmds.delete(keyed_objects, constraints=True)
        cmds.refresh(suspend=False)   
        
        """
        # Lock attributes of offset group
        attrs += [".sx", ".sy", ".sz", ".v"]
        for attr in attrs:
            cmds.setAttr(null + attr, lock=True)
        """