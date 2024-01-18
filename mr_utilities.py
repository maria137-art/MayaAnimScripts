"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_utilities.py
# VERSION: 0018
#
# CREATORS: Maria Robertson
# CREDIT: Morgan Loomis, Tom Bailey
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of short support functions.
# Individual scripts in other files will mention if this script is required.
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

# ------------------------------------------------------------------------------ #
"""

import inspect
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from maya import OpenMaya

##################################################################################################################################################

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
        # print_warning_from_caller("No selected animation layers connected.")
        return
    return animation_layers

# ------------------------------------------------------------------------------ #
def set_selected_for_all_layers(state):
    # Python version of setSelectedForAllLayers from Autodesk Maya's layerEditor.mel, line 1220
    layers = cmds.ls(type='animLayer')
    for layer in layers:
        cmds.animLayer(layer, edit=True, selected=state)

##################################################################################################################################################

########################################################################
#                                                                      #
#                          ATTRIBUTE FUNCTIONS                         #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def clear_keys(reset_selected_attributes=True):
    """
    Clear animation keys for selected attributes or all keyable attributes of selected objects.
    This function ensures that the animation curves of attributes to clear will be unlocked.

    """
    selection = get_selection_generator()
    if not selection:
        return

    # ---------------------------------------
    # 01. GET VALID OBJECT ATTRIBUTES.
    # ---------------------------------------
    object_attributes_to_clear = []
    for item in selection:

        if reset_selected_attributes:
            attributes = get_selected_channels() or cmds.listAttr(item, keyable=True, unlocked=True)
        else:
            attributes = cmds.listAttr(item, keyable=True, unlocked=True)

        if attributes:
            valid_attributes = []
            for attr in attributes:
                # Check if it exists.
                if cmds.attributeQuery(attr, node=item, exists=True):

                    valid_attributes.append(attr)

            if valid_attributes:
                # Get the relevant object attribute names.
                valid_object_attributes = get_object_attributes(attributes=valid_attributes, filter_locked=True, filter_muted=True, filter_constrained=False, filter_connected=False) 

        else:
            print_warning_from_caller('No attributes to clear.')
            return

        # ---------------------------------------
        # 01. UNTEMPLATE ALL KEYABLE ANIMATION CURVES.
        # ---------------------------------------
        all_keyable_object_attributes = cmds.listAttr(item, keyable=True, unlocked=True, nodeName=True)
        if all_keyable_object_attributes:
            animation_curves = get_animation_curves_from_object_attributes(all_keyable_object_attributes)
        for curve in animation_curves:
            set_animation_curve_template_state(curve, lock_state=False)

    cmds.cutKey(valid_object_attributes) 

# ------------------------------------------------------------------------------ #
def reset_attributes_to_default_value(selection=None, attributes=None, reset_selected_attributes=False, reset_non_numeric_attributes=False):
    """
    Reset attributes of selected objects to their default values.

    Credit
    -------
    Fernando Ortega: This function was originally adapted from Ortega's reset_to_default.py script
        https://animtd.gumroad.com/l/reset_to_default
        Using version last downloaded on 2023-12-31: 

    :param selection: List of objects to reset attributes for. If None, uses the current selection.
    :type selection: List[str], optional
    :param attributes: List of attributes to reset. If None, reset all keyable and unlocked attributes.
    :type attributes: List[str], optional
    :param reset_selected_attributes: If True, reset only selected attributes in the Channel Box.
    :type reset_selected_attributes: bool
    :param reset_non_numeric_attributes: If True, reset only numeric attributes.
    :type reset_non_numeric_attributes: bool

    :Example:

    >>> mr_utilities.reset_attributes_to_default_value(
    ...     selection=None,
    ...     attributes=None,
    ...     reset_selected_attributes=True,
    ...     reset_non_numeric_attributes=False
    ... )
    
    """
    if not selection:
        selection = get_selection_generator()
    if not selection:
        return

    # ---------------------------------------
    # 01. DISABLE AUTOKEYFRAME, TO AVOID SPAM IN THE LOG.
    # ---------------------------------------
    original_autoKey_state = cmds.autoKeyframe(query=True, state=True)
    if original_autoKey_state: 
        cmds.autoKeyframe(state=False)

    # ---------------------------------------
    # 01. FOR EVERY OBJECT.
    # ---------------------------------------
    for obj in selection:

        # ---------------------------------------
        # 02. GET ATTRIBUTES.
        # ---------------------------------------
        if not attributes:
            if reset_selected_attributes:
                attributes = get_selected_channels() or cmds.listAttr(obj, keyable=True, unlocked=True)
            else:
                attributes = cmds.listAttr(obj, keyable=True, unlocked=True)

        # ---------------------------------------
        # 02. GET VAILD ATTRIBUTES.
        # ---------------------------------------
        if attributes:
            valid_attributes = []
            for attr in attributes:
                # Check if it exists.
                if cmds.attributeQuery(attr, node=obj, exists=True):

                    # Skip if non-numeric attributes should be ignored.
                    if not reset_non_numeric_attributes:
                        if not is_attribute_numeric(obj, attr):
                            continue
                    valid_attributes.append(attr)
                else:
                    continue
            if valid_attributes:
                valid_object_attributes = get_object_attributes(attributes=valid_attributes, filter_locked=True, filter_muted=True, filter_constrained=True, filter_connected=True)
        else:
            print_warning_from_caller('Nothing to reset')
            return

        # ---------------------------------------
        # 02. UNTEMPLATE ALL KEYABLE ANIMATION CURVES.
        # ---------------------------------------
        all_keyable_object_attributes = cmds.listAttr(obj, keyable=True, unlocked=True, nodeName=True)
        animation_curves = get_animation_curves_from_object_attributes(all_keyable_object_attributes)

        for curve in animation_curves:
            set_animation_curve_template_state(curve, lock_state=False)

    # ---------------------------------------
    # 01. RESET ATTRIBUTES TO DEFAULT VALUES.
    # ---------------------------------------
    for obj_attr in valid_object_attributes:
        obj, attr = obj_attr.split('.')

        # Get the default value and check if the attribute is keyed.
        defaultValue = cmds.attributeQuery(attr, node=obj, listDefault=True)
        if defaultValue:
            defaultValue = defaultValue[0]
            has_keyframes = cmds.keyframe(obj_attr, query=True, keyframeCount=True)

            try:
                # Using a try, as don't know yet how to query if an attribute is connected.
                # e.g. ERROR: setAttr: The attribute 'rivet.translateX' is locked or connected and cannot be modified.

                # Set the attribute to its default value.
                cmds.setAttr(obj_attr, defaultValue)
                # Only set keys if the attribute already is keyed.
                if has_keyframes:
                    cmds.setKeyframe(obj, attribute=attr, value=defaultValue)
            except:
                print(f"{obj_attr} could not be reset.")
            finally:
                continue

        else:
            # print(f"Attribute {attr} has no default value on object {obj}.")
            continue

    # ---------------------------------------
    # 01. RESTORE AUTOKEYFRAME STATE
    # ---------------------------------------
    if original_autoKey_state:
        cmds.autoKeyframe(state=True)
  
##################################################################################################################################################

########################################################################
#                                                                      #
#                          CONSTRAINT FUNCTIONS                        #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def constrain_unlocked_attributes(driver, target, mode):
    """
    Constrain unlocked attributes of the target to follow the driver.
    
    :param driver: The object to control the target.
    :type driver: str
    :param target: The object to be constrained.
    :type target: str
    :param mode: The type of constraints to use.
    :type mode: str

    """
    mode_functions = {
        "translate": (constrain_unlocked_translates,),
        "rotate": (constrain_unlocked_rotates,),
        "both": (constrain_unlocked_translates, constrain_unlocked_rotates),
    }

    if mode in mode_functions:
        for func in mode_functions[mode]:
            func(driver, target)
    else:
        display_viewport_warning("Invalid mode. Supported modes are 'both', 'translate', and 'rotate'.")

# ------------------------------------------------------------------------------ 
def constrain_unlocked_rotates(driver, item):
    """
    Create an orient constraint between the driver and the item, skipping locked attributes.

    :param driver: The object to control the target.
    :type driver: str
    :param item: The object to be constrained.
    :type item: str
    """
    # Check if rotate X, Y, Z are locked.
    skip_rot_axes = []
    if cmds.getAttr(item + ".rotateX", lock=True):
        skip_rot_axes.append("x")
    if cmds.getAttr(item + ".rotateY", lock=True):
        skip_rot_axes.append("y")
    if cmds.getAttr(item + ".rotateZ", lock=True):
        skip_rot_axes.append("z")

    if skip_rot_axes:
        if skip_rot_axes == ['x', 'y', 'z']:
            return
        else:
            # Apply orient constraint with skipping specified axes.
            cmds.orientConstraint(driver, item, maintainOffset=True, skip=skip_rot_axes)
    else:
        cmds.orientConstraint(driver, item, maintainOffset=True)

# ------------------------------------------------------------------------------ #
def constrain_unlocked_translates(driver, item):
    """
    Create a point constraint between the driver and the item, skipping locked attributes.

    :param driver: The object to control the target.
    :type driver: str
    :param item: The object to be constrained.
    :type item: str
    """
    # Check if translate X, Y, Z are locked.
    skip_trans_axes = []
    if cmds.getAttr(item + ".translateX", lock=True):
        skip_trans_axes.append("x")
    if cmds.getAttr(item + ".translateY", lock=True):
        skip_trans_axes.append("y")
    if cmds.getAttr(item + ".translateZ", lock=True):
        skip_trans_axes.append("z")

    if skip_trans_axes:
        if skip_trans_axes == ['x', 'y', 'z']:
            return
        else:
            # Apply point constraint with skipping specified axes.
            cmds.pointConstraint(driver, item, maintainOffset=True, skip=skip_trans_axes)
    else:
        cmds.pointConstraint(driver, item, maintainOffset=True)

##################################################################################################################################################

########################################################################
#                                                                      #
#                             IS FUNCTIONS                             #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def are_parents_visible(node):
    """
    Check if all parents of the given node are visible.

    :param node: The node to check for visibility.
    :type: str
    :return: True, if all parents are visible.
    :rtype: bool
    """

    # Set up recursive counter.
    rec_num = 0
    rec_limit = 1000
    # Start with the given node as the parent.
    parent = node

    # Recursion loop.
    while parent and rec_num < rec_limit:
        parent = cmds.listRelatives(parent, parent=True, fullPath=True)
        if not parent:
            break

        parent = parent[0]
        if not is_visible(parent):
            return False

        rec_num += 1

    return True

# ------------------------------------------------------------------------------ #
def is_attribute_connected_as_destination(obj_attr):
    """
    Check if an object's attribute is connected as a destination to certain types of nodes.

    :param object_attribute: The object's attribute to check
    :type object_attribute: str
    :return: True if the attribute is connected.
    :rtype: bool

    :Example:

    >>> object_attribute = "rivet.scaleX"
    >>> result = is_attribute_connected_as_destination(object_attribute)
    >>> print(result)
    False

    """
    obj, attr = obj_attr.split('.')
    source_connection = cmds.connectionInfo(obj_attr, sourceFromDestination=True)

    # nodes_to_check = [['pointOnSurfaceInfo','pos'],['loft','loft'],['fourByFourMatrix','mat'],['decomposeMatrix','dcp']]  
    nodes_to_check = ['pos','loft','mat','dcp']
    
    for node_info in nodes_to_check:
        if node_info in source_connection:
            return True
    
    return False

# ------------------------------------------------------------------------------ #
def is_attribute_muted(obj_attr):
    """
    Check if an object's attribute is muted.

    :param obj_attr: The object's attribute to check.
    :type obj_attr: str
    :return: True if the attribute is muted.
    :rtype: bool

    """
    source_nodes = cmds.listConnections(obj_attr, source=True, type="mute")
    if source_nodes:
        return cmds.getAttr("{}.mute".format(source_nodes[0]))

    return False

# ------------------------------------------------------------------------------ #
def is_attribute_numeric(obj, attr):
    """
    Check if an object's attribute is numeric.

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

# ------------------------------------------------------------------------------ #
def is_constrained(node):
    '''
    Check if the given node is constrained.
    Can be the object itself or a specified attribute.

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
    accepted_constraint_types = ['pairBlend', 'constraint', 'parentConstraint', 'pointConstraint', 'orientConstraint', 'scaleConstraint']
    connections = cmds.listConnections(node, source=True, destination=False, plugs=False)
    if not connections:
        return False, None, None

    # Get rid of duplicates.
    connections = list(set(connections))   
    accepted_connections = [conn for conn in connections if cmds.objectType(conn) in accepted_constraint_types]
    if accepted_connections:
        constraint_relatives = cmds.listRelatives(node, type='constraint')
        return True, accepted_connections, constraint_relatives
    else:
        return False, None, None

# ------------------------------------------------------------------------------ #
def is_current_panel_modelPanel():
    # Check the panel where the mouse cursor is over.
    modelPanel = cmds.getPanel(withFocus=True)

    # Check if the current panel is a modelPanel.
    if cmds.getPanel(typeOf=modelPanel) != "modelPanel":
        cmds.warning("The current panel is not a 3D view panel.")
    else:
        return modelPanel

# ------------------------------------------------------------------------------ #
def is_group_null(obj):
    """
    Check if the given node is a group null transform.

    :param obj: The node to check.
    :type obj: str
    :return: True if the object is a group null.
    :rtype: bool

    """   
    return cmds.objectType(obj) == 'transform' and not cmds.listRelatives(obj, shapes=True) and cmds.listRelatives(obj, children=True, type='transform')

# ------------------------------------------------------------------------------ #
def is_nurbs_curve(node):
    """
    Check if the given node is a NURBS curve transform node, containing a NURBS curve shape.

    :param node: The node to check.
    :type node: str
    :return: True if object is a NURBS curve transform.
    :rtype: bool

    """
    shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
    return any(cmds.nodeType(shape) == 'nurbsCurve' for shape in shapes)

# ------------------------------------------------------------------------------ #
def is_object_attribute_connected_to_referenced_animation_curve(object_attribute):
    """
    Check if the given node attribute is connected to an animation curve, that was created in a referenced file.

    :param object_attribute: The node attribute to check.
    :type object_attribute: str
    :return: True if the attribute is connected to an animation curve created in a referenced file.
    :rtype: bool

    :Example:

    >>> object_attribute = "pSphere1.translateX"
    >>> result = is_object_attribute_connected_to_referenced_animation_curve(object_attribute)
    >>> print(result)
    False

    """
    # Split the attribute into node and attribute name.
    node, attr = object_attribute.split('.')

    if cmds.attributeQuery(attr, node=node, exists=True):
        # Get the attribute's connection.
        connections = cmds.listConnections(f'{node}.{attr}', source=True, destination=False, plugs=True)

        if connections:
            for connection in connections:
                # Check if the connection is from a reference.
                if cmds.referenceQuery(connection, isNodeReferenced=True):
                    # cmds.warning(f"Ignoring {object_attribute} - it has keyes in its referenced file.")
                    return True
        else:
            # Check if the attribute has animation keys in the current scene.
            anim_curves = cmds.listAttr('{}.{}'.format(node, attr), string="*animCurve*")
            if anim_curves:
                return True

    return False

# ------------------------------------------------------------------------------ #
def is_transform(node):
    """
    Check if the given node is a transform.

    :param obj: The node to check.
    :type obj: str
    :return: True if the node is a transform type.
    :rtype: bool

    """

    return cmds.nodeType(node) == 'transform'

# ------------------------------------------------------------------------------ #
def is_visible(node):
    """
    Check if the given node is visible.

    :param node: The node to check.
    :type node: str
    :return: True if the object has both its visibility and lodVisibility set to on.
    :rtype: bool

    """
    visibility = cmds.getAttr(node + '.visibility')
    lod_visibility = cmds.getAttr(node + '.lodVisibility')
    return visibility and lod_visibility

##################################################################################################################################################

########################################################################
#                                                                      #
#                             GET FUNCTIONS                            #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def get_animation_curves_from_object_attributes(object_attributes, filter_referenced=True):
    """
    Get animation curves connected to given object attributes.

    :param object_attributes: List of object attributes (e.g., ["pSphere1.translateX", "pSphere1.rotateY"]).
    :type object_attributes: list
    :param  filter_referenced: If True, skip attributes on referenced nodes.
    :type filter_referenced: bool
    :return: Animation curve names connected to the given object attributes.
    :rtype: generator of str

    """
    for obj_attr in object_attributes:
        if filter_referenced:
            if is_object_attribute_connected_to_referenced_animation_curve(obj_attr):
                continue

        get_attr_connection = cmds.listConnections(obj_attr, destination=False, source=True)
        # This should be better than just formatting the attribute name to replace . and _, as if the object or attribute gets renamed,
        # it's animation curve won't be renamed and match it, unless its deleted and created again.
        if get_attr_connection:
            get_animation_curve = cmds.ls(get_attr_connection[0], type=("animCurveTL", "animCurveTU", "animCurveTA", "animCurveTT"))

            for curve in get_animation_curve:
                yield curve

# ------------------------------------------------------------------------------ #
def get_channel_from_animation_curve(curve, plugs=True):
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

    >>> result = get_channel_from_animation_curve('pSphere2_translateX')
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
                return get_channel_from_animation_curve(source[0], plugs=plugs)
            return source[0]

# ------------------------------------------------------------------------------ #
def get_keyed_nodes(objects_to_check=None):

    if objects_to_check is None:
        objects_to_check = cmds.ls(dag=True) or []

    keyed_objects = []

    for item in objects_to_check:
        # Check if any attribute is keyed directly.
        if cmds.listAttr(item, keyable=True, unlocked=True):
            keyed_objects.append(item)

    return keyed_objects
    
# ------------------------------------------------------------------------------ #
def get_layered_attributes(obj, filter_selected_animation_layers=False):
    """
    Find attributes connected to the specified object that are on animation layers.

    :param obj: The object for which layered attributes are to be found.
    :type obj: str
    :param filter_selected_animation_layers: Whether the script should only process selected animation layers.
    :type filter_selected_animation_layers: bool
    :return: A dictionary mapping animation layers to their respective layered attributes.
    :rtype: dict or None


    :Example:

    >>> result = get_layered_attributes(obj, filter_selected_animation_layers=False)
    >>> print(result)
    {'AnimLayer1': ['translateX', 'translateY', 'translateZ'], 'AnimLayer2': ['rotateX', 'rotateY', 'rotateZ']}

    >>> layered_attributes_dict = mr_utilities.get_layered_attributes(obj, filter_selected_animation_layers=True)
    >>> for layer, attributes in layered_attributes_dict.items():
    ...     print(layer)
    ...     print(attributes)
    AnimLayer1
    ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'visibility', 'scaleX', 'scaleY', 'scaleZ']
    
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
def get_object_attributes(selection=None, attributes=None, filter_locked=True, filter_muted=True, filter_constrained=True, filter_connected=True):
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
    :param filter_connected: If True, filters out connected attributes.
    :type filter_connected: bool
    :return: List of valid object attribute names based on the specified conditions.
    :rtype: list

    :Example:

    >>> result = get_object_attributes(
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
        selection = get_selection_generator()

    if not attributes:
        attributes = cmds.listAttr(selection, keyable=True)

    # Convert selection to a list if it's a single object name
    if isinstance(selection, str):
        selection = [selection]

    for obj in selection:
        for attr in attributes:
            object_attribute = f"{obj}.{attr}"

            if cmds.objExists(object_attribute):
                if filter_locked and cmds.getAttr(object_attribute, lock=True):
                    continue
                if filter_muted and is_attribute_muted(object_attribute):
                    continue
                if filter_constrained:
                    has_constraint, conns, constraint_relatives = is_constrained(object_attribute)
                    if has_constraint:
                        continue
                if filter_connected and is_attribute_connected_as_destination(object_attribute):
                    continue
                yield object_attribute

    """
    # Different ways to query if an object attribute exists.
    cmds.objExists(obj_attr)
    cmds.attributeQuery(attr, node=obj, exists=True)
    """

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

    shapeAttrs = cmds.channelBox(channelBox, query=True, selectedShapeAttributes=True)
    mainAttrs = cmds.channelBox(channelBox, query=True, selectedMainAttributes=True)
    inputAttrs = cmds.channelBox(channelBox, query=True, selectedHistoryAttributes=True)

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

# ------------------------------------------------------------------------------ #
def get_selection_generator():
    """
    Get the current selection as a generator, even if only one item is selected.

    :yield: Selected object.
    :rtype: str
    """
    selection = cmds.ls(selection=True)
    if selection:
        # If selection is just an instance of a string, yield it directly.
        if isinstance(selection, str):
            yield selection
        else:
            # If selection is a list, yield each item in the list.
            for obj in selection:
                yield obj
    else:
        display_viewport_warning("No selected objects found.")

##################################################################################################################################################

########################################################################
#                                                                      #
#                           MESSAGE FUNCTIONS                          #
#                                                                      #
########################################################################

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

# ------------------------------------------------------------------------------ #
def print_warning_from_caller(message):
    """
    A function made to find source of bugs easier.
    """
    caller_function_name = inspect.currentframe().f_back.f_code.co_name
    cmds.warning(f"{message}\n    from {caller_function_name}()")

##################################################################################################################################################

########################################################################
#                                                                      #
#                          SELECT FUNCTIONS                            #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def deselect_non_nurbs_curve_transforms():
    """
    Deselect non-NURBS curve transform nodes in the current selection.

    """
    selection = get_selection_generator()
    nurbs_curve_transforms = [obj for obj in selection if cmds.objectType(obj) == 'transform' and cmds.listRelatives(obj, shapes=True, type='nurbsCurve')]
    cmds.select(nurbs_curve_transforms, replace=True)

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
    selection = get_selection_generator()
    hierarchy_joints = []
    
    for item in selection:
        cmds.select(item, hierarchy=True)
        joints = cmds.ls(selection=True, type="joint")
        hierarchy_joints.extend(joints)

    cmds.select(deselect=True)
    if hierarchy_joints:
        cmds.select(hierarchy_joints, replace=True)
    else:
        display_viewport_warning("No joints found under", item)


##################################################################################################################################################

########################################################################
#                                                                      #
#                           SET STATE FUNCTIONS                        #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def set_animation_curve_template_state(animation_curves, lock_state=False):
    """
    Set the lock state of specified animation curve nodes.
    
    Thanks to DrWeeny at StackOverflow for explaining how the MEL commands "doTemplateChannel" and "expandSelectionConnectionAsArray" work:
    https://stackoverflow.com/questions/37816681/maya-python-trying-to-template-untemplate-channel


    :param anim_curve_nodes: List of animation curve nodes
    :type anim_curve_nodes: list
    :param lock_state: The lock state to be set
    :type lock_state: bool

    """
    attributes_to_unlock = ['.ktv', '.kix', '.kiy', '.kox', '.koy']

    if not animation_curves:
        display_viewport_warning("No animation_curves were given.")

    # If animation_curves is just an instance of a string, convert it to a list.
    if isinstance(animation_curves, str):
        animation_curves = [animation_curves]

    for curve in animation_curves:
        for k_attr in attributes_to_unlock:
            full_name = f"{curve}{k_attr}"
            if cmds.objExists(full_name):
                cmds.setAttr(full_name, lock=lock_state)

"""
##################################################################################################################################################
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-16- 0018:
#   - Moving following functions into mr_animLayers.py
#       - reset_animation_layer_keys_at_currentTime()
#       - nullify_animation_layer_keys()
#   - Added functions:
#       - set_selected_for_all_layers()
#       - are_parents_visible()
#
# 2024-01-15- 0017:
#   - clear_keys()
#   -   Adding check for all_keyable_object_attributes to avoid NoneType error.
#   - Moving CHANGELOG to the bottom.
#
# 2024-01-14- 0016:
#   - constrain_unlocked_attributes()
#       - Fixing bug where it wouldn't trigger constraints.
#
# 2024-01-14- 0015:
#   - reset_attributes_to_default_value()
#       - Now uses set_animation_curve_template_state().
#       - Updated try, except, finally.
#
# 2024-01-14- 0014:
#   - Added is_object_attribute_connected_to_referenced_animation_curve().
#   - Updated get_animation_curves_from_object_attributes() to use is_object_attribute_connected_to_referenced_animation_curve().
#       - Now it should only ignore animation curves that were created originally in the referenced file.
#
# 2024-01-14- 0013:
#   - Using get_selection_generator() in more functions.
#   - Adding is_attribute_connected_as_destination().   
#
# 2024-01-14- 0012:
#   - Readding missing descriptions.
#   - clear_keys()
#       - Untemplate animation curves before clearing.
#       - Added option to disable clearing only selected keys.
#
# 2024-01-14- 0011:
#   - Adding more accepted_constraint_types to is_constrained().
#   - Minor formatting.
#
# 2024-01-14- 0010:
#   - Simplifying clear_keys().
#   - Reordered functions.
#   - Adding functions from mr_selectVisibleControl.py.
#   - Renaming functions:
#       - find_layered_attributes to get_layered_attributes().
#       - filter_attributes() to get_object_attributes().
#       - reset_to_default() to reset_attributes_to_default_value().
#   - Learnt how efficient Python generators are. Started incorporating them more.
#   - Reworked reset_attributes_to_default_value() to use generators to work faster.
#
# 2024-01-08- 0009:
#   - reset_to_default()
#       - Disabling script until freezes solved.
#       - Added checks for it defaultValue is None.
#
# 2024-01-08- 0008:
#   - reset_to_default()
#       Add variable checks.
#
# 2024-01-08- 0007:
#   - reset_to_default()
#       - Don't set keys if attribute wasn't keyed. Use setAttr instead then. 
#
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
# ---------------------------------------
##################################################################################################################################################
"""