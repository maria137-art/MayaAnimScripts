import maya.cmds as cmds

def main(point=True, orient=True):
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("No object selected.")
        return
    last_selected_object = selection[-1]

    # Get the camera being used in the current panel.
    panel = cmds.getPanel(withFocus=True)
    camera = cmds.modelPanel(panel, query=True, camera=True)
    if not camera:
        cmds.warning("No camera found in the current panel.")
        return

    # Get camera's position and rotation.
    camera_position = cmds.xform(camera, query=True, translation=True, worldSpace=True)
    camera_rotation = cmds.xform(camera, query=True, rotation=True, worldSpace=True)

    # Check if camera is already parented.
    group_node_suffix = "camOffsetGrp"
    group_node_name = f"{camera}_{selection[0]}_{group_node_suffix}"

    parent_group = cmds.listRelatives(camera, parent=True, fullPath=True)
    if parent_group:
        existing_group = parent_group[0]
        if existing_group.endswith(group_node_suffix):
            # Unparent camera.
            cmds.parent(camera, world=True)
            cmds.delete(existing_group)
            cmds.warning(f"Camera was already parented to group '{existing_group}'. Deleted.")
            cmds.select(selection)
            return

    # Create a group node for the camera.
    camera_group = cmds.group(empty=True, name=group_node_name)

    cmds.xform(camera_group, translation=camera_position, rotation=camera_rotation, worldSpace=True)

    cmds.parent(camera, camera_group)

    if point and orient:
        cmds.parentConstraint(last_selected_object, camera_group, maintainOffset=True)
    elif point and not orient:
        cmds.pointConstraint(last_selected_object, camera_group, maintainOffset=True)


    # Reselect the object.
    cmds.select(selection)