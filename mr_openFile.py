"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_openFile.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A script with functions to customise how files are opened.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_openFile
importlib.reload(mr_openFile)

# USE ONE OF THE FUNCTIONS BELOW:
mr_openFile.open_file_in_current_scene_directory()
mr_openFile.open_current_scene_file()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-08- 0006:
#   - Minor formatting.
#
# 2024-01-03- 0006:
#   - Added functions.
# ------------------------------------------------------------------------------ #
"""

import os
import maya.cmds as cmds
import maya.mel as mel

# ------------------------------------------------------------------------------ #
def open_file_in_current_scene_directory():
    """
    Open a Maya scene file located in the current scene directory.

    """
    
    current_file_path = cmds.file(query=True, sceneName=True)
    current_directory_path = os.path.dirname(current_file_path)

    # Bring up the "Open File" window and get the selected file path.
    selected_file_path = cmds.fileDialog2(fileMode=1, startingDirectory=current_directory_path, dialogStyle=2, fileFilter='Maya Files (*.ma *.mb)')

    # If a file path is selected, open the scene using that path.
    if selected_file_path:
        selected_file_path = selected_file_path[0]
        cmds.file(selected_file_path, open=True, force=True)

        # Determine the file type based on the file extension.
        file_type = cmds.file(selected_file_path, query=True, type=True)

        # Help for adding to Recent Files list - https://python.hotexamples.com/examples/maya.mel/-/addRecentFile/python-addrecentfile-function-examples.html
        # Add the opened file to the Recent Files list.
        mel.eval('addRecentFile("{0}", "{1}")'.format(selected_file_path, file_type[0]))

# ------------------------------------------------------------------------------ #
def open_current_scene_file():
    """
    Reopen the current Maya scene file.
    Can be handy if wanting to quickly discard changes in the current Maya session.

    """
    current_file_path = cmds.file(query=True, sceneName=True)

    # Check if there are unsaved changes.
    if cmds.file(query=True, modified=True):
        # Ask the user if they want to save changes.
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

    # Reopen scene.
    cmds.file(current_file_path, open=True, force=True)