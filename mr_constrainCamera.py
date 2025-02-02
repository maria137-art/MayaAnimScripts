import maya.cmds as cmds

"""
import importlib
import mr_constrainCamera
importlib.reload(mr_constrainCamera)

mr_constrainCamera.main()
"""

def main():
    selected_objects = cmds.ls(selection=True)
            
    # Get the current panel under the mouse cursor.
    current_panel = cmds.getPanel(withFocus=True)

    if 'modelPanel' in cmds.getPanel(typeOf=current_panel):
        # Get the camera attached to the current panel
        camera = cmds.modelPanel(current_panel, query=True, camera=True)

        # Check if the camera is already parented to a group with the suffix "_offset"
        parent_group = cmds.listRelatives(camera, parent=True)

        if parent_group and parent_group[0].endswith("_offset"):
            # Unparent the camera and delete the existing group
            cmds.parent(camera, world=True)
            cmds.delete(parent_group[0])
            print("Deleted existing group with '_offset' suffix:", parent_group[0])
            cmds.select(clear=True)
            cmds.select(selected_objects)
        else:
        
            if selected_objects:
                # Ensure selected object is not the current camera.
                if selected_objects[0] == camera:
                    cmds.warning("The selected object is the same as the current camera. Point constraint not created.")
                else:
                    cam_position = cmds.xform(camera, query=True, worldSpace=True, translation=True)
                    cam_rotation = cmds.xform(camera, query=True, worldSpace=True, rotation=True)
                    
                    # Create a null group at the camera's position and rotation
                    null_group = cmds.group(empty=True, world=True, name=camera + "_offset")
                    cmds.xform(null_group, worldSpace=True, translation=cam_position)
                    cmds.xform(null_group, worldSpace=True, rotation=cam_rotation)
                    
                    cmds.parent(camera, null_group)
            
                    # Create a point constraint to the selected object, skipping the Y axis.
                    cmds.pointConstraint(selected_objects[0], null_group, skip="y", maintainOffset=True)
                    print("Point constraint created between {} and {}".format(selected_objects[0], null_group))
            else:
                cmds.warning("No objects selected. Point constraint not created.")
    else:
        cmds.warning("Mouse cursor is not over a valid viewport panel.")