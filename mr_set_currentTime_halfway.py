"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_set_currentTime_halfway.py
# VERSION: 0005
#
# CREATORS: Maria Robertson
# ---------------------------------------
# Last tested for Autodesk Maya 2023.3
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Set the current time to the midpoint of queried parameters, depending where the mouse cursor is.
# 
#   - If the mouse pointer is NOT above Graph Editor:
#       - Set the current time to the midpoint of the playback range.
#
#   - If the mouse pointer IS above Graph Editor:
#       - If keys on animation curves are selected:
#           - Set the current time to the midpoint of the selected keys' range.
#       - If NO keys on animation curves are selected:
#           - Set the current time to the midpoint of the next and previous key of the current frame.
#               - If there are keys at the current frame, do nothing.
#
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------
import importlib
import mr_set_currentTime_halfway
importlib.reload(mr_set_currentTime_halfway)

# USE ONE OF THE FOLLOWING:
mr_set_currentTime_halfway.main(float=False)
mr_set_currentTime_halfway.main(float=True)

# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

# ------------------------------------------------------------------------------ #
def main(float=False):
    """
    :param float: If False, always set the current time as a whole number, with no sub-frames.
    :type float: float
    """
    selection = cmds.ls(selection=True)

    # ---------------------------------------
    # 01. IF NOTHING IS SELECTED.
    # ---------------------------------------
    if not selection:
        startTime = cmds.playbackOptions(query=True, min=True)
        endTime = cmds.playbackOptions(query=True, max=True)   

        # Go to midpoint of the playback range.
        if float:
            midTime = (startTime + endTime) / 2.0
        else:
            midTime = (startTime + endTime) // 2
        cmds.currentTime(midTime)
        return
    

    current_panel = cmds.getPanel(underPointer=True)
    current_time = cmds.currentTime(query=True)

    # ---------------------------------------
    # 01. IF MOUSE CURSOR IS OVER GRAPH EDITOR.
    # ---------------------------------------  
    if current_panel == "graphEditor1":

        # ---------------------------------------
        # 02. IF KEYS ARE SELECTED.
        # ---------------------------------------  
        selected_keys = cmds.keyframe(query=True, selected=True)
        if selected_keys:
            keyframe_range = (min(selected_keys), max(selected_keys))

            # Go to midpoint of selected keys.
            if float:
                midTime = (keyframe_range[0] + keyframe_range[1]) / 2.0
            else:
                midTime = (keyframe_range[0] + keyframe_range[1]) // 2
            cmds.currentTime(midTime)

            return

    # ---------------------------------------
    # 01. OTHERWISE.
    # ---------------------------------------               
    # Check if any visible animation curves in the Graph Editor have keys at current time.
    visible_animation_curves = cmds.animCurveEditor('graphEditor1GraphEd', query=True, curvesShown=True)

    if visible_animation_curves:
        are_keys_at_currentTime = cmds.keyframe(query=True, time=(current_time, current_time), keyframeCount=True)

        # If there are no keys,
        if are_keys_at_currentTime == 0:
            # go to midpoint of next and previous keys.
            midPoint = get_midpoint_of_next_and_previous_key_at_currentTime(float=float)
            cmds.currentTime(midPoint)
        # Otherwise, do nothing.
        else:
            return

##################################################################################################################################################

########################################################################
#                                                                      #
#                          SUPPORT FUNCTIONS                           #
#                                                                      #
########################################################################

# ------------------------------------------------------------------------------ #
def get_midpoint_of_next_and_previous_key_at_currentTime(float=False):
    """
    Get the midpoint between the previous and next keyframes at the current time.

    :param float: If False, always set the current time as a whole number, with no sub-frames.
    :type float: float

    """
    current_time = cmds.currentTime(query=True)
    startTime = cmds.playbackOptions(query=True, min=True)
    endTime = cmds.playbackOptions(query=True, max=True)  

    prevKeyframe = cmds.findKeyframe(timeSlider=True, which="previous")
    nextKeyframe = cmds.findKeyframe(timeSlider=True, which="next")
    
    if prevKeyframe is None or prevKeyframe >= current_time:
        prevKeyframe = startTime
    if nextKeyframe is None or nextKeyframe <= current_time:
        nextKeyframe = endTime

    # Go to the midpoint of the previous and next keyframe of selected objects. 
    if float:
        midPoint = (nextKeyframe + prevKeyframe) / 2.0
    else:
        midPoint = (nextKeyframe + prevKeyframe) // 2

    return midPoint

"""
##################################################################################################################################################
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-28 - 0005:
#   - Renamed and divided original function.
#   - Fixed logic for when mouse cursor is over graph editor, and no keys are selected.
#   - Rearranged logic.
#   - Added to description.
#   - Moved changelog to the bottom.
#
# 2023-06-25 - 0004:
#   - Renamed script.
#   - Adding option to set currentTime as float or integer.
#
# 2023-06-24 - 0003:
#   - Converted script from MEL to Python. 
#   - Added ability to jump to midpoint of selected keys in Graph Editor.
#   - Added option to use startTime or endTime as the prev/nextKeyframe, if one doesn't exist.
#
# 2023-01-30 - 0002: 
#   - If no objects are selected, script will jump to midpoint of playback range.
#
# ---------------------------------------
##################################################################################################################################################
"""