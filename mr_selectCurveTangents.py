"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_selectCurveTangents.py
# VERSION: 0003
#
# CREATORS: Maria Robertson
# CREDIT: Morten Andersen (for original select_curve_tangents.py)
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Selects the tangent handles of currently selected keys in the Graph Editor.
#
# Adapted from Morten Anderson's select_curve_tangents.py, to switch between in and out tangents.
#   https://github.com/monoteba/maya/blob/master/scripts/animation/select_curve_tangents/select_curve_tangents.py
#
# Modified 
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------
import importlib
import mr_selectCurveTangents
importlib.reload(mr_selectCurveTangents)

# TO SELECT A SPECIFIC TANGENT TYPE:
mr_selectCurveTangents.main(tangent_handle='outTangent')
mr_selectCurveTangents.main(tangent_handle='inTangent')
# TO TOGGLE BETWEEN THEM:
mr_selectCurveTangents.toggle()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-01-12 - 0003:
#   - Updating script name and descriptions.
#
# 2023-12-17 - 0002:
# - Make script cycle between selecting inTangent and outTangent handles.
#
# 2023-12-17 - 0001:
# - First pass.
# ------------------------------------------------------------------------------ #
"""

import pymel.core as pm

def main(tangent_handle=None):
    """
    Select the specified tangent handle type for selected keys in the Graph Editor.

    :param tangent_handle: The tangent handle to manipulate, either 'inTangent' or 'outTangent'.
    :type tangent_handle: str
    """
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

# -------------------------------------------------------------------
def toggle():
    """
    Toggle between the select tangent of a key in the Graph Editor.
    """
    global last_tangent_type

    if 'last_tangent_type' not in globals():
        last_tangent_type = 'inTangent'

    if last_tangent_type == 'inTangent':
        main(tangent_handle='outTangent')
        last_tangent_type = 'outTangent'
    else:
        main(tangent_handle='inTangent')
        last_tangent_type = 'inTangent'