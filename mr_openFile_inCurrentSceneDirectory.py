import maya.cmds as cmds
import os

def mr_openFile_inCurrentSceneDirectory():
    current_file_path = cmds.file(query=True, sceneName=True)

    # Get the directory path of the current scene file
    current_dir_path = os.path.dirname(current_file_path)

    # Bring up the "Open File" window and get the selected file path
    selected_file_path = cmds.fileDialog2(fileMode=1, startingDirectory=current_dir_path, dialogStyle=2, fileFilter='Maya Files (*.ma *.mb)')

    # If a file path is selected, open the scene using that path
    if selected_file_path:
        cmds.file(selected_file_path[0], open=True, force=True)

def mr_openFile_currentFile():
    current_file_path = cmds.file(query=True, sceneName=True)

    # Check if there are unsaved changes.
    if cmds.file(query=True, modified=True):
        # Ask the user if they want to save changes
        result = cmds.confirmDialog(
            title='Save Changes',
            message='Save changes to {}?'.format(current_file_path),
            button=['Save', 'Don\'t Save', 'Cancel'],
            defaultButton='Save',
            cancelButton='Cancel',
            dismissString='Cancel'
        )

        # Process user choice.
        if result == 'Save':
            cmds.file(save=True, force=True)
        elif result == 'Don\'t Save':
            cmds.file(force=True, new=True)
        else:
            # User canceled the operation.
            return

    # Reopen the scene.
    cmds.file(current_file_path, open=True, force=True)