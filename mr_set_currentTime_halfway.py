"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_set_currentTime_halfway.py
# VERSION: 0004
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# DESCRIPTION: 
# Set the currentTime on the Time Slider to the nearest number frame inbetween the next and previous keyframes, either as an integer or float.
# 
# ---------------------------------------
# RUN COMMANDS:
# ---------------------------------------

mr_set_currentTime_halfway(float=False)

mr_set_currentTime_halfway(float=True)

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------

# 2023-06-25 - 0004
    - Renamed script
    - Adding option to set currentTime as float or integer

# 2023-06-24 - 0003
    - Converted script from MEL to Python. 
    - Added ability to jump to midpoint of selected keys in Graph Editor.
    - Added option to use startTime or endTime as the prev/nextKeyframe, if one doesn't exist.

# 2023-01-30 - 0002: 
    - If no objects are selected, script will jump to midpoint of playback range.

# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def mr_set_currentTime_halfway(float=False):

    sel = cmds.ls(selection=True)

    startTime = cmds.playbackOptions(query=True, min=True)
    endTime = cmds.playbackOptions(query=True, max=True)    

    # If selection is empty, go to midpoint of playback range.
    if not sel:
        if float:
            midTime = (startTime + endTime) / 2.0
        else:
            midTime = (startTime + endTime) // 2

        cmds.currentTime(midTime)
        
    # If the cursor is above the Graph Editor, and keys are selected,
    # go to their range midpoint.
    else:
        current_panel = cmds.getPanel(underPointer=True)

        if current_panel == "graphEditor1":
            selected_keys = cmds.keyframe(query=True, selected=True)

            if selected_keys:
                if float:
                    midTime = sum(selected_keys) / len(selected_keys)
                else:
                    midTime = sum(selected_keys) // len(selected_keys)

                cmds.currentTime(midTime)
        
        # Otherwise, go to midpoint of prev and next keyframe of selected.
        else:
            current_time = cmds.currentTime(query=True)
            
            prevKeyframe = cmds.findKeyframe(timeSlider=True, which="previous")
            nextKeyframe = cmds.findKeyframe(timeSlider=True, which="next")
            
            if prevKeyframe is None or prevKeyframe >= current_time:
                prevKeyframe = startTime

            if nextKeyframe is None or nextKeyframe <= current_time:
                nextKeyframe = endTime
            
            if float:
                midPoint = (nextKeyframe + prevKeyframe) / 2.0
            else:
                midPoint = (nextKeyframe + prevKeyframe) // 2

            cmds.currentTime(midPoint)