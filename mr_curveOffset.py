"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_curveOffset.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# CREDIT: Nicolas Prothais (for original np_curveOffset.mel script)
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A script to offset animation curves when changes are made in the viewport.
#
# Based on Nicolas Prothais's np_curveOffset.mel script.
# Original link: http://nicolas-prothais.com/script.html
# Alternate link: https://docs.google.com/document/d/1vEaG8KTG3BXYx6yusfGmnU1DjO2rVywWb2rSxqRIWqA/edit
#
# ---------------------------------------
# EXAMPLE USES:
# ---------------------------------------
# Tweaking controls during walk cycles.
#
# ---------------------------------------
# INSTRUCTIONS:
# ---------------------------------------
# Assign a hotkey for offset_press() with the option set to "press".
# Assign a hotkey for offset_release() with the optino set to "release".
#
# Hold the hotkey down when making viewport changes you'd like to offset.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_curveOffset
importlib.reload(mr_curveOffset)

# PRESS HOTKEY
mr_curveOffset.offset_press()

# RELEASE HOTKEY
mr_curveOffset.offset_release()

"""

import maya.cmds as cmds

import importlib
import mr_utilities
importlib.reload(mr_utilities)

# ------------------------------------------------------------------------------ #
def offset_press():
	cmds.undoInfo(openChunk=True)

	global attr_value
	attr_value = []

	# If auto keyframe was on, temporarily disable it.
	global original_autoKey_state
	original_autoKey_state = cmds.autoKeyframe(query=True, state=True)

	if original_autoKey_state: 
		cmds.autoKeyframe(state=False)

	# Save object attribute values.
	valid_object_attributes = mr_utilities.get_object_attributes(
		selection=None, 
		attributes=None, 
		filter_locked=True, 
		filter_muted=True, 
		filter_constrained=True, 
		filter_connected=True
	)
	att_buffer = []

	for attr in valid_object_attributes:
		att_value = cmds.getAttr(attr)
		att_buffer.append(att_value)
		attr_value.append(att_value)


# ------------------------------------------------------------------------------ #
def offset_release():
	# Query how many object attributes need to be offset.
	selection = cmds.ls(selection=True) or []
	all_keyable_attr = mr_utilities.get_object_attributes(
		selection=selection, 
		attributes=None, 
		filter_locked=True, 
		filter_muted=True, 
		filter_constrained=True, 
		filter_connected=True
	)

	# Initialize variables.
	obj_attr_name = []
	second_attr_value = []
	result = []

	time_range = cmds.keyframe(query=True, attribute=True) or []

	# Get each object attribute's value.
	for obj in selection:
		second_keyable_attr = mr_utilities.get_object_attributes(
			selection=obj, 
			attributes=None, 
			filter_locked=True, 
			filter_muted=True, 
			filter_constrained=True, 
			filter_connected=True
		)

		for attr in second_keyable_attr:
			second_attr_value.append(cmds.getAttr(attr))
			obj_attr_name.append(attr)

	try:
		if not time_range:
			for j in range(len(list(all_keyable_attr))):
				result.append(-1 * (attr_value[j] - second_attr_value[j]))
				cmds.keyframe(obj_attr_name[j], animation="objects", relative=True, valueChange=(0 + result[j]))

		else:
			for j in range(len(list(all_keyable_attr))):
				result.append(-1 * (attr_value[j] - second_attr_value[j]))
				time_range_str = "{}:{}".format(time_range[0], time_range[-1])
				cmds.keyframe(obj_attr_name[j], animation="objects", relative=True, time=(time_range_str), valueChange=(0 + result[j]))

	finally:
		# If auto keyframe was originally on, restore its state.
		cmds.autoKeyframe(state=original_autoKey_state)
		cmds.undoInfo(closeChunk=True)

"""
##################################################################################################################################################
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-02-02 - 0002:
#	- Fixing undo queue, so autokeyframe doesn't unexpectadly get disabled when undoing.
#
# 2024-01-23 - 0001:
#   - First pass, converting the original mel script to python.
#		- Incorporating mr_utilities.get_object_attributes(), to avoid errors with incompatible attributes.
#
# ---------------------------------------
##################################################################################################################################################
"""