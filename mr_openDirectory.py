"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_openDirectory.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of functions to open directories with Windows Explorer from inside Autodesk Maya.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_openDirectory
importlib.reload(mr_openDirectory)

# USE ANY OF THE FUNCTIONS BELOW:
mr_openDirectory.current_scene_directory()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-02-25- 0001:
#   - First pass..
# ------------------------------------------------------------------------------ #
"""

import os
import maya.cmds as cmds
import inspect
from maya import OpenMaya

def current_scene_directory():
    """
    Open Windows Explorer in the directory of the current scene.
    """
    current_file_path = cmds.file(query=True, sceneName=True)
    
    if current_file_path:
        current_directory = os.path.dirname(current_file_path)
        os.startfile(current_directory)
    else:
        # Display a warning message in the viewport.
        message = ("No scene file found to locate a directory for.")
        position='midCenterTop'

        caller_function_name = inspect.currentframe().f_back.f_code.co_name
        OpenMaya.MGlobal.displayWarning(message)
        fadeTime = min(len(message)*100, 2000)
        cmds.inViewMessage( message=f"{message}", pos=position, fade=True, fadeStayTime=fadeTime, dragKill=True)
