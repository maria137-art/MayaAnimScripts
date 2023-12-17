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

# Use one of the following commands:
mr_select_curve_tangents.main(inTangent=True, outTangent=False)
mr_select_curve_tangents.main(inTangent=False, outTangent=True)

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-17 - 0001:
# - First pass.
# ------------------------------------------------------------------------------ #
"""

import pymel.core as pm

def main(inTangent=None, outTangent=None):
	anim_curves = pm.keyframe(query=True, name=True)

	for curve in anim_curves:
		keys = pm.keyframe(curve, query=True, timeChange=True, selected=True)
		
		if inTangent:
			for key in keys:
				pm.selectKey(curve, add=True, inTangent=True, time=key)
				pm.selectKey(curve, remove=True, outTangent=True, time=key)
						
		if outTangent:
			for key in keys:
				pm.selectKey(curve, remove=True, inTangent=True, time=key)
				pm.selectKey(curve, add=True, outTangent=True, time=key)