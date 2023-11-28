import maya.cmds as cmds
import maya.mel as mel

import importlib
import mr_find_constraint_targets_and_drivers
importlib.reload(mr_find_constraint_targets_and_drivers)

"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_tempPin_pivotFromSelectionSet.py
# VERSION: 0005
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# DESCRIPTION: 
# Create a offset group to pivot with from a predetermined object.
#
# The temp pivot is intended for use only on the current frame.
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------

# To tag an object to pivot from.
mr_tempPin_create_followSelectionSet() ;

# To pivot with translation and rotation:
mr_tempPin_pivotFrom_followSelectionSet(1)

# To pivot with just translation:
mr_tempPin_pivotFrom_followSelectionSet(2)

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-11-28 - 0005
# Splitting script to two options: 
# 	1: pivot with translation and rotation
# 	2: pivot with just translation
#
# 2023-11-20 - 0004
# Converted original MEL script to Python.
#
# 2023-06-05 - 0003
# Fixing bug that would think objects had constraints when they didn't.
#
# 2023-04-11 - 0002
# Added two possible options to pivot with.
# ------------------------------------------------------------------------------ //
"""

########################################################################
#                                                                      #
#                    CREATE A SELECTION SET TO FOLLOW                  #
#                                                                      #
########################################################################

def mr_tempPin_create_followSelectionSet():
	obj_to_follow_set_name = "objToFollowSet"

	# If nothing or more than one object is selected,
	if len(cmds.ls(selection=True)) != 1:
		# give an error.
		# NOTE: make sure -title is unique, otherwise dialog won't trigger
		cmds.confirmDialog(title="Error A", message="Select one object to remember to pivot from.")
	else:
		# If the set already exists, delete it.
		if cmds.objExists(obj_to_follow_set_name):
			cmds.delete(obj_to_follow_set_name)

		# Create a selection set from the selected object.
		obj_to_follow_set = cmds.sets(name=obj_to_follow_set_name)


########################################################################
#                                                                      #
#           CREATE AN OFFSET GROUP TO PIVOT WITH SET TO FOLLOW         #
#                                                                      #
########################################################################

def mr_tempPin_pivotFrom_followSelectionSet(mode):
	if mode not in ["1", "2"]:
		cmds.warning("Please input a valid manipulation mode (1 to tranlsate and rotate, or 2 to only translate).")

	# -------------------------------------------------------------------
	# 01. INITIALIZE VARIABLES
	# -------------------------------------------------------------------
	temp_pivot_offset_group_name = "TEMP_pivot_offset" 
	follow_set_name = "objToFollowSet"
	
	objs_to_pivot = cmds.ls(selection=True)

	cmds.select(follow_set_name)
	follow_object = cmds.ls(selection=True)

	# If the selected object has any constraints, cancel procedure.
	for obj in objs_to_pivot:
		constraints = cmds.listRelativs(obj, type="constraint") or []
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
		
		# Create array of its children.
		temp_pivot_offset_group_child = cmds.listRelatives(temp_pivot_offset_group_name, children=True) or []

		# Set keys on its child.
		cmds.select(temp_pivot_offset_group_child)
		mr_find_constraint_targets_and_drivers.mr_find_targets_of_selected()
		driven_objs = cmds.ls(selection=True)

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
			# Create an offset group to pivot with, at the same location as follow_object.
			temp_pivot_offset_group = cmds.group(em=True, name=temp_pivot_offset_group_name)
			# Set its transforms.
			cmds.pointConstraint(follow_object[0], temp_pivot_offset_group, weight=1)
			cmds.orientConstraint(follow_object[0], temp_pivot_offset_group, weight=1)

			# NOTE: Have to specifically name the constraint to delete, otherwise the null
			# group itself gets deleted too if "delete -cn" or "DeleteConstraints" is used  
			
			# Option B - Delete all offset group constraints. Can be better for pivoting around controls on the same rig.
			cmds.setKeyframe(temp_pivot_offset_group, attribute="translate")
			cmds.delete(temp_pivot_offset_group + "_orientConstraint1")
			cmds.delete(temp_pivot_offset_group + "_pointConstraint1")

			for obj in objs_to_pivot:
				loc = cmds.spaceLocator(name=obj + "_temp_pivot_loc")
				cmds.parent(loc, temp_pivot_offset_group)
	
				# Parent constrain loc to objs_to_pivot.
				cmds.parentConstraint(obj, loc, weight=1)
				cmds.delete(loc, constraints=True)
				
				if mode == "1":
					# Parent constrain loc to objs_to_pivot.
					cmds.pointConstraint(loc, obj, maintainOffset=True, weight=1)
					cmds.orientConstraint(loc, obj, maintainOffset=True, weight=1)
				
				elif mode == "2":
					cmds.pointConstraint(loc, obj, maintainOffset=True, weight=1)
					
				
			cmds.select(temp_pivot_offset_group)

			# End with rotate manipulator active.
			mel.eval("buildRotateMM ;")
			mel.eval("destroySTRSMarkingMenu RotateTool ;")

	# -------------------------------------------------------------------
	# 01. IF NO SELECTION SET EXISTS, GIVE A WARNING
	# -------------------------------------------------------------------

	# If both of the conditions don't exist, give prompt.
	else:
		# (make sure -title is unique; otherwise, dialog won't trigger
		cmds.confirmDialog(title="Error C", message="Create a follow selection set first.")