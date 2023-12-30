"""
# ------------------------------------------------------------------------------ #
# SCRIPT: ml_setKey_mr_checkIfAnimCurvesSelected.py
# VERSION: 0001
#
# CREATORS: Maria Robertson (just added check for selected animation curves)
# CREDIT: Morgan Loomis (for ml_setKey.py and ml_utilities.py)
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A script importing from Morgan Loomis' robust ml_setKey script (Revision 11):
# http://morganloomis.com/tool/ml_setKey/
# 
# This script just adds the following check:
#   - If mouse pointer is NOT above Graph Editor:
#       - Set key as normal.
#
#   - If mouse pointer IS above Graph Editor:
#       - If any animation curve keys are selected, key on only them (ignoring any highlighted attributes in the channel box).
#
# My hotkey preference:
#   - S         : ml_setKey.setKey(selectedChannels=False, visibleInGraphEditor=False, keyKeyed=False, deleteSubFrames=False, insert=True, keyShapes=False)
#
#   - ALT + S   : ml_setKey_mr_checkIfAnimCurvesSelected.main()
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import ml_setKey_mr_checkIfAnimCurvesSelected
importlib.reload(ml_setKey_mr_checkIfAnimCurvesSelected)

ml_setKey_mr_checkIfAnimCurvesSelected.main()

# ---------------------------------------
# REQUIREMENTS: 
# ---------------------------------------
# This script uses ml_setKey.py from the ml_tools library.
# Follow instructions here for installation: http://morganloomis.com/tool/ml_setKey/
# 
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-29 - 0001:
#   - First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel
import ml_setKey

def main():
    connection = cmds.editor('graphEditor1GraphEd', query=True, mainListConnection=True)
    visible_curves = mel.eval('expandSelectionConnectionAsArray "{}"'.format(connection))
    selected_curves = []
    
    current_panel = cmds.getPanel(underPointer=True)
    
    # -------------------------------------------------------------------
    # 01. IF MOUSE CURSOR IS NOT OVER GRAPH EDITOR.
    # -------------------------------------------------------------------  
    if current_panel != 'graphEditor1':
        personal_ml_setkey_settings()

    # -------------------------------------------------------------------
    # 01. IF MOUSE CURSOR IS GRAPH EDITOR.
    # -------------------------------------------------------------------       
    else:
        # If any of the visible curves in the Graph Editor have selected keys, key only them.
        # Otherwise, key as normal.
        if visible_curves:
            for curve in visible_curves:
                has_keys_selected = are_keys_selected_on_animation_curve(curve) 
                if has_keys_selected:
                    selected_curves.append(curve)          
            if selected_curves:
                cmds.setKeyframe(selected_curves, insert=True)
            else:
                personal_ml_setkey_settings()
        else:
            personal_ml_setkey_settings()
            

def are_keys_selected_on_animation_curve(curve):
    selected_keys = cmds.keyframe(curve, query=True, selected=True)
    return bool(selected_keys)
      
def personal_ml_setkey_settings():
    ml_setKey.setKey(selectedChannels=True, visibleInGraphEditor=False, keyKeyed=True, deleteSubFrames=False, insert=True, keyShapes=False)
