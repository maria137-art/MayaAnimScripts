"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_utilities.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# CREDIT: Morgan Loomis
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of short and/or support functions.
# Individual tools will mention if this script is required.
#
# Inspired by Morgan Loomis' ml_tools library:
# http://morganloomis.com/tool/ml_utilities/
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_utilities
importlib.reload(mr_utilities)

# USE ANY OF THE SUPPORT FUNCTIONS:
# e.g.
mr_utilities.clear_keys()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-30 - 0001:
#   - Adding following scripts:
#       - mr_clear_attributeKeys.mel
#       - mr_zeroOut_selectedAttributes.mel
#       - mr_zeroOut_selectedKeysInGraphEditor.mel
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

########################################################################
#                                                                      #
#                           KEYS FUNCTIONS                             #
#                                                                      #
########################################################################

def clear_keys():
	'''
	Highlighted attributes in the Channel Box will be cleared. 
	If no attributes are highlighted, all attributes of selected objects will be cleared.
	'''

    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("No selected objects found.")
        return
        
    highlighted_attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
    if highlighted_attributes:
        for item in sel:
            for attr in highlighted_attributes:
                cmds.cutKey(item + "." + attr)
    else:
        cmds.cutKey()

# ------------------------------------------------------------------------------ #

def zero_selected_keys()
	'''
	Zero out values of selected keys in the Graph Editor.
	'''
	cmds.keyframe(animation='keys', valueChange=0)