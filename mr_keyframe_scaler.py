"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_keyframe_scaler.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# CREDIT: David Peers (for the original keyScaler.mel script) - https://web.archive.org/web/20040816235635/http://andrewsilke.com/mel_info.html
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# "This script scales keys from the center of each curve from selected keys in the graph editor." - David Peers
#
# This script started as a Python conversion of David Peers' original keyScaler.mel script.
#
# Example hotkeys:
#   - SHIFT + !       = invert curves
#   - SHIFT + ALT + 1 = enlarge curves by 20%
#   - SHIFT + ALT + 2 = reduce curves by 20%
#
# INSTRUCTIONS:
# ---------------------------------------
# Select animation curves in the Graph Editor to scale.
# Set the scale amount in the Run Command.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_keyframe_scaler
importlib.reload(mr_keyframe_scaler)

# SET DESIRED SCALE AMOUNT.
# e.g.
mr_keyframe_scaler.main(-1)
mr_keyframe_scaler.main(1.2)
mr_keyframe_scaler.main(0.8)

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-28 - 0001:
#   - First pass of converting keyScaler.mel script to Python.
#   - If BaseAnimation is locked, temporarily unlock it, to allow anim_curves on animation layers to be scaled.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def main(scale_amount=None):
    base_anim_layer = "BaseAnimation"

    if cmds.objExists(base_anim_layer):
        was_locked = cmds.animLayer(base_anim_layer, query=True, lock=True)
        if was_locked:
            was_locked = cmds.animLayer(base_anim_layer, edit=True, lock=False)

    # Make array of selected curves.
    sel_curves = cmds.keyframe(query=True, name=True, selected=True)

    # Loop scaler for each curve.
    for curve in sel_curves:
        # Array for keys on a single curve.
        key_vals = cmds.keyframe(query=True, selected=True, valueChange=True, attribute=curve)
        key_index = cmds.keyframe(query=True, selected=True, indexValue=True, attribute=curve)
        index_size = len(key_index)
        index_last = key_index[index_size - 1]

        # Get the destination attribute from the list of connections
        curve_obj = cmds.listConnections(curve + ".output", plugs=True, destination=True)
        if curve_obj:
            curve_obj = curve_obj[0]
        else:
            continue  # Skip if there are no connections

        # Get the attribute type
        curve_attr = cmds.listAttr(curve_obj)

        max_key = -1000000
        min_key = 1000000

        # Scan keyframes for max and min values.
        for key in key_vals:
            max_key = max(max_key, key)
            min_key = min(min_key, key)

        mid_point = (max_key + min_key) / 2
        key_insert_start = int(key_index[0])
        key_insert_end = int(index_last)
     
        # Scale around center pivot - ts and tp are ineffectual for magnitude scaling
        cmds.scaleKey(
            curve_obj,
            includeUpperBound=False,
            timeScale=1,
            timePivot=52,
            index=(key_insert_start, key_insert_end),
            valueScale=scale_amount,
            valuePivot=mid_point,
            attribute=curve_attr
        )

    if cmds.objExists(base_anim_layer):
        if was_locked:
            cmds.animLayer(edit=True, lock=1, name=base_anim_layer)