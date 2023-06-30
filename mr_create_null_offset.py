import maya.cmds as cmds

import importlib
import mr_bake_to_worldspace
importlib.reload(mr_bake_to_worldspace)


def mr_create_null_offset():
    sel = cmds.ls(selection=True)
    objects_with_keyframes = []
    
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
                objects_with_keyframes.append(item)            
            
 
    if objects_with_keyframes:
        cmds.select(objects_with_keyframes)
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