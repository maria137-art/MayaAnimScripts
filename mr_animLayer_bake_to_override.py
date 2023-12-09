"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_animLayer_bake_to_override.py
# VERSION: 0001
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
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
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
			
			cmds.bakeResults(
				destinationLayer=highlighted_layers[0],
				simulation=True,
				time=(minTime, maxTime),
				sampleBy=1,
				oversamplingRate=1,
				disableImplicitControl=True,
				preserveOutsideKeys=True,
				sparseAnimCurveBake=False,
				removeBakedAttributeFromLayer=False,
			)
			
			# Clear any old warning messages.
			print("")