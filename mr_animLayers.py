"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_animLayers.py
# VERSION: 0005
#
# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Create a new additive animation layer for selected objects that has the same
# number of keyframes as the BaseAnimation layer.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_animLayers
importlib.reload(mr_animLayers)

# EXAMPLES
mr_animLayers.create_animation_layer_with_baseAnimation_keyTiming(override_layerMode=False)
mr_animLayers.bake_to_selected_override_animation_layer(simulation=True)

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-14 - 0005:
#   - Converting and merging mr_animLayer_createEmptyLayerWithKeyTimingFromSelected.mel to Python.
#
# 2024-01-03 - 0004:
#   - mr_animLayer_bake_to_override()
#       - Suspend viewport during bake.
#       - Add option to simulate bake or not.
#
# 2024-01-03 - 0003:
#   - mr_animLayer_bake_to_override()
#       - Avoid major bug when "BaseAnimation" is selected, by not using -destinationLayer with it during bakeResults.
#
# 2023-12-18 - 0002:
#   - mr_animLayer_bake_to_override()
#       - Ensuring no keys are selected before baking, to prevent Maya error.
#
# 2023-11-19 - 0001:
#   - mr_animLayer_bake_to_override()
#       - 1st pass of script. Created after working on multiple cycles in one file, each on an Override Layer.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

# ------------------------------------------------------------------------------ #
def bake_to_selected_override_animation_layer(simulation=True):
    """
    Working with multiple Override animation layers in a scene, and wanting to bake additve layers to it.
    Personally find it better than using Maya's Default Merge Layers, when dealing with a scene with multiple override animation layers.

    Example Uses
    -------
    Working with multiple Override animation layers in a scene, and wanting to bake additve layers to it.
    Personally find it better than using Maya's Default Merge Layers.

    Wish List
    -------
    - Bake to additive layers, without causing crazy offsets.
    - When baking, ignore attributes that aren't connected to any animation layers.

    """
    tool_name = "AnimLayerTab"
    
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.warning("No objects selected.")
        return
    
    selected_animation_layers = cmds.treeView(tool_name + "animLayerEditor", query=True, selectItem=True)
    if not selected_animation_layers:
        cmds.warning("No animation layer highlighted.")
    elif len(selected_animation_layers) > 1:
        cmds.warning("Please highlight only ONE animation layer to bake to.")
    else:
        selected_layer = selected_animation_layers[0]
        is_override = cmds.animLayer(selected_layer, query=True, override=True)
    
        if is_override:
            min_time = cmds.playbackOptions(query=True, minTime=True)
            max_time = cmds.playbackOptions(query=True, maxTime=True)

            # Deselect all keys, to avoid script erroring.
            cmds.selectKey(clear=True)

            cmds.refresh(suspend=1)
            if selected_layer == "BaseAnimation":
                # Don't use -destinationLayer flag with "BaseAnimation".
                # Otherwise, for some reason it stops user from setting keys on the object, until all animation layers are deleted.
                cmds.bakeResults(
                    simulation=simulation,
                    time=(min_time, max_time)
                )
            else:
                cmds.bakeResults(
                    destinationLayer=selected_animation_layers[0],
                    simulation=simulation,
                    time=(min_time, max_time)
                )
            cmds.refresh(suspend=0)
            # Clear any old warning messages.
            print("")

        else:
            cmds.warning(f"{selected_layer} is NOT of an 'Override' animation layer.")

# ------------------------------------------------------------------------------ #
def create_animation_layer_with_baseAnimation_keyTiming(override_layerMode=False):
    # ---------------------------------------
    # 01. CREATE ANIMATION LAYER.
    # ---------------------------------------
    selection = cmds.ls(selection=True) 

    # Create animation layer.
    if override_layerMode:
        animation_layer = cmds.animLayer(override=True)
    else:
        animation_layer = cmds.animLayer()

    # Add selected objects to a new animation_layer.
    cmds.animLayer(animation_layer, edit=True, addSelectedObjects=True)

    # ---------------------------------------
    # 01. IGNORE IRRELEVANT ATTRIBUTES.
    # ---------------------------------------
    attributes_to_ignore = [".v", ".sx", ".sy", ".sz"]

    for item in selection:
        # Check if attributes exist.
        attributes_to_remove = [
            attr 
            for attr in attributes_to_ignore 
            if cmds.attributeQuery(attr[1:], node=item, exists=True)
            ]

        if attributes_to_remove:
            cmds.animLayer(animation_layer, edit=True, removeAttribute=[f"{item}{attr}" for attr in attributes_to_remove])

    # ---------------------------------------
    # 01. COPY BASEANIMATION KEY TIMING.
    # ---------------------------------------
    # Deselect all animation layers.
    set_selected_for_all_layers(0)
    # Select just BaseAnimation.
    cmds.animLayer("BaseAnimation", edit=True, selected=True)

    # Get each frame that the selected object is keyed on on BaseAnimation.
    for item in selection:
        cmds.select(item)
        # Use a generator instead of a list.
        keyframes = (frame for frame in cmds.keyframe(item, query=True) or ())
        
        for frame in keyframes:
            # Set a key on the frame of the new animation layer.
            # NOTE: Use the -identity flag to nullify any offsets on the animation layer.
            cmds.setKeyframe(item, animLayer=animation_layer, time=(frame, frame), attribute=item, identity=True)

    # ---------------------------------------
    # 01. END SCRIPT.
    # ---------------------------------------
    cmds.select(selection, replace=True)

    # Select the new animation layer.
    set_selected_for_all_layers(0)
    cmds.animLayer(animation_layer, edit=True, selected=True)

##################################################################################################################################################

########################################################################
#                                                                      #
#                           SUPPORT FUNCTIONS                          #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def set_selected_for_all_layers(state):
    # Python version of setSelectedForAllLayers from Autodesk Maya's layerEditor.mel, line 1220
    layers = cmds.ls(type='animLayer')
    for layer in layers:
        cmds.animLayer(layer, edit=True, selected=state)