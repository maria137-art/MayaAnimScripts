"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_tempPin_pivotFromSelectionSet.py
# VERSION: 0008
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A script to create an temp offset group to pivot with, from a predetermined object.
# Originally created when wanting to quickly rotate IK controls in an FK manner. (e.g. rotating an IK foot around a pelvis)
#
# INSTRUCTIONS:
# ---------------------------------------
# PHASE 1: 
# Tag an object to pivot from with this command:
# mr_tempPin_pivotFromSelectionSet.create_follow_selection_set()
#
# PHASE 2:
# Select the objects you'd like to pivot, and then run the pivot_from_follow_selection_set(mode, time) function, with the desired settings:
#	mode:
#   	- "both" - constrain translate and rotate attributes
#   	- "translate" - constrain just translate attributes, leaving rotations unaffected.
#
#	time:
#		- "frame" - bake the temp pivot only on the curernt frame. For small on-frame adjustments.
#		- "range" - bake the temp pivot for the whole playback range.
#
# PHASE 3:
# When ready, run the same function used in PHASE 2, to set keys on the current frame for all of the temp pivot's targets, then delete temp pivot.
#
# EXAMPLE USES:
# ---------------------------------------
# I personally use two hotkeys for this script. 
# 	- CTRL + SHIFT + ALT + D to tag an object to pivot from.
# 	- CTRL + ALT + D to cycle between creating and deleting the temp pivot.
#
# If I want to often pivot around specific points of a mesh, I sometimes create rivet locators on it, so I can quickly tag them as pivots.
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------

import importlib
import mr_tempPin_pivotFromSelectionSet
importlib.reload(mr_tempPin_pivotFromSelectionSet)

# To tag an object to pivot from.
mr_tempPin_pivotFromSelectionSet.create_follow_selection_set()

# Use one of the following commads to pivot with:
mr_tempPin_pivotFromSelectionSet.pivot_from_follow_selection_set("both", "frame")
mr_tempPin_pivotFromSelectionSet.pivot_from_follow_selection_set("both", "range")
mr_tempPin_pivotFromSelectionSet.pivot_from_follow_selection_set("translate", "frame")
mr_tempPin_pivotFromSelectionSet.pivot_from_follow_selection_set("translate", "range")

# ---------------------------------------
# REQUIREMENTS: 
# ---------------------------------------
# Must have mr_find_constraint_targets_and_drivers.py in order to use mr_find_targets_of_selected()
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-18 - 0008:
# 	- Add warning if follow_set_name does not exist.
#
# 2023-12-18 - 0007:
# 	- Added option to create temp pivot on either the current frame or whole playback range.
#	- Adding to script description.
#
# 2023-11-28 - 0006:
# 	- Fixing typos with quotation marks.
#
# 2023-11-28 - 0005:
# 	- Splitting script to two options: 
# 		1: pivot with translation and rotation
# 		2: pivot with just translation
#
# 2023-11-20 - 0004:
# 	- Converted original MEL script to Python.
#
# 2023-06-05 - 0003:
# 	- Fixing bug that would think objects had constraints when they didn't.
#
# 2023-04-11 - 0002:
# 	- Added two possible options to pivot with.
# ------------------------------------------------------------------------------ //
"""

import maya.cmds as cmds
import maya.mel as mel

import importlib
import mr_find_constraint_targets_and_drivers
importlib.reload(mr_find_constraint_targets_and_drivers)

########################################################################
#                                                                      #
#                    CREATE A SELECTION SET TO FOLLOW                  #
#                                                                      #
########################################################################

def create_follow_selection_set():
	follow_set_name = "objToFollowSet"

	# If nothing or more than one object is selected,
	if len(cmds.ls(selection=True)) != 1:
		# NOTE: make sure -title is unique, otherwise dialog won't trigger
		cmds.confirmDialog(title="Error A", message="Select one object to tag as a pivot.")
	else:
		# If the set already exists, delete it.
		if cmds.objExists(follow_set_name):
			cmds.delete(follow_set_name)

		# Create a selection set for the selected object.
		obj_to_follow_set = cmds.sets(name=follow_set_name)


########################################################################
#                                                                      #
#           CREATE AN OFFSET GROUP TO PIVOT WITH SET TO FOLLOW         #
#                                                                      #
########################################################################

def pivot_from_follow_selection_set(mode=None, time=None):
	if mode != "both" and mode != "translate":
		cmds.warning("Please input a valid manipulation mode.")
		return
	if time != "range" and time != "frame":
		cmds.warning("Please choose the length of frames the pivot should be baked on.")
		return

	# -------------------------------------------------------------------
	# 01. INITIALIZE VARIABLES
	# -------------------------------------------------------------------
	temp_pivot_offset_group_name = "TEMP_pivot_offset" 
	follow_set_name = "objToFollowSet"
	
	objs_to_pivot = cmds.ls(selection=True)

	if not cmds.objExists(follow_set_name):
		cmds.warning(f"The selection set \"{follow_set_name}\" hasn't been created yet.")
		return	

	cmds.select(follow_set_name)
	follow_object = cmds.ls(selection=True)

	# If the selected object has any constraints, cancel script.
	for obj in objs_to_pivot:
		constraints = cmds.listRelatives(obj, type="constraint") or []
		unique_constraints = list(set(constraints))
 
		if len(constraints) > 0:
			cmds.confirmDialog(title="Error D", message="Selected object has constraints.")
			cmds.select(objs_to_pivot)
			raise RuntimeError("Selected objects have constraints, please remove them first.")
			return

	# -------------------------------------------------------------------
	# 01. IF AN OFFSET GROUP ALREADY EXISTS, KEY THE TARGETS AND DELETE THE GROUP
	# -------------------------------------------------------------------

	# If an offset group already exists,
	if cmds.objExists(temp_pivot_offset_group_name):
		# delete its connections.
		cmds.delete(temp_pivot_offset_group_name, constraints=True)

		temp_pivot_offset_group_children = cmds.listRelatives(temp_pivot_offset_group_name, children=True) or []

		# Set keys on children.
		cmds.select(temp_pivot_offset_group_children)
		mr_find_constraint_targets_and_drivers.mr_find_targets_of_selected()

		mel.eval("SetKeyTranslate ;")
		mel.eval("SetKeyRotate ;")
		
		# Delete the offset group.
		cmds.delete(temp_pivot_offset_group_name)
		
		# End with the Translate manipulator on.
		mel.eval("buildTranslateMM ;")
		mel.eval("destroySTRSMarkingMenu MoveTool ;")

	# -------------------------------------------------------------------
	# 01. IF AN OFFSET GROUP DOESN'T EXISTS, CREATE ONE AND SET-UP A TEMP PIVOT
	# -------------------------------------------------------------------

	# If the selection set exists,
	elif cmds.objExists(follow_set_name):

		# -------------------------------------------------------------------
		# 02. CHECK SELECTION
		# -------------------------------------------------------------------

		# If nothing or more than one object is selected,
		if len(objs_to_pivot) == 0:
			# NOTE: make sure -title is unique, otherwise dialog won't trigger
			cmds.confirmDialog(title="Error A", message="Select objects to pivot.")

		# If the selection set object is selected as the pivot,
		elif objs_to_pivot[0] == follow_object[0]:
			cmds.confirmDialog(title="Error B", message="Can't use an object marked to pivot from as the pivot.")

		# -------------------------------------------------------------------
		# 02. CREATE AN OFFSET GROUP TO PIVOT
		# -------------------------------------------------------------------

		else:
			# Create an offset group to pivot with.
			temp_pivot_offset_group = cmds.group(em=True, name=temp_pivot_offset_group_name)
			# Match its translate and rotate to the follow object.
			point_constraint = cmds.pointConstraint(follow_object[0], temp_pivot_offset_group, weight=1)
			orient_constraint = cmds.orientConstraint(follow_object[0], temp_pivot_offset_group, weight=1)
			

			# NOTE: Have to specifically name the constraint to delete, otherwise the null
			# group itself gets deleted too if "delete -cn" or "DeleteConstraints" is used  
			if time == "frame":
				cmds.setKeyframe(temp_pivot_offset_group, attribute="translate")

			elif time == "range":
				start_time = cmds.playbackOptions(query=True, min=True)
				end_time = cmds.playbackOptions(query=True, max=True)
				attributes = ["translateX", "translateY", "translateZ","rotateX", "rotateY", "rotateZ"]

				cmds.refresh(suspend=True)
				cmds.bakeResults(
					temp_pivot_offset_group,
					attribute=attributes,
					simulation=False,
					time=(start_time, end_time)
				)
				cmds.delete(temp_pivot_offset_group, staticChannels=True)
				cmds.refresh(suspend=False)

			cmds.delete(point_constraint)
			cmds.delete(orient_constraint)

			for obj in objs_to_pivot:
				loc = cmds.spaceLocator(name=obj + "_temp_pivot_loc")
				cmds.parent(loc, temp_pivot_offset_group)
	
				# Parent constrain loc to objs_to_pivot.
				cmds.parentConstraint(obj, loc, weight=1)
				cmds.delete(loc, constraints=True)
				
				if mode == "both":
					# Parent constrain loc to objs_to_pivot.
					cmds.pointConstraint(loc, obj, maintainOffset=True, weight=1)
					cmds.orientConstraint(loc, obj, maintainOffset=True, weight=1)
				
				elif mode == "translate":
					cmds.pointConstraint(loc, obj, maintainOffset=True, weight=1)
					
			cmds.select(temp_pivot_offset_group)

			# End with rotate manipulator active.
			mel.eval("buildRotateMM ;")
			mel.eval("destroySTRSMarkingMenu RotateTool ;")

	# -------------------------------------------------------------------
	# 01. IF NO SELECTION SET EXISTS, GIVE A WARNING
	# -------------------------------------------------------------------
	else:
		# (make sure -title is unique; otherwise, dialog won't trigger
		cmds.confirmDialog(title="Error C", message="Create a follow selection set first.")