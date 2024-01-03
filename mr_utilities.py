"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_utilities.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# CREDIT: Morgan Loomis
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of short and/or support functions.
# Individual tools will mention if this script is required.
#
# Inspired by Morgan Loomis' ml_tools library:
# http://morganloomis.com/tool/ml_utilities/
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_utilities
importlib.reload(mr_utilities)

# USE ANY OF THE SUPPORT FUNCTIONS BELOW:
mr_utilities.#

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-01-02 - 0002:
#	- Working on adding docstrings.
# 	- Added reset key functions.
#	- Added animation layer functions.
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

########################################################################
#                                                                      #
#                           KEY FUNCTIONS                              #
#                                                                      #
########################################################################

def clear_keys():
	"""
	Highlighted attributes in the Channel Box will be cleared. 
	If no attributes are highlighted, all attributes of selected objects will be cleared.
	"""

	sel = cmds.ls(selection=True)
	if not sel:
		cmds.warning("No selected objects found.")
		return
		
	highlighted_attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
	if highlighted_attributes:
		for item in sel:
			for attr in highlighted_attributes:
				cmds.cutKey(item + "." + attr)
	else:
		cmds.cutKey()

# ------------------------------------------------------------------------------ #
def select_keys_at_currentTime(selection=None, attributes=None):
	"""
	Select keys at the current frame.

	Args:
		selection (list): Selected objects.
		attributes (list, optional): Specific attributes to select.

	Returns:
		None
	"""

	current_time = cmds.currentTime(query=True)

	if not selection:
		cmds.warning("Please specify a \"selection\" to process.")
		return

	cmds.selectKey(clear=True)
	if attributes:
		for obj in selection:
			cmds.selectKey(attributes, add=True, time=(current_time,))
	else:
		for obj in selection:
			cmds.selectKey(add=True, time=(current_time,))

########################################################################
#                                                                      #
#                     		 RESET FUNCTIONS                      	   #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def get_selected_channels():
	""" 
	Returns selected attributes in the Channel Box.
	Queries the main, the shape and the input attrs.

	Creators:
		Fernando Ortega: From Ortega's reset_to_default.py script.
			https://animtd.gumroad.com/l/reset_to_default

	Returns:
		list: Selected attributes in the Channel Box.

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
def reset_to_default(selection=None, attrsToReset=None, reset_selected_attributes=False, reset_non_numeric_attributes=False, nullify_animation_layers=True, nullify_only_selected_animation_layers=False):
	"""
	This function resets specified attributes to their default values.
	It supports nullifying animation layers and has options for selective resets.

	Args:
		selection (str or list, optional): Objects for which attributes are to be reset.
			If not provided, the current selection will be used.
		attrsToReset (list, optional): Specific attributes to reset.
		reset_selected_attributes (bool, optional): If True, reset attributes only on selected channels.
		reset_non_numeric_attributes (bool, optional): If True, non-numeric attributes will be skipped during the reset.
		nullify_animation_layers (bool, optional): If True, nullify attributes for animation layers.
		nullify_only_selected_animation_layers (bool, optional): If True, nullify only animation layers selected in the current object. Default is False.

	Returns:
		None

	Credit:
		Fernando Ortega: This function was originally adapted from Ortega's reset_to_default.py script.
			https://animtd.gumroad.com/l/reset_to_default

	"""

	#############################################################################
	# STEP 1: Get selection.

	# If selection is just an instance of a string (like when using a for loop, like "for obj in selection:"), convert it to a list.
	if isinstance(selection, str):
		selection = [selection]

	# If selection isn't provided, use the current selection.
	if not selection:
		selection = cmds.ls(selection=True)
		if not selection:
			print_warning_from_caller('Select something first.')
			return

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

		if not attrsToReset:
			print_warning_from_caller('Nothing to reset')
			return

		else:
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
				for attr in attrsToReset:
					if not reset_non_numeric_attributes:
						if not is_numeric_attribute(obj, attr):
							continue
					attrFullName = f"{obj}.{attr}"
					defaultValue = cmds.attributeQuery(attr, node=obj, listDefault=True)[0]
					cmds.setAttr(attrFullName, defaultValue)

# ------------------------------------------------------------------------------ #
def is_numeric_attribute(obj, attr):
	"""
	Check if an object's specified attribute is a numeric type.

	Args:
		obj (str): The name of the object.
		attr (str): The name of the attribute to check.

	Returns:
		bool: True if the attribute is a numeric type (float, bool, doubleLinear, doubleAngle, double), 
			  False otherwise.

	Example:
		>>> is_numeric_attribute("pSphere1", "translate")
		True
	"""
	attrFullName = f"{obj}.{attr}"
	attrType = cmds.getAttr(attrFullName, type=True)
	return attrType in ["float", "bool", "doubleLinear", "doubleAngle", "double"]

########################################################################
#                                                                      #
#                       ANIMATION LAYER FUNCTIONS                      #
#                                                                      #
########################################################################

def filter_for_selected_animation_layers(animation_layers):
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
	Get a dictionary of an object's attributes grouped by animation layers.

	Args:
		obj (str): A single object to process.
		filter_selected_animation_layers (bool): Choose whether to process only selected animation layers.

	Returns:
		dict or None: A dictionary representing object attributes grouped by animation layers, or None if no valid result.

	Example:
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
	Reset an object's offset on an animation layer.
	Works the same as setting an animation layer's weight to 0, setting a key to store the current pose frame, then restoring its weight.

	Args:
		filter_selected_animation_layers (bool): 
		reset_non_numeric_attributes (bool): 
		reset_selected_attributes (bool): 

	Returns:
		None
	"""

	sel = cmds.ls(selection=True) or []
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

# ------------------------------------------------------------------------------ #
def untemplate_anim_curve_nodes(anim_curve_nodes):
	"""
	Untemplate animcurves of selected objects to ensure everything can bake.

	Thanks to https://stackoverflow.com/questions/37816681/maya-python-trying-to-template-untemplate-channel
	for explaining how the MEL commands "doTemplateChannel" and "expandSelectionConnectionAsArray" work.

	Args:
		anim_curve_nodes(list):
	"""

	for node in anim_curve_nodes:
		if cmds.objExists(node):
			# print(node)
			# Unlock and untemplate channel box attributes.
			for attr in ['.ktv', '.kix', '.kiy', '.kox', '.koy']:
				attr_name = node + attr
				if cmds.attributeQuery(attr_name, node=node, exists=True):
					cmds.setAttr(attr_name, lock=0) 

# ------------------------------------------------------------------------------ #
def print_warning_from_caller(message):
	"""
	A function to try making it easier to diagnose bugs.
	"""
	caller_function_name = inspect.currentframe().f_back.f_code.co_name
	cmds.warning(f"{message}\n    from {caller_function_name}()")