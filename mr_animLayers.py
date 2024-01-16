"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_animLayers.py
# VERSION: 0007
#
# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of functions to help work with animation layers.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_animLayers
importlib.reload(mr_animLayers)

# EXAMPLES
mr_animLayers.bake_to_selected_override_animation_layer(
    simulation=True, 
    preserveOutsideKeys=True
)

mr_animLayers.create_animation_layer_with_baseAnimation_keyTiming(
    override_layerMode=False
)

mr_animLayers.reset_animation_layer_keys_at_currentTime(
    filter_selected_animation_layers=True, 
    reset_non_numeric_attributes=True, 
    reset_selected_attributes=True
)

# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import sys

import importlib
import mr_utilities
importlib.reload(mr_utilities)

# ------------------------------------------------------------------------------ #
def bake_to_selected_override_animation_layer(simulation=True, preserveOutsideKeys=True):
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
                    time=(min_time, max_time),
                    preserveOutsideKeys=preserveOutsideKeys
                )
            else:
                cmds.bakeResults(
                    destinationLayer=selected_animation_layers[0],
                    simulation=simulation,
                    time=(min_time, max_time),
                    preserveOutsideKeys=preserveOutsideKeys
                )
            cmds.refresh(suspend=0)
            # Clear any old warning messages.
            print("")

        else:
            cmds.warning(f"{selected_layer} is NOT of an 'Override' animation layer.")

# ------------------------------------------------------------------------------ #
def create_animation_layer_with_baseAnimation_keyTiming(override_layerMode=False):
    """
    Create a new additive animation layer for selected objects,
    that has the same umber of keyframes as the BaseAnimation layer.

    :param override_layerMode: If True, create an Override animation layer, instead of Additive.
    :type override_layerMode: bool
    """
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
    mr_utilities.set_selected_for_all_layers(0)
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
    mr_utilities.set_selected_for_all_layers(0)
    cmds.animLayer(animation_layer, edit=True, selected=True)

##################################################################################################################################################

# ------------------------------------------------------------------------------ #
def reset_animation_layer_keys_at_currentTime(
    filter_selected_animation_layers=False, 
    reset_non_numeric_attributes=False, 
    reset_selected_attributes=False
):
    """
    Reset keys of animation layers at the current time for selected objects.
    This works the same as setting an animation layer's weight to 0, setting a key to store the current pose frame, then restoring its weight.

    :param filter_selected_animation_layers: If True, reset only for the currently selected animation layers.
    :type filter_selected_animation_layers: bool
    :param reset_non_numeric_attributes: If True, reset non-numeric attributes.
    :type reset_non_numeric_attributes: bool
    :param reset_selected_attributes: If True, reset only the selected attributes on the objects.
    :type reset_selected_attributes: bool

    :Example:

    >>>  (
    ...     filter_selected_animation_layers=True,
    ...     reset_non_numeric_attributes=False,
    ...     reset_selected_attributes=True
    ... )

    """
    # ---------------------------------------
    # 01. GET SELECTION.
    # ---------------------------------------
    selection = mr_utilities.get_selection_generator()

    # ---------------------------------------
    # 01. CHECK IF ANIMATION LAYERS CONNECTED TO SELECTED OBJECTS ARE LOCKED OR MUTED.
    # ---------------------------------------
    animation_layers = set()

    for obj in selection:
        connected_animation_layers = cmds.listConnections(obj, type="animLayer") or []
        animation_layers.update(connected_animation_layers)

    # ---------------------------------------
    # 01. OPTIONAL - CHECK IF ANIMATION LAYERS ARE SELECTED.
    # ---------------------------------------
    if filter_selected_animation_layers:
        animation_layers = mr_utilities.filter_for_selected_animation_layers(animation_layers)

    # ---------------------------------------
    # 01. CHECK IF CONNECTED ANIMATION LAYERS ARE LOCKED OR MUTED.
    # ---------------------------------------
    if animation_layers:
        for layer in animation_layers:
            mute_state = cmds.getAttr(layer + ".mute")
            lock_state = cmds.getAttr(layer + ".lock")

            if mute_state and lock_state:
                mr_utilities.print_warning_from_caller(f"\"{layer}\" is muted and locked.")
                return
            elif mute_state:
                mr_utilities.print_warning_from_caller(f"\"{layer}\" is muted.")
                return
            elif lock_state:
                mr_utilities.print_warning_from_caller(f"\"{layer}\" is locked.")
                return
    else:
        mr_utilities.print_warning_from_caller("No connections found to queried animation layers.")
        return


    # ---------------------------------------
    # 01. RESET KEYS.
    # ---------------------------------------
    nullify_animation_layer_keys(
        selection=mr_utilities.get_selection_generator(),
        attributes_to_reset=None, 
        reset_selected_attributes=reset_selected_attributes, 
        reset_non_numeric_attributes=reset_non_numeric_attributes, 
        nullify_only_selected_animation_layers=filter_selected_animation_layers
    )

# ------------------------------------------------------------------------------ #
def nullify_animation_layer_keys(selection=None, attributes_to_reset=None, reset_selected_attributes=False, reset_non_numeric_attributes=False, nullify_only_selected_animation_layers=False):
    if not selection:
        mr_utilities.print_warning_from_caller("Nothing is selected.")

    for obj in selection:
        # ---------------------------------------
        # 02. IF NO ATTRIBUTES SPECIFIED, USE ALL KEYABLE.
        # ---------------------------------------
        if not attributes_to_reset:
            if reset_selected_attributes:
                attributes_to_reset = mr_utilities.get_selected_channels() or cmds.listAttr(obj, keyable=True)
            else:
                attributes_to_reset = cmds.listAttr(obj, keyable=True)

        # ---------------------------------------
        # 02. FILTER KEYS TO NULLIFY.
        # ---------------------------------------
        if attributes_to_reset:

            # ---------------------------------------
            # 03. OPTIONAL - FILTER FOR ATTRIBUTES ON SELECTED ANIMATON LAYERS.
            # ---------------------------------------    
            if nullify_only_selected_animation_layers:
                layered_attributes = mr_utilities.get_layered_attributes(obj, filter_selected_animation_layers=True)
            else:
                layered_attributes = mr_utilities.get_layered_attributes(obj, filter_selected_animation_layers=False)

            if layered_attributes:
                for layer, attributes in layered_attributes.items():
                    # ---------------------------------------
                    # 03. OPTIONAL - FILTER FOR SELECTED ATTRIBUTES.
                    # ---------------------------------------
                    if reset_selected_attributes:
                        for attr in attributes:
                            if attr not in attributes_to_reset:
                                attributes.remove(attr)
                    # ---------------------------------------
                    # 03. OPTIONAL - FILTER OUT NON-NUMERIC ATTRIBUTES
                    # ---------------------------------------
                    if not reset_non_numeric_attributes:
                        for attr in attributes:
                            if not mr_utilities.is_attribute_numeric(obj, attr):
                                attributes.remove(attr)
                    # ---------------------------------------
                    # 03. SET KEYS.
                    # ---------------------------------------
                    cmds.setKeyframe(obj, animLayer=layer, attribute=attributes, identity=True)
        else:
            continue

    # Set to current time again, to force the viewport to update with the change.
    current_time = cmds.currentTime(query=True)
    cmds.currentTime(current_time, edit=True)


##################################################################################################################################################
"""
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-16 - 0007:
#   - reset_animation_layer_keys_at_currentTime()
#       - Using generators more for efficiency.
#   - nullify_animation_layer_keys()
#       - Added layered_attributes check.
#
#
# 2024-01-16 - 0006:
#   - Add following functions for mr_utilities.
#       - reset_animation_layer_keys_at_currentTime()
#       - nullify_animation_layer_keys()
#
# 2024-01-14 - 0005:
#   - Converting and merging mr_animLayer_createEmptyLayerWithKeyTimingFromSelected.mel to Python.
#   - bake_to_selected_override_animation_layer():
#       - Adding option to preserve outside keys.
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