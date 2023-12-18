"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_animLayer_bake_to_override.py
# VERSION: 0002
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
	
	# -------------------------------------------------------------------
	# 01. CHECK IF OBJECTS ARE SELECTED.
	# -------------------------------------------------------------------
	selected_objects = cmds.ls(selection=True)
	if not selected_objects:
		cmds.warning("No objects selected.")
		return
	
	# -------------------------------------------------------------------
	# 01. CHECK HOW MANY ANIMLAYERS ARE HIGHLIGHTED.
	# -------------------------------------------------------------------
	highlighted_layers = cmds.treeView(tool_name + "animLayerEditor", query=True, selectItem=True)
	if not highlighted_layers:
		cmds.warning("No animation layer highlighted.")
	elif len(highlighted_layers) > 1:
		cmds.warning("Please highlight only ONE animation layer to bake to.")
	
	else:
		# -------------------------------------------------------------------
		# 01. CHECK IF HIGHLIGHTED ANIM LAYER IS AN OVERRIDE.
		# -------------------------------------------------------------------
		highlighted_layer = highlighted_layers[0]
		is_override = cmds.animLayer(highlighted_layer, query=True, override=True)
	
		if not is_override:
			cmds.warning(f"{highlighted_layer} is NOT of an 'Override' mode animation layer.")

		# -------------------------------------------------------------------
		# 01. BAKE TO THE OVERRIDE LAYER.
		# -------------------------------------------------------------------            
		else:   
			minTime = cmds.playbackOptions(query=True, minTime=True)
			maxTime = cmds.playbackOptions(query=True, maxTime=True)

			# Ensure no keys are selected, to avoid script erroring.
			cmds.selectKey(clear=True)

			cmds.bakeResults(
				destinationLayer=highlighted_layers[0],
				simulation=True,
				time=(minTime, maxTime)
			)
			
			# Clear any old warning messages.
			print("")