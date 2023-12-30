"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_keyScaler.py
# VERSION: 0003
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
import mr_keyscaler
importlib.reload(mr_keyscaler)

# SET DESIRED SCALE AMOUNT.
# e.g.
mr_keyscaler.main(-1)
mr_keyscaler.main(1.2)
mr_keyscaler.main(0.8)

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-28 - 0002:
#   - Updating name.
#
# 2023-12-28 - 0002:
#   - Stopped script from scaling multiple curves altogether rather than individually.
#
# 2023-12-28 - 0001:
#   - First pass of converting keyScaler.mel script to Python.
#   - If BaseAnimation is locked, temporarily unlock it, to allow anim_curves on animation layers to be scaled.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def main(scale_amount=None):

    # ------------------------------------------------------------------- 
    # 01. CHECK SELECTED ANIMATION CURVES
    # -------------------------------------------------------------------

    sel_curves = cmds.keyframe(query=True, name=True, selected=True)
    if not sel_curves:
        cmds.warning("No animation curves selected.")
        return

    # ------------------------------------------------------------------- 
    # 01. CHECK IF BASE ANIMATION LAYER IS LOCKED.
    # -------------------------------------------------------------------
    base_anim_layer = "BaseAnimation"

    if cmds.objExists(base_anim_layer):
        was_locked = cmds.animLayer(base_anim_layer, query=True, lock=True)
        if was_locked:
            was_locked = cmds.animLayer(base_anim_layer, edit=True, lock=False)

    # ------------------------------------------------------------------- 
    # 01. SCALE EACH CURVE.
    # -------------------------------------------------------------------
    for curve in sel_curves:
        # Make an array for keys on a single curve.
        key_vals = cmds.keyframe(curve, query=True, selected=True, valueChange=True)
        key_index = cmds.keyframe(curve, query=True, selected=True, indexValue=True)
        index_size = len(key_index)
        index_last = key_index[index_size - 1]

        # Get the destination attribute from the list of connections.
        curve_obj = cmds.listConnections(curve, plugs=True)
        curve_attr = cmds.listAttr(curve_obj[0])

        max_key = -1000000
        min_key = 1000000

        # Scan keyframes for max and min values.
        for key in key_vals:
            max_key = max(max_key, key)
            min_key = min(min_key, key)

        mid_point = (max_key + min_key) / 2
        key_insert_start = int(key_index[0])
        key_insert_end = int(index_last)

        # Scale around center pivot.
        cmds.scaleKey(
            curve_obj[0],
            includeUpperBound=False,
            index=(key_insert_start, key_insert_end),
            valueScale=scale_amount,
            valuePivot=mid_point,
            attribute=curve_attr[0]
        )

    # ------------------------------------------------------------------- 
    # 01. RESTORE LOCK STATE OF BASE ANIMATION LAYER.
    # ------------------------------------------------------------------- 
    if cmds.objExists(base_anim_layer):
        if was_locked:
            cmds.animLayer(edit=True, lock=1, name=base_anim_layer)