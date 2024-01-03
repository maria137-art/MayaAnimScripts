"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_animLayer_bake_to_override.py
# VERSION: 0003
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Bake animation to a highlighted Override animation layer.
#
# EXAMPLE USES:
# ---------------------------------------
# Working with multiple Override animation layers in a scene, and wanting to bake additve layers to it.
# Personally find it better than using Maya's Default Merge Layers.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

import importlib
import mr_animLayer_bake_to_override
importlib.reload(mr_animLayer_bake_to_override)

mr_animLayer_bake_to_override.main()

# ---------------------------------------
# WISH LIST:
# ---------------------------------------
# - Bake to additive layers, without causing crazy offsets.
# - When baking, ignore attributes that aren't connected to any animation layers.
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-03 - 0003:
# 	- Avoid major bug when "BaseAnimation" is selected, by not using -destinationLayer with it during bakeResults.
#
# 2023-12-18 - 0002:
# 	- Ensuring no keys are selected before baking, to prevent Maya error.
#
# 2023-11-19 - 0001:
#   - 1st pass of script. Created after working on multiple cycles in one file, each on an Override Layer.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def main():
	tool_name = "AnimLayerTab"
	
	selected_objects = cmds.ls(selection=True)
	if not selected_objects:
		cmds.warning("No objects selected.")
		return
	
	selected_layers = cmds.treeView(tool_name + "animLayerEditor", query=True, selectItem=True)
	if not selected_layers:
		cmds.warning("No animation layer highlighted.")
	elif len(selected_layers) > 1:
		cmds.warning("Please highlight only ONE animation layer to bake to.")
	else:
		selected_layer = selected_layers[0]
		is_override = cmds.animLayer(selected_layer, query=True, override=True)
	
		if is_override:
			min_time = cmds.playbackOptions(query=True, minTime=True)
			max_time = cmds.playbackOptions(query=True, maxTime=True)

			# Deselect all keys, to avoid script erroring.
			cmds.selectKey(clear=True)


			if selected_layer == "BaseAnimation":
				# Don't use -destinationLayer flag with "BaseAnimation".
				# Otherwise for some reason, it stops user from setting keys on connected objects, until all other animation layers are deleted.
				cmds.bakeResults(
					simulation=True,
					time=(min_time, max_time)
				)
			else:
				cmds.bakeResults(
					destinationLayer=selected_layers[0],
					simulation=True,
					time=(min_time, max_time)
				)
			
			# Clear any old warning messages.
			print("")

		else:
			cmds.warning(f"{selected_layer} is NOT of an 'Override' mode animation layer.")