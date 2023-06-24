"""
# ------------------------------------------------------------------------------ #
# SCRIPT: moveHalfway_int.py
# VERSION: 0003
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# DESCRIPTION: 
# Move Time Slider to the nearest integering number frame inbetween the next and previous keyframes.
# 
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

mr_move_halfway_int()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-06-24 - 0003
    - Converted script from MEL to Python. 
    - Added ability to jump to midpoint of selected keys in Graph Editor.
    - Added option to use startTime or endTime as the prev/nextKeyframe, if one doesn't exist.

# 0002: 
    - If no objects are selected, script will jump to midpoint of playback range.
# 
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def mr_move_halfway_int():

    sel = cmds.ls(selection=True)
    
    # If selection is empty, go to midpoint of playback range.
    if not sel:
        startTime = cmds.playbackOptions(query=True, min=True)
        endTime = cmds.playbackOptions(query=True, max=True)
        
        midTime = (startTime + endTime) // 2
        cmds.currentTime(midTime)
        
    # If the cursor is above the Graph Editor, and keys are selected,
    # go to their range midpoint.
    else:
        current_panel = cmds.getPanel(underPointer=True)

        if current_panel == "graphEditor1":
            selected_keys = cmds.keyframe(query=True, selected=True)

            if selected_keys:
                midTime = sum(selected_keys) // len(selected_keys)
                cmds.currentTime(midTime)
        
        # Otherwise, go to midpoint of prev and next keyframe of selected.
        else:
            current_time = cmds.currentTime(query=True)
            
            prevKeyframe = cmds.findKeyframe(timeSlider=True, which="previous")
            nextKeyframe = cmds.findKeyframe(timeSlider=True, which="next")
            
            # If there is no previous keyframe, use the playback range's start time.
            if prevKeyframe is None or prevKeyframe >= current_time:
                prevKeyframe = cmds.playbackOptions(query=True, min=True)

            # If there is no next keyframe, use the playback range's end time.
            if nextKeyframe is None or nextKeyframe <= current_time:
                nextKeyframe = cmds.playbackOptions(query=True, max=True)
            
            midPoint = (nextKeyframe + prevKeyframe) // 2
            cmds.currentTime(midPoint)
