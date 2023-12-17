"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_select_curve_tangents.py
# VERSION: 0001
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Selects the tangent handles of currently selected keys in the Graph Editor.
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------
import importlib
import mr_select_curve_tangents
importlib.reload(mr_select_curve_tangents)

# For toggling.
mr_select_curve_tangents.toggle()
# For specific selection:
mr_select_curve_tangents.main(tangent_handle='outTangent')
mr_select_curve_tangents.main(tangent_handle='inTangent')

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-17 - 0002:
# - Make script cycle between selecting inTangent and outTangent handles.
#
# 2023-12-17 - 0001:
# - First pass.
# ------------------------------------------------------------------------------ #
"""

import pymel.core as pm

def main(tangent_handle=None):
    if tangent_handle not in ['inTangent', 'outTangent']:
        pm.warning("Invalid tangent_handle. Please use 'inTangent' or 'outTangent'.")
        return

    anim_curves = pm.keyframe(query=True, name=True)

    for curve in anim_curves:
        keys = pm.keyframe(curve, query=True, timeChange=True, selected=True)

        for key in keys:
            if tangent_handle == 'inTangent':
                pm.selectKey(curve, add=True, inTangent=True, time=key)
                pm.selectKey(curve, remove=True, outTangent=True, time=key)
                
            elif tangent_handle == 'outTangent':
                pm.selectKey(curve, remove=True, inTangent=True, time=key)
                pm.selectKey(curve, add=True, outTangent=True, time=key)

# Toggle between tangent handles.
def toggle():
    global last_tangent_type

    if 'last_tangent_type' not in globals():
        last_tangent_type = 'inTangent'

    if last_tangent_type == 'inTangent':
        main(tangent_handle='outTangent')
        last_tangent_type = 'outTangent'
    else:
        main(tangent_handle='inTangent')
        last_tangent_type = 'inTangent'