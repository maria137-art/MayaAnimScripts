import maya.cmds as cmds
import os

def mr_openFile_inCurrentSceneDirectory():
    # Get the current scene file name
    current_file_path = cmds.file(query=True, sceneName=True)

    # Get the directory path of the current scene file
    current_dir_path = os.path.dirname(current_file_path)

    # Bring up the "Open File" window and get the selected file path
    selected_file_path = cmds.fileDialog2(fileMode=1, startingDirectory=current_dir_path, dialogStyle=2, fileFilter='Maya Files (*.ma *.mb)')

    # If a file path is selected, open the scene using that path
    if selected_file_path:
        cmds.file(selected_file_path[0], open=True, force=True)

