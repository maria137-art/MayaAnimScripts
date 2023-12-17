"""
# ------------------------------------------------------------------------------------------------------------------------------------------------
# SCRIPT: mr_select_graphEditor_keys.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# CREDIT: Brian Horgan / Jørn-Harald Paulsen
# -------------------------------------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Select keys of selected objects within the timeslider range.
#
# A modification of a script by Brian Horgan kindly provided on CGSociety,
# with snippets from Jørn-Harald Paulsen's jh_getKeyObjs:
# https://forums.cgsociety.org/t/selecting-all-keys-on-a-certain-frame/1563705/2
#
# EXAMPLE USES:
# ---------------------------------------
# Found this helpful when animating scenes with multiple shots inside.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_select_graphEditor_keys
importlib.reload(mr_select_graphEditor_keys)

# Use one of the following:
mr_select_graphEditor_keys.main("all")
mr_select_graphEditor_keys.main("range")

# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# https://help.autodesk.com/cloudhelp/2017/CHS/Maya-Tech-Docs/Commands/selectKey.html
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-17 - 0002: 
# 	- Converted original MEL script.
#	- Made option to select all visible keys, or just those within the playback range.
#
# 2022-10-03 - 0001:
# 	- First original MEL script.
# ------------------------------------------------------------------------------------------------------------------------------------------------
"""


import maya.cmds as cmds

def main(mode=None):
	# -------------------------------------------------------------------
	# 01. INITIALISE VARIABLES
	# -------------------------------------------------------------------
	start_time = cmds.playbackOptions(query=True, min=True)
	end_time = cmds.playbackOptions(query=True, max=True)

	sel = cmds.ls(sl=True)
	visible_curves = cmds.animCurveEditor('graphEditor1GraphEd', query=True, curvesShown=True)

	if visible_curves:
		# -------------------------------------------------------------------
		# 03. SELECT OBJECTS THAT ONLY HAVE KEYFRAMES.
		# -------------------------------------------------------------------
		cmds.select(cl=True)
		for obj in sel:
			keyframe_count = cmds.keyframe(obj, query=True, keyframeCount=True)
			if keyframe_count != 0:
				cmds.select(obj, add=True)

		# -------------------------------------------------------------------
		# 04. SELECT KEYFRAMES.
		# -------------------------------------------------------------------
		cmds.selectKey(clear=True)

		# Select keys within playback range.
		if mode == "range":
			for curve in visible_curves:
				cmds.selectKey(curve, tgl=True, time=(start_time, end_time), add=True)

		# Select all keys.
		if mode == "all":
			for curve in visible_curves:
				cmds.selectKey(curve, tgl=True)
	else:
		 print("No visible animation curves found.")