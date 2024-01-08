"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_utilities.py
# VERSION: 0006
#
# CREATORS: Maria Robertson
# CREDIT: Morgan Loomis, Tom Bailey
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of short and/or support functions.
# Individual tools will mention if this script is required.
#
# Major thanks to:
#   - Morgan Loomis' ml_tools library: http://morganloomis.com/tool/ml_utilities/
#   - Tom Bailey's tbAnimTools library: https://github.com/tb-animator/tbAnimTools
# 
# They've been a great resource for script and animation workflows.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_utilities
importlib.reload(mr_utilities)

# USE ANY OF THE FUNCTIONS BELOW:
mr_utilities.#

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-08- 0006:
#   - Trying to use reStructuredText docString style.
#       - https://stackabuse.com/common-docstring-formats-in-python/
#       - https://www.rdegges.com/2010/python-docstring-symmetry/
#       - https://peps.python.org/pep-0257/
#       - https://www.writethedocs.org/guide/writing/reStructuredText/
#   - Added several functions.
#   - Added check for locked attributes in reset_to_default().
#   - Added check for if attr in attrToRest reset_to_default().
#   - Starting to use get_selection() for most functions.
#
# 2024-01-03- 0005:
#   - Added select_joints_under_selected_objects().
#
# 2024-01-03- 0004:
#   - Added functions.
#
# 2024-01-03 - 0003:
#   - Updated clear_keys() to check if selected attributes exist on each selected object.
#
# 2024-01-02 - 0002:
#   - Working on adding docstrings.
#   - Added reset key functions.
#   - Added animation layer functions.
#
# 2023-12-30 - 0001:
#   - Added scripts:
#       - mr_clear_attributeKeys.mel
#       - mr_zeroOut_selectedAttributes.mel
#       - mr_zeroOut_selectedKeysInGraphEditor.mel
# ------------------------------------------------------------------------------ #
"""

import inspect
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from maya import OpenMaya

########################################################################
#                                                                      #
#                        ANIMATION CURVE FUNCTIONS                     #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def set_animation_curves_lock_state(anim_curve_nodes, lock_state=False):
    """
    Set the lock state of specified animation curve nodes.
    
    Thanks to DrWeeny at StackOverflow for explaining how the MEL commands "doTemplateChannel" and "expandSelectionConnectionAsArray" work:
    https://stackoverflow.com/questions/37816681/maya-python-trying-to-template-untemplate-channel

    :param anim_curve_nodes: List of animation curve nodes
    :type anim_curve_nodes: list
    :param lock_state: The lock state to be set
    :type lock_state: bool

    """
    if anim_curve_nodes:
        for node in anim_curve_nodes:
            if cmds.objExists(node):
                for attr in ['.ktv', '.kix', '.kiy', '.kox', '.koy']:
                    attr_name = node + attr
                    # Removing the . in attr for attributeQuery.
                    if cmds.attributeQuery(attr[1:], node=node, exists=True):
                        # Lock curve.
                        if lock_state:
                            cmds.setAttr(attr_name, lock=lock_state)
                        # Unlock curve.
                        else:
                            # Set the lock_state as the True, to try avoiding weird Maya 2023 bug.
                            # Sometimes an animation curve won't unlock unless you lock it again (even if it's already locked).
                            cmds.setAttr(attr_name, lock=True)
                            cmds.setAttr(attr_name, lock=lock_state)
    else:
        print_warning_from_caller("No anim_curves_nodes specified.")

########################################################################
#                                                                      #
#                       ANIMATION LAYER FUNCTIONS                      #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def filter_for_selected_animation_layers(animation_layers):
    """
    Filter a list of animation layers based on currently selected animation layers.

    :param animation_layers: List of animation layers to filter
    :type animation_layers: list
    :return: A filtered list of animation layers based on the selected layers
    :rtype: list

    """
    tool_name = "AnimLayerTab"
    selected_layers = cmds.treeView(tool_name + "animLayerEditor", query=True, selectItem=True)
    if not selected_layers:
        print_warning_from_caller("No animation layers are selected.")
        return

    if selected_layers == ["BaseAnimation"]:
        print_warning_from_caller("Only BaseAnimation layer is selected. Select other animation layers to reset selected objects on.")
        return

    if "BaseAnimation" in animation_layers:
        animation_layers.remove("BaseAnimation")
        print("Ignoring the BaseAnimation layer as a selected animation layer.")
        return

    # Remove anything in animation_layers that is not in selected_layers.
    animation_layers = [animLayer for animLayer in animation_layers if animLayer in selected_layers]

    if not animation_layers:
        print_warning_from_caller("No selected animation layers connected.")
        return

    return animation_layers

# ------------------------------------------------------------------------------ #
def find_layered_attributes(obj, filter_selected_animation_layers=False):
    """
    Find attributes connected to the specified object that are on animation layers.

    :param obj: The object for which layered attributes are to be found.
    :type obj: str
    :param filter_selected_animation_layers: Whether the script should only process selected animation layers.
    :type filter_selected_animation_layers: bool
    :return: A dictionary mapping animation layers to their respective layered attributes.
    :rtype: dict or None


    :Example:

    >>> result = find_layered_attributes(obj, filter_selected_animation_layers=False)
    >>> print(result)
    {'AnimLayer1': ['translateX', 'translateY', 'translateZ'], 'AnimLayer2': ['rotateX', 'rotateY', 'rotateZ']}

    """
    # ---------------------------------------
    # 01. GET CONNECTED ANIMATION LAYERS.
    # ---------------------------------------
    animation_layers = cmds.listConnections(obj, type="animLayer")
    if not animation_layers:
        print_warning_from_caller("No animation layers connected.")
        return
    # Remove duplicates.
    animation_layers = list(set(animation_layers))

    if filter_selected_animation_layers:
        animation_layers = filter_for_selected_animation_layers(animation_layers)

    # ---------------------------------------
    # 01. GET CONNECTED ATTRIBUTES.
    # ---------------------------------------
    # Get shape node, to ignore later.
    shape_node = cmds.listRelatives(obj, shapes=True)
    if shape_node:
        shape_node = shape_node[0]
    else:
        shape_node = None

    layered_attributes_dict = {}

    for layer in animation_layers:
        long_name_layered_attributes = cmds.animLayer(layer, query=True, attribute=True)
        if long_name_layered_attributes:

            layer_attributes = []
            for attr in long_name_layered_attributes:
                # Ignore shape node attributes.
                if not shape_node or (not attr.startswith(shape_node + ".") and attr.startswith(obj + ".")):
                    attr_names = attr.split('.')[-1]
                    if attr_names not in layer_attributes:
                        layer_attributes.append(attr_names)

            layered_attributes_dict[layer] = layer_attributes

    return layered_attributes_dict

# ------------------------------------------------------------------------------ #
def reset_animation_layer_keys_at_currentTime(filter_selected_animation_layers=False, reset_non_numeric_attributes=False, reset_selected_attributes=False):
    """
    Resets animation layer keys at the current time for the specified objects.
    This works the same as setting an animation layer's weight to 0, setting a key to store the current pose frame, then restoring its weight.

    :param filter_selected_animation_layers: If True, reset only for the currently selected animation layers.
    :type filter_selected_animation_layers: bool
    :param reset_non_numeric_attributes: If True, reset non-numeric attributes.
    :type reset_non_numeric_attributes: bool
    :param reset_selected_attributes: If True, reset only the selected attributes on the objects.
    :type reset_selected_attributes: bool

    :Example:

    >>> reset_animation_layer_keys_at_currentTime(
    ...     filter_selected_animation_layers=True,
    ...     reset_non_numeric_attributes=False,
    ...     reset_selected_attributes=True
    ... )

    """
    sel = get_selection()
    if not sel:
        print_warning_from_caller("Nothing is selected.")

    # ---------------------------------------
    # 01. OPTIONAL - CHECK IF ANIMATION LAYERS ARE HIGHLIGHTED.
    # ---------------------------------------
    if filter_selected_animation_layers:
        tool_name = "AnimLayerTab"
        selected_layers = cmds.treeView(tool_name + "animLayerEditor", query=True, selectItem=True)
        if not selected_layers:
            print_warning_from_caller("No animation layers are highlighted.")
            return

    # ---------------------------------------
    # 01. CHECK IF ANY CONNECTED ANIMATION LAYERS ARE LOCKED OR MUTED.
    # ---------------------------------------
    connected_animation_layers = []

    for obj in sel:
        animation_layers = cmds.listConnections(obj, type="animLayer")
        for layer in animation_layers:
            connected_animation_layers.append(layer)
    # Remove duplicates.
    connected_animation_layers = list(set(connected_animation_layers))

    if filter_selected_animation_layers:
        connected_animation_layers = filter_for_selected_animation_layers(connected_animation_layers)

    if connected_animation_layers:
        for layer in connected_animation_layers:
            mute_state = cmds.getAttr(layer + ".mute")
            lock_state = cmds.getAttr(layer + ".lock")

            if mute_state and lock_state:
                print_warning_from_caller(f"\"{layer}\" is muted and locked.")
                return
            elif mute_state:
                print_warning_from_caller(f"\"{layer}\" is muted.")
                return
            elif lock_state:
                print_warning_from_caller(f"\"{layer}\" is locked.")
                return
    else:
        print_warning_from_caller("No connection found to queried animation layers.")
        return

    # ---------------------------------------
    # 01. RESET.
    # ---------------------------------------
    reset_to_default(
        selection=sel, 
        attrsToReset=None, 
        reset_selected_attributes=reset_selected_attributes, 
        reset_non_numeric_attributes=reset_non_numeric_attributes, 
        nullify_animation_layers=True, 
        nullify_only_selected_animation_layers=filter_selected_animation_layers)

########################################################################
#                                                                      #
#                          ATTRIBUTE FUNCTIONS                         #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def clear_keys():
    """
    Clear animation keys for selected attributes or all keyable attributes of selected objects.
    This function ensures that the animation curves of attributes to clear will be unlocked.

    """
    selection = get_selection()
    selected_attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
    object_attribute_names_to_clear = []

    # ---------------------------------------
    # 01. OPTION A - IF ATTRIBUTES ARE SELECTED.
    # ---------------------------------------
    if selected_attributes:
        selected_object_attribute_names = []
        for item in selection:
            existing_attributes = []
            for attr in selected_attributes:
                if cmds.attributeQuery(attr, node=item, exists=True):
                    existing_attributes.append(attr)
                else:
                    continue
            # Ignore locked, muted and/or constrained object attributes.
            valid_object_attribute_names = filter_attributes(attributes=existing_attributes, filter_locked=True, filter_muted=True, filter_constrained=False) 
            for obj_attr in valid_object_attribute_names:
                object_attribute_names_to_clear.append(obj_attr)          
         
        # Ensure the attributes' animation curves are unlocked.
        animation_curves = get_animation_curves_from_object_attributes(object_attributes=object_attribute_names_to_clear)
        set_animation_curves_lock_state(animation_curves, lock_state=False)
             
        cmds.cutKey(object_attribute_names_to_clear) 
        
    # ---------------------------------------
    # 01. OPTION B - IF NO ATTRIBUTES ARE SELECTED.
    # ---------------------------------------             
    else:
        for item in selection:
            keyable_attributes = cmds.listAttr(item, keyable=True)
            # Ignore locked, muted and/or constrained object attributes.
            valid_object_attribute_names = filter_attributes(attributes=keyable_attributes, filter_locked=True, filter_muted=True, filter_constrained=False)
            for obj_attr in valid_object_attribute_names:
                object_attribute_names_to_clear.append(obj_attr)

        # Ensure the attributes' animation curves are unlocked.
        animation_curves = get_animation_curves_from_object_attributes(object_attributes=object_attribute_names_to_clear)
        set_animation_curves_lock_state(animation_curves, lock_state=False)
            
        cmds.cutKey(object_attribute_names_to_clear)
            
    # Reselect selection, to refresh Graph Editor.
    # Otherwise it might not show that animation curves have been untemplated, until reinteracting with it.
    cmds.select(selection, replace=True)

# ------------------------------------------------------------------------------ #
def reset_to_default(selection=None, attrsToReset=None, reset_selected_attributes=False, reset_non_numeric_attributes=False, nullify_animation_layers=True, nullify_only_selected_animation_layers=False):
    """
    This function has two main uses:
        - Reset specified attributes to their default values.
        - Or nullify animation layers for selected objects.

    Credit
    -------
    Fernando Ortega: This function was originally adapted from Ortega's reset_to_default.py script: https://animtd.gumroad.com/l/reset_to_default

    :param selection: List of objects to reset attributes for.
    :type selection: list
    :param attrsToReset: List of attributes to reset. If None, resets all keyable attributes.
    :type attrsToReset: list, optional
    :param reset_selected_attributes: If True, resets only selected attributes in the Channel Box.
    :type reset_selected_attributes: bool
    :param reset_non_numeric_attributes: If True, skips resetting non-numeric attributes.
    :type reset_non_numeric_attributes: bool
    :param nullify_animation_layers: If True, nullify animation layer keys on the current frame.
    :type nullify_animation_layers: bool
    :param nullify_only_selected_animation_layers: If True, nullify only selected animation layers.
    :type nullify_only_selected_animation_layers: bool

    :Example:

    >>> reset_to_default(
    ...     selection=["pSphere1", "pSphere2"],
    ...     attrsToReset=["translateX", "rotateY"],
    ...     reset_selected_attributes=True,
    ...     reset_non_numeric_attributes=False,
    ...     nullify_animation_layers=True,
    ...     nullify_only_selected_animation_layers=False
    ... )

    """
    #############################################################################
    # STEP 1: Get selection.

    selection = get_selection()

    #############################################################################
    # STEP 2: Reset every selection object.

    for obj in selection:
        # ---------------------------------------
        # 02. GET ATTRIBUTES TO RESET.
        # ---------------------------------------
        if not attrsToReset:
            if reset_selected_attributes:
                # Reset selected channels, if nothing is selected then reset all keyable.
                attrsToReset = get_selected_channels() or cmds.listAttr(obj, keyable=True)
            else:
                attrsToReset = cmds.listAttr(obj, keyable=True)

        if attrsToReset:
            # ---------------------------------------
            # 03. OPTION A - NULLIFY ANIMATION LAYERS.
            # ---------------------------------------
            if nullify_animation_layers:
                if nullify_only_selected_animation_layers:
                    layered_attributes = find_layered_attributes(obj, filter_selected_animation_layers=True)
                else:
                    layered_attributes = find_layered_attributes(obj, filter_selected_animation_layers=False)

                for layer, attributes in layered_attributes.items():
                    if reset_selected_attributes:
                        for attr in attributes:
                            if attr not in attrsToReset:
                                attributes.remove(attr)

                    if not reset_non_numeric_attributes:
                        for attr in attributes:
                            if not is_numeric_attribute(obj, attr):
                                attributes.remove(attr)

                    cmds.setKeyframe(obj, animLayer=layer, attribute=attributes, identity=True)

                # Set to current time again, to force the viewport to update with the change.
                current_time = cmds.currentTime(query=True)
                cmds.currentTime(current_time, edit=True)
                return

            # ---------------------------------------
            # 03. OPTION B - RESET ATTRIBUTES.
            # ---------------------------------------
            else:
                object_attribute_names_to_reset = []
                valid_attributes = []

                for attr in attrsToReset:
                    if cmds.attributeQuery(attr, node=obj, exists=True):
                        if not reset_non_numeric_attributes:
                            if not is_numeric_attribute(obj, attr):
                                continue
                        valid_attributes.append(attr)
                    else:
                        continue

                valid_object_attribute_names = filter_attributes(attributes=valid_attributes, filter_locked=True, filter_muted=True, filter_constrained=True)
                
                for obj_attr in valid_object_attribute_names:
                    object_attribute_names_to_reset.append(obj_attr)          

                # Ensure the attributes' animation curves are unlocked.
                animation_curves = get_animation_curves_from_object_attributes(object_attributes=object_attribute_names_to_reset)
                set_animation_curves_lock_state(animation_curves, lock_state=False)

                # Need to tidy this whole object_attribute_names_to_reset to be less convoluted. Maybe use a dict instead for what valid_oject_attribute_names returns?
                for obj_attr in object_attribute_names_to_reset:
                    attr = obj_attr.split('.')[-1]
                    obj = obj_attr.split('.')[0]
                    defaultValue = cmds.attributeQuery(attr, node=obj, listDefault=True)[0]
                    cmds.setAttr(obj_attr, defaultValue)
                    cmds.setKeyframe(obj_attr)

        else:
            print_warning_from_caller('Nothing to reset')
            return

########################################################################
#                                                                      #
#                             IS FUNCTIONS                             #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def is_attribute_muted(obj_attr):
    """
    Check if the specified object attribute is muted.

    :param obj_attr: The object attribute to check for muting.
    :type obj_attr: str
    :return: True if the attribute is muted.
    :rtype: bool

    :Example:

    >>> result = is_attribute_muted("pSphere1.translateX")
    >>> print(result)
    True

    """
    source_nodes = cmds.listConnections(obj_attr, source=True, type="mute")
    if source_nodes:
        return cmds.getAttr("{}.mute".format(source_nodes[0]))

    return False

# ------------------------------------------------------------------------------ #
def is_constrained(node):
    '''
    Check if the specified node is constrained.

    Original Creators
    ----------
    Tom Bailey: From tbAnimTools: https://github.com/tb-animator/tbAnimTools
        From version: 2024-01-03621:57:
        isConstrained() in tb_functions.py: line 1137

    :param node: The node to check for constraints
    :type node: str
    :return: A tuple
             - is_constrained: True if the node is constrained
             - constraint_nodes: List of constraint nodes connected to the node
             - constraint_relatives: List of constraint relatives
    :rtype: (bool, list, list)

    :Example:

    >>> is_constrained, constraint_nodes, constraint_relatives = is_constrained('pSphere1')
    >>> print(is_constrained)
    True
    >>> print(constraint_nodes)
    ['pairBlend1]
    >>> print(constraint_relatives)
    ['pSphere1_pointConstraint1']

    '''
    accepted_constraint_types = ['pairBlend', 'constraint']
    conns = cmds.listConnections(node, source=True, destination=False, plugs=False)
    if not conns:
        return False, None, None
    conns = [conn for conn in list(set(conns)) if cmds.objectType(conn) in accepted_constraint_types]
    if conns:
        constraint_relatives = cmds.listRelatives(node, type='constraint')
        return True, conns, constraint_relatives
    return False, None, None

# ------------------------------------------------------------------------------ #
def is_group_null(obj):
    """
    Check if the specified object is a group null node.

    :param obj: The object to check.
    :type obj: str
    :return: True if the object is a group null.
    :rtype: bool

    """
    return cmds.objectType(obj) == 'transform' and not cmds.listRelatives(obj, shapes=True) and cmds.listRelatives(obj, children=True, type='transform')

# ------------------------------------------------------------------------------ #
def is_numeric_attribute(obj, attr):
    """
    Check if an object's specified attribute is a numeric type.

    :param obj: The object to check.
    :type obj: str
    :param attr: The attribute to check.
    :type attr: str
    :return: True if the attribute is numeric.
    :rtype: bool

    """
    object_attribute_name = f"{obj}.{attr}"

    if not cmds.attributeQuery(attr, node=obj, exists=True):
        # cmds.warning(f"Attribute \"{attr}\" not found on {obj}")
        return

    attrType = cmds.getAttr(object_attribute_name, type=True)
    return attrType in ["float", "bool", "doubleLinear", "doubleAngle", "double"]

########################################################################
#                                                                      #
#                           FILTER FUNCTIONS                           #
#                                                                      #
########################################################################

def filter_attributes(selection=None, attributes=None, filter_locked=True, filter_muted=True, filter_constrained=True):
    """
    Filter attributes based on specified conditions for the given selection.

    :param selection: List of objects to filter attributes for.
    :type selection: list, optional
    :param attributes: List of attributes to filter.
    :type attributes: list, optional

    :param filter_locked: If True, filters out locked attributes.
    :type filter_locked: bool
    :param filter_muted: If True, filters out muted attributes.
    :type filter_muted: bool
    :param filter_constrained: If True, filters out constrained attributes.
    :type filter_constrained: bool
    :return: List of valid object attribute names based on the specified conditions.
    :rtype: list

    :Example:

    >>> result = filter_attributes(
    ...     selection=["pSphere1", "pSphere2"],
    ...     attributes=["translateX", "rotateY"],
    ...     filter_locked=True,
    ...     filter_muted=True,
    ...     filter_constrained=True
    ... )
    >>> print(result)
    ['pSphere1.translateX', 'pSphere2.rotateY']

    """
    if not selection:
        selection = get_selection()
        
    if not attributes:
        # attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
        attributes = cmds.listAttr(selection, keyable=True)

    valid_attributes = []
    for obj in selection:
        for attr in attributes:
            object_attribute_name = f"{obj}.{attr}"
            
            if cmds.objExists(object_attribute_name):
                if filter_locked:
                    if cmds.getAttr(object_attribute_name, lock=True):
                        continue
                if filter_muted:
                    if is_attribute_muted(object_attribute_name):
                        continue
                if filter_constrained:
                    has_constraint, conns, constraint_relatives = is_constrained(object_attribute_name)
                    if has_constraint:
                        continue
                
                valid_attributes.append(object_attribute_name)
    return valid_attributes

########################################################################
#                                                                      #
#                             GET FUNCTIONS                            #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def get_animation_curves_from_object_attributes(object_attributes=None):
    """
    Get animation curves connected to specified object attributes.

    :param object_attributes: List of object attributes to query animation curves.
    :type object_attributes: list or None
    :return: List of animation curves connected to the specified object attributes.
    :rtype: list

    :Example:

    >>> curves = get_animation_curves_from_object_attributes(object_attributes=["pSphere1.translateX", "pSphere1.rotateY"])
    >>> print(curves)
    ['pSphere1_translateX', 'pSphere1_rotateY']

    """
    if not object_attributes:
        display_viewport_warning("No object_attributes specified.")

    for obj_attr in object_attributes:
        curve_types = ["animCurveTL", "animCurveTU", "animCurveTA", "animCurveTT"]
        curves = []
        for curve_type in curve_types:
            connected_curves = cmds.listConnections(object_attributes, type=curve_type, destination=False, source=True) or []
            curves.extend(connected_curves)

    return curves

# ------------------------------------------------------------------------------ #
def get_channel_from_anim_curve(curve, plugs=True):
    """
    Get the channel associated with the given animation curve.
    
    Original Creators:
    ----------
    Morgan Loomis: From ml_utilities (Revision 36): 
        http://morganloomis.com/tool/ml_utilities/
        getChannelFromAnimCurve(): line 371

    :param curve: The animation curve to query for the associated channel.
    :type curve: str
    :param plugs: If True, returns plugs (attributes).
    :type plugs: bool
    :return: The channel associated with the animation curve.
    :rtype: str

    :Example:

    >>> result = get_channel_from_anim_curve('pSphere2_translateX')
    >>> print(result)
    'pSphere2.translateX'

    """
    #we need to save the attribute for later.
    attr = ''
    if '.' in curve:
        curve, attr = curve.split('.')

    nodeType = cmds.nodeType(curve)
    if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
        source = cmds.listConnections(curve+'.output', source=False, plugs=plugs)
        if not source and nodeType=='animBlendNodeAdditiveRotation':
            #if we haven't found a connection from .output, then it may be a node that uses outputX, outputY, etc.
            #get the proper attribute by using the last letter of the input attribute, which should be X, Y, etc.
            #if we're not returning plugs, then we wont have an attr suffix to use, so just use X.
            attrSuffix = 'X'
            if plugs:
                attrSuffix = attr[-1]

            source = cmds.listConnections(curve+'.output'+attrSuffix, source=False, plugs=plugs)
        if source:
            nodeType = cmds.nodeType(source[0])
            if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
                return get_channel_from_anim_curve(source[0], plugs=plugs)
            return source[0]

# ------------------------------------------------------------------------------ #
def get_selected_channels():
    """ 
    Get selected attributes in the Channel Box.
    
    Original Creators:
    ----------
    Fernando Ortega: From Ortega's reset_to_default.py script:
        https://animtd.gumroad.com/l/reset_to_default

    :return: List of selected attributes in the Channel Box.
    :rtype: list

    :Example:

    >>> result = get_selected_channels()
    >>> print(result)
    ['pSphere1.translateX', 'pSphere1.translateY']

    """
    channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')  # fetch maya's main channelbox
    selectedAttrs = []

    shapeAttrs = cmds.channelBox(channelBox, q=True, selectedShapeAttributes=True)
    mainAttrs = cmds.channelBox(channelBox, q=True, selectedMainAttributes=True)
    inputAttrs = cmds.channelBox(channelBox, q=True, selectedHistoryAttributes=True)

    if shapeAttrs:
        selectedAttrs.extend(shapeAttrs)

    if mainAttrs:
        selectedAttrs.extend(mainAttrs)

    if inputAttrs:
        selectedAttrs.extend(inputAttrs)

    return selectedAttrs

# ------------------------------------------------------------------------------ #
def get_selection():
    """
    Get the current selection as a list, even if only one item is selected.

    :return: List of selected objects.
    :rtype: list

    """

    selection = cmds.ls(selection=True)
    if selection:
        # If selection is just an instance of a string (like when using a for loop, like "for obj in selection:"), convert it to a list.
        if isinstance(selection, str):
            selection = [selection]
        return selection
    else:
        display_viewport_warning("No selected objects found.")
        return [] 

########################################################################
#                                                                      #
#                           MESSAGE FUNCTIONS                          #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def print_warning_from_caller(message):
    """
    A function made to find source of bugs easier.
    """
    caller_function_name = inspect.currentframe().f_back.f_code.co_name
    cmds.warning(f"{message}\n    from {caller_function_name}()")

# ------------------------------------------------------------------------------ #
def display_viewport_warning(message, position='midCenterTop'):
    """
    Display a warning message in the viewport.
    
    Original Creators:
    ----------
    Morgan Loomis: From ml_utilities (Revision 36): 
        http://morganloomis.com/tool/ml_utilities/
        message(), line 868
    """
    caller_function_name = inspect.currentframe().f_back.f_code.co_name

    OpenMaya.MGlobal.displayWarning(message)
    fadeTime = min(len(message)*150, 2000)
    cmds.inViewMessage( message=f"{message}\n\n    Warning from {caller_function_name}()", pos=position, fade=True, fadeStayTime=fadeTime, dragKill=True)

########################################################################
#                                                                      #
#                          SELECT FUNCTIONS                            #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def select_group_nulls_in_scene():
    """
    Select all group nodes in the scene.
    """
    all_dag_objects = cmds.ls(dag=True, long=True)

    group_nulls = [obj for obj in all_dag_objects if is_group_null(obj)]
    cmds.select(group_nulls, replace=True)

# ------------------------------------------------------------------------------ #
def select_joints_under_selected_objects():
    """
    Select all joints under selected items in the Outliner.
    """
    selection = get_selection()
    hierarchy_joints = []
    
    for item in selection:
        cmds.select(item, hierarchy=True)
        joints = cmds.ls(selection=True, type="joint")
        hierarchy_joints.extend(joints)

    cmds.select(deselect=True)
    if hierarchy_joints:
        cmds.select(hierarchy_joints, replace=True)
    else:
        cmds.warning("No joints found under", item)

# ------------------------------------------------------------------------------ #
def deselect_non_nurbs_curve_transforms():
    """
    Deselect non-NURBS curve transform nodes in the current selection.

    """
    selection = get_selection()
    nurbs_curve_transforms = [obj for obj in selection if cmds.objectType(obj) == 'transform' and cmds.listRelatives(obj, shapes=True, type='nurbsCurve')]
    cmds.select(nurbs_curve_transforms, replace=True)
