"""
# ------------------------------------------------------------------------------------------------------------------------------------------------
# SCRIPT: mr_selectKeys.py
# VERSION: 0006
#
# CREATORS: Maria Robertson
# CREDIT: Brian Horgan / Jørn-Harald Paulsen
# -------------------------------------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Select keys of selected objects in the Graph Editor.
# Use one of the selection modes.
# 		- "playback_range" 	- Select keys only within the Playback Range.
# 		- "all" 			- Select all keys in the Graph Editor.
# 		- "currentTime" 	- Select keys that are only on the current frame.
#
# EXAMPLE USES:
# ---------------------------------------
# Found using "playback_range" helpful when animating scenes with multiple shots inside.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_selectKeys
importlib.reload(mr_selectKeys)

# USE ONE OF THE FOLLOWING:
mr_selectKeys.main("playback_range")
mr_selectKeys.main("currentTime")
mr_selectKeys.main("all")

# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# https://help.autodesk.com/cloudhelp/2017/CHS/Maya-Tech-Docs/Commands/selectKey.html
# 
# This script started as a modification of a script Brian Horgan kindly provided on CGSociety, with snippets from Jørn-Harald Paulsen's jh_getKeyObjs:
# https://forums.cgsociety.org/t/selecting-all-keys-on-a-certain-frame/1563705/2
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-16 - 0006:
# 	- Minor formatting and changes.
#
# 2023-12-30 - 0005:
#	- Typo fix.
#
# 2023-12-30 - 0004:
# 	- Rename from mr_select_graphEditor_keys.py.
#
# 2023-12-29 - 0003:
#   - Combining with old MEL scripts, mr_select_currentFrameKeysOnVisibleCurvesOfSelected.mel and mr_select_currentFrameKeysOfSelected.mel.
#
# 2023-12-17 - 0002: 
# 	- Converted original MEL script.
#	- Made option to select all visible keys, or just those within the playback range.
#
# 2022-10-03 - 0001:
# 	- First original MEL script.
# ------------------------------------------------------------------------------------------------------------------------------------------------
"""

import maya.cmds as cmds

# ------------------------------------------------------------------------------ #
def main(selection_mode=None):
	# -------------------------------------------------------------------
	# 01. INITIALISE VARIABLES
	# -------------------------------------------------------------------
	selection = cmds.ls(selection=True)
	if not selection:
		cmds.warning("No selected items found.")
		return

	# deselect_unkeyed_objects(selection)

	visible_curves = cmds.animCurveEditor('graphEditor1GraphEd', query=True, curvesShown=True)
	if not visible_curves:
		cmds.warning("No visible animation curves found.")
		return

	cmds.selectKey(clear=True)

	# -------------------------------------------------------------------
	# 01. PICK A SELECTION TYPE.
	# -------------------------------------------------------------------
	# Select keys only within the playback range.
	if selection_mode == "playback_range":
		start_time = cmds.playbackOptions(query=True, min=True)
		end_time = cmds.playbackOptions(query=True, max=True)
		for curve in visible_curves:
			cmds.selectKey(curve, toggle=True, time=(start_time, end_time), add=True)

	# Select all keys.
	if selection_mode == "all":
		for curve in visible_curves:
			cmds.selectKey(curve, toggle=True)

	# Select keys only at the current time.
	if selection_mode == "currentTime":
		current_time = cmds.currentTime(query=True)
		for curve in visible_curves:
			cmds.selectKey(curve, toggle=True, time=(current_time, current_time))


##################################################################################################################################################

########################################################################
#                                                                      #
#                         SUPPORTING FUNCTIONS                         #
#                                                                      #
########################################################################

def deselect_unkeyed_objects(selection):
	new_selection = [obj for obj in selection if cmds.keyframe(obj, query=True, keyframeCount=True) != 0]
	
	if new_selection:
		cmds.select(new_selection, replace=True)
		return new_selection