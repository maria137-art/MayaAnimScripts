import maya.cmds as cmds
import os

def mr_saveAs_inCurrentSceneDirectory():
	# Get the current scene file name
	current_file_path = cmds.file(query=True, sceneName=True)

	# Get the directory path of the current scene file
	current_dir_path = os.path.dirname(current_file_path)
	
	# Bring up the "Save As" window and get the new file path
	new_file_path = cmds.fileDialog2(fileMode=0, startingDirectory=current_dir_path, dialogStyle=2, fileFilter='Maya ASCII (*.ma);;Maya Binary (*.mb)')


	# If a new file path is specified, save the scene using that path
	if new_file_path:
	    cmds.file(rename=new_file_path[0])
	    cmds.file(save=True, type='mayaAscii') # Change to 'mayaBinary' for binary file format