import os
import maya.cmds as cmds
import maya.mel as mel

def mr_openFile_inCurrentSceneDirectory():
    current_file_path = cmds.file(query=True, sceneName=True)

    # Get the directory path of the current scene file.
    current_dir_path = os.path.dirname(current_file_path)

    # Bring up the "Open File" window and get the selected file path.
    selected_file_path = cmds.fileDialog2(fileMode=1, startingDirectory=current_dir_path, dialogStyle=2, fileFilter='Maya Files (*.ma *.mb)')

    # If a file path is selected, open the scene using that path.
    if selected_file_path:
        selected_file_path = selected_file_path[0]
        cmds.file(selected_file_path, open=True, force=True)

        # Determine the file type based on the file extension.
        file_type = cmds.file(selected_file_path, query=True, type=True)

        # Help for adding to Recent Files list - https://python.hotexamples.com/examples/maya.mel/-/addRecentFile/python-addrecentfile-function-examples.html
        # Add the opened file to the Recent Files list.
        mel.eval('addRecentFile("{0}", "{1}")'.format(selected_file_path, file_type[0]))



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