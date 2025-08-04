"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_animLayers.py
# VERSION: 0010
#
# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of functions for working with animation layers.
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

mr_animLayers.remove_inactive_object_attributes(
    use_only_selected_animation_layers=True, 
    use_only_selected_objects=True
)

# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

import importlib
import mr_utilities
importlib.reload(mr_utilities)

# ------------------------------------------------------------------------------ #
def bake_to_selected_override_animation_layer(simulation=True, preserveOutsideKeys=True):
    """
    Bake animation to selected override animation layers.

    Example Uses
    -------
    I found this helpful when working with multiple Override animation layers in a scene, and wanting to bake information from others layers to it.
    Personally I find it better than using Maya's default "Merge Layers", which currently seems to bake objects even if they aren't attached to other layers.

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
                # Otherwise, for some reason it stops users from setting keys on the object, until all animation layers are deleted.
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
    that has the same number of keyframes as the BaseAnimation layer.

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
    mr_utilities.set_selected_for_all_animation_layers(0)
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
    mr_utilities.set_selected_for_all_animation_layers(0)
    cmds.animLayer(animation_layer, edit=True, selected=True)

# ------------------------------------------------------------------------------ #
def set_key_every_frame_on_animation_layers(
    filter_selected_animation_layers=True, 
    reset_non_numeric_attributes=True, 
    reset_selected_attributes=True,
    reset_to_default_value=True
):
    """
    (I can't remember why I made this... Maybe to quickly make manual noise on animation layers?
    Or to reset every keyframe on animation layers? In which case, need to stop it processing every frame regardless.)

    :param filter_selected_animation_layers: If True, filter only selected animation layers.
    :type filter_selected_animation_layers: bool
    :param reset_non_numeric_attributes: If True, reset non-numeric attributes as well.
    :type reset_non_numeric_attributes: bool
    :param reset_selected_attributes: If True, reset only selected attributes.
    :type reset_selected_attributes: bool

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
    start_frame = int(cmds.playbackOptions(query=True, minTime=True))
    end_frame = int(cmds.playbackOptions(query=True, maxTime=True))

    selection = cmds.ls(selection=True)


    for frame in range(start_frame, end_frame + 1):
        cmds.currentTime(frame, edit=True)
        for layer in animation_layers:
            if reset_to_default_value:
                cmds.setKeyframe(selection, animLayer=layer, identity=True)
            else:
                cmds.setKeyframe(selection, animLayer=layer)          

# ------------------------------------------------------------------------------ #
def toggle_mute_selected_animation_layers():
    """
    Toggle mute selected animation layers to quickly compare differences.

    """

    # Use MEL to get all highlighted animation layers in the AnimLayerTab
    mel_cmd = 'getSelectedAnimLayer("AnimLayerTab")'
    highlighted_layers = mel.eval(mel_cmd)

    if not highlighted_layers:
        return

    for anim_layer in highlighted_layers:
        is_muted = cmds.getAttr(anim_layer + ".mute")
        cmds.animLayer(anim_layer, edit=True, mute=not is_muted)

    # Re-evaluate the current frame to ensure any adjustments made to objects on the animation layer are preserved before toggling.
    cmds.currentTime(cmds.currentTime(query=True), edit=True)

##################################################################################################################################################

# ------------------------------------------------------------------------------ #
def remove_inactive_object_attributes(use_only_selected_animation_layers=True, use_only_selected_objects=True):
    """
    If object attributes have no keys or no offset values on an animation layer, remove them from it.

    :param use_only_selected_animation_layers: If True, process only selected animation layers.
    :type use_only_selected_animation_layers: bool
    :param use_only_selected_objects: If True, process only selected objects.
    :type use_only_selected_objects: bool

    :Notes:
    As of Autodesk Maya 2023.3, it looks likewhen you add three rotate attributes to an animation layer at once, it creates just one animBlend node.
    e.g.
    ... pSphere1_rotate_AnimLayer1

    This is instead of what happens for other attributes like translate and scale, where one animBlend node is always created per attribute.
    ... pSphere1_translateX_AnimLayer1
    ... pSphere1_translateY_AnimLayer1
    ... pSphere1_translateZ_AnimLayer1

    If one of the rotate attributes gets removed from its animation layer, THEN the other animBlend nodes are created.
    e.g.
    removing
    ... pSphere1,rotateX

    deletes
    ... pSphere1_rotate_AnimLayer1

    and creates
    ... pSphere1_rotateY_AnimLayer1
    ... pSphere1_rotateZ_AnimLayer1

    So had to make the function check for nodes during the for loop rather than outside.

    :Research:
    https://stackoverflow.com/questions/62846321/maya-query-animation-curve-data

    """

    # ---------------------------------------
    # 01. CHECK IF ANIMATION LAYERS ARE SELECTED.
    # ---------------------------------------
    selected_animation_layers = mel.eval("getSelectedAnimLayer(\"AnimLayerTab\")")

    if use_only_selected_animation_layers and not selected_animation_layers:
        mr_utilities.display_viewport_warning("No animation layers are selected.")
        return

    elif not use_only_selected_animation_layers:
        # Check if scene contains animation layers.
        all_animation_layers = mel.eval("buildAnimLayerArray;")
        if not all_animation_layers or all_animation_layers == ["BaseAnimation"]:
            mr_utilities.display_viewport_warning("No animation layers found in scene.")
            return    

        # Select all animation layers.
        mel.eval("setSelectedForAllLayers(1) ; ")
        cmds.animLayer("BaseAnimation", edit=True, selected=False, forceUIRefresh=True)

    # ---------------------------------------
    # 01. CHECK IF OBJECTS ARE SELECTED.
    # ---------------------------------------
    if use_only_selected_objects:
        selection = mr_utilities.get_selection_generator()
        if not selection:
            return
    else:
        original_selection = cmds.ls(selection=True)
        mel.eval("string $layers[] = getSelectedAnimLayer(\"AnimLayerTab\");")
        mel.eval("layerEditorSelectObjectAnimLayer($layers);")

    selection = mr_utilities.get_selection_generator()
    if not selection:
        return

    try:
        cmds.refresh(suspend=True)

        was_BaseAnimation_locked = cmds.animLayer("BaseAnimation", query=True, lock=True)
        if was_BaseAnimation_locked:
            cmds.animLayer("BaseAnimation", edit=True, lock=False, forceUIRefresh=True)

        for obj in selection:
            # ------------------------------------------------------------------- 
            # 03. GET OBJECT ATTRIBUTES CONNECTED TO ANIMATION LAYERS.
            # -------------------------------------------------------------------
            layered_attributes_dict = mr_utilities.get_layered_attributes(obj, filter_selected_animation_layers=True)

            if layered_attributes_dict:
                for layer, attributes in layered_attributes_dict.items():
                    for attr in attributes:
                        obj_attr = obj + "." + attr
                        # Get nodes and their associated animation layers.
                        nodes_with_layers = get_animblend_nodes_and_connected_layers_recursively(obj_attr)
                        # print(nodes_with_layers)

                        # ---------------------------------------
                        # 06. CHECK KEYS FOR EACH OBJECT ATTRIBUTE ON EACH CONNECTED ANIMATION LAYER.
                        # ---------------------------------------
                        if nodes_with_layers:
                            # print(f"\nObject Attribute: {obj_attr}")
                            # Iterate over nodes and their associated layers.
                            for node, layer in nodes_with_layers.items():
                                # print(f"Node: {node}")
                                # print(f"AnimLayer: {layer}")   

                                # If the object attribute has no keyframes on the animation layer, remove it.
                                keyframes = cmds.keyframe(node, query=True)
                                if not keyframes:
                                    remove_object_attribute(layer, obj_attr)
                                    break

                                # Check if it has any offsets from BaseAnimation.
                                if not is_object_attribute_offset(node, obj_attr, keyframes):
                                    print(f"No offsets found on {node}. Removing {obj_attr} from {layer}.")
                                    remove_object_attribute(layer, obj_attr)

    finally:
        cmds.refresh(suspend=False)

        if was_BaseAnimation_locked:
            cmds.animLayer("BaseAnimation", edit=True, lock=True, forceUIRefresh=True)

        if not use_only_selected_objects:
            cmds.select(original_selection)

        # End with the original selection of animation layers.
        mel.eval("setSelectedForAllLayers(0) ; ")
        for layer in selected_animation_layers:
            cmds.animLayer(layer, edit=True, selected=True)

        mr_utilities.display_viewport_warning("Finished!")


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
        reset_selected_attributes=reset_selected_attributes, 
        reset_non_numeric_attributes=reset_non_numeric_attributes, 
        nullify_only_selected_animation_layers=filter_selected_animation_layers
    )


########################################################################
#                                                                      #
#                            HELPER FUNCTIONS                          #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def get_animblend_nodes_and_connected_layers_recursively(object_attribute):
    """
    Get a list of animBlend nodes and the animation layers they're connected to for a given object attribute.

    :param object_attribute: The object attribute to find animBlend nodes and connected animation layers for.
    :type object_attribute: str
    :return: A dictionary of animBlend nodes and their connected animation layers.
    :rtype: dict

    :Example:

    >>> object_attribute = 'pSphere1.scaleX'
    >>> animBlend_nodes_and_animLayers_dict = get_animblend_nodes_and_connected_layers_recursively(object_attribute)
    >>> print("\n")
    ... for node, layer in animBlend_nodes_and_animLayers_dict.items():
    ...... print(f"ANIMBLEND NODE: {node}\nANIMATION LAYER: {layer}")

    ANIMBLEND NODE: pSphere1_scaleX_AnimLayer1
    ANIMATION LAYER: AnimLayer1
    ANIMBLEND NODE: pSphere1_scaleX_AnimLayer2
    ANIMATION LAYER: AnimLayer2  
     
    :Notes:
    In the Note Editor, you can see the type of a node by hovering the cursor over it.

    This link also lists all animBlend node types in Autodesk Maya:
    https://github.com/LumaPictures/pymel-docs/blob/master/docs/generated/pymel.core.nodetypes.rst

    """ 
    animBlend_nodes_and_animation_layers = {}
    blend_node_types = [
        "animBlendNodeAdditive",
        "animBlendNodeAdditiveDA",
        "animBlendNodeAdditiveDL",
        "animBlendNodeAdditiveF",
        "animBlendNodeAdditiveFA",
        "animBlendNodeAdditiveFL",
        "animBlendNodeAdditiveI16",
        "animBlendNodeAdditiveI32",
        "animBlendNodeAdditiveRotation",
        "animBlendNodeAdditiveScale",
        "animBlendNodeBase",
        "animBlendNodeBoolean",
        "animBlendNodeEnum",
        "animBlendNodeTime"
    ]
    connections = [object_attribute]

    while connections:
        next_connections = []
        for connection in connections:
            for node_type in blend_node_types:
                blend_nodes = cmds.listConnections(connection, source=True, destination=False, type=node_type)
                if blend_nodes:
                    for blend_node in blend_nodes:
                        animation_layer = get_animation_layers_of_animblend_node(blend_node)
                        if animation_layer:
                            animBlend_nodes_and_animation_layers[blend_node] = animation_layer
                    next_connections.extend(blend_nodes)
        connections = next_connections
    
    return animBlend_nodes_and_animation_layers

# ------------------------------------------------------------------------------ #
def get_animation_layers_of_animblend_node(node):
    """
    Get the animation layer connected to the specified animBlend node.

    :param node: The animBlend node to search a connected animation layer for.
    :type node: str
    :return: The animation layer connected to the node.
    :rtype: str

    :Example:

    >>> animBlend_node = 'pSphere1_scaleX_AnimLayer1'
    >>> animation_layer = get_animation_layers_of_animblend_node(animBlend_node)
    ...
    >>> print(f"\nBLEND NODE: {animBlend_node}\nANIMATION LAYER: {animation_layer}")
    ...
    BLEND NODE: pSphere1_scaleX_AnimLayer1
    ANIMATION LAYER: AnimLayer1

    """
    connections = cmds.listConnections(node, source=True, destination=False, type='animLayer') or []
    for connection in connections:
        if cmds.nodeType(connection) == 'animLayer':
            return connection
    return None

# ------------------------------------------------------------------------------ #
def nullify_animation_layer_keys(
    selection=None,
    reset_selected_attributes=False, 
    reset_non_numeric_attributes=False, 
    nullify_only_selected_animation_layers=False
):
    """
    A support function for reset_animation_layer_keys_at_currentTime(), to filter for the specific attributes to reset.

    :param selection: A list of objects to process
    :type selection: list(str), optional
    :param reset_selected_attributes: If True, reset only selected attributes.
    :type reset_selected_attributes: bool
    :param reset_non_numeric_attributes: If true, also reset non-numeric attributes.
    :type reset_non_numeric_attributes: bool
    :param nullify_only_selected_animation_layers: If true, reset keys on only selected animation layers.
    :type nullify_only_selected_animation_layers: bool

    """
    if not selection:
        mr_utilities.print_warning_from_caller("Nothing is selected.")

    for obj in selection:
        # ---------------------------------------
        # 02. IF NO ATTRIBUTES SPECIFIED, USE ALL KEYABLE.
        # ---------------------------------------
        if reset_selected_attributes:
            attributes_to_reset = mr_utilities.get_selected_channels(longName=True, node_to_query=obj) or cmds.listAttr(obj, keyable=True)
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
                    filtered_attributes = []
                    # ---------------------------------------
                    # 03. OPTIONAL - FILTER FOR SELECTED ATTRIBUTES.
                    # ---------------------------------------
                    if reset_selected_attributes:
                        filtered_attributes = [attr for attr in attributes if attr in attributes_to_reset]

                    # ---------------------------------------
                    # 03. OPTIONAL - FILTER OUT NON-NUMERIC ATTRIBUTES
                    # ---------------------------------------
                    if not reset_non_numeric_attributes:
                        filtered_attributes = [attr for attr in filtered_attributes if mr_utilities.is_attribute_numeric(obj, attr)]
                    # ---------------------------------------
                    # 03. SET KEYS.
                    # ---------------------------------------
                    cmds.setKeyframe(obj, animLayer=layer, attribute=filtered_attributes, identity=True)
        else:
            continue

    # Set to current time again, to force the viewport to update with the change.
    current_time = cmds.currentTime(query=True)
    cmds.currentTime(current_time, edit=True)

# ------------------------------------------------------------------------------ #
def is_object_attribute_offset(animBlend_node, object_attribute, keyframes):
    """
    Check if the specified object attribute has an offset from its default value at any of the given keyframes.

    :param animBlend_node: The animBlend node to read its value for.
    :type animBlend_node: str
    :param object_attribute: The object attribute to read the default value for.
    :type object_attribute: str
    :param keyframes: The keyframes to evaluate for the attribute's value.
    :type keyframes: list
    :return: True if the attribute has an offset at any of the keyframes.
    :rtype: bool
       
    """

    attribute = object_attribute.split('.')[-1]
    node = object_attribute.split('.')[0]

    default_value = cmds.attributeQuery(attribute, node=node, listDefault=True)[0]
    # print(f"\nDefault Value: {default_value}")

    for f in keyframes:
        # The BaseAnimation layer needs to be unlocked, for this to work.
        curve_value = cmds.keyframe(animBlend_node, query=True, eval=True, time=(f, f))[0]
        # print(f"Curve Value: {curve_value}")

        if curve_value != default_value:
            # print("OFFSET FOUND.")
            return True
    return False

# ------------------------------------------------------------------------------ #
def remove_object_attribute(animation_layer, object_attribute):
    """
    Remove a specified object attribute from an animation layer.

    :param animation_layer: The animation layer to remove the object attribute from.
    :type animation_layer: str
    :param object_attribute: The object attribute to remove.
    :type object_attribute: str

    """
    cmds.animLayer(animation_layer, edit=True, removeAttribute=object_attribute)


##################################################################################################################################################
"""
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
#
# 2025-08-04 - 0011:
#   - Added function:
#       - toggle_mute_selected_animation_layers()
#
# 2024-03-16 - 0010:
#   - Adding functions:
#       - remove_inactive_object_attributes()
#       - get_animblend_nodes_and_connected_layers_recursively()
#       - get_animation_layers_of_animblend_node()
#       - is_object_attribute_offset()
#       - remove_object_attribute()
#
# 2024-03-02 - 0009:
#   - Adding functions:
#       - set_key_every_frame_on_animation_layers()
#
# 2024-01-21 - 0008:
#   - Updating renamed function in mr_utilities:
#       -  set_selected_for_all_layers() to set_selected_for_all_animation_layers()
#   - Bug fix for nullify_animation_layer_keys()
#       - reset_selected_attributes was not exclusively resetting selected attributes. 
#
# 2024-01-16 - 0007:
#   - reset_animation_layer_keys_at_currentTime()
#       - Using generators more for efficiency.
#   - nullify_animation_layer_keys()
#       - Added layered_attributes check.
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