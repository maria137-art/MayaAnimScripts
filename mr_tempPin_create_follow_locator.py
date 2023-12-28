"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_tempPin_create_follow_locator.py
# VERSION: 0003
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# For each selected object, create a locator inside an offset group that follows it.
# The locator can be freely placed while still following the original control.
#
# EXAMPLE USES:
# ---------------------------------------
# - Create follow locators, to be tagged as pivots with other scripts, such as mr_tempPin_pivotFromSelectionSet.py.
# - e.g. in order to easily set a particular point on a foot as a pivot.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_tempPin_create_follow_locator
importlib.reload(mr_tempPin_create_follow_locator)

mr_tempPin_create_follow_locator.main()

# ---------------------------------------
# WISH LIST:
# ---------------------------------------
# - Be able to create follow locators for vertices. Explore using rivets.
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-18 - 0003:
#   - Converting original MEL script to Python.
#
# 2023-04-10 - 0002:
#   - Minor edits.
#
# 2023-03-29 - 0001:
#   - First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def main():
    # ------------------------------------------------------------------- 
    # 01.INITIALISE VARIABLES.
    # ------------------------------------------------------------------- 
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning("Please select one or more objects to create a follow locator for.")
        return  

    attr_to_lock = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "v"]
    attr_to_lock_and_hide = ["scaleX", "scaleY", "scaleZ"]

    names_to_check = ["_offset", "_follow_loc"]

    # ------------------------------------------------------------------- 
    # 01. CHECK IF ANY SELECTED OBJECTS ARE EXISTING OFFSET GROUPS OR FOLLOW LOCATORS.
    # ------------------------------------------------------------------- 
    for obj in sel:
        if any(name in obj for name in names_to_check):   
            cmds.warning("Please select objects that are not an offset group or follow locator.")
            return

    # ------------------------------------------------------------------- 
    # 01. CREATE A FOLLOW LOCATOR.
    # -------------------------------------------------------------------   
    follow_locators = []

    for obj in sel:
        # Check if a follow locator already exists.
        loc = obj + "_follow_loc"
        if cmds.objExists(loc):
            cmds.warning(f"{loc} already exists.")
            return

        cmds.spaceLocator(name=loc)[0] 
        cmds.setAttr(loc + ".localScale", 18, 18, 18)
        
        follow_locators.append(loc)

        # Hide unrelated attributes.
        formatted_attrs = [f"{loc}.{attr}" for attr in attr_to_lock_and_hide]
        for attr in formatted_attrs:
            cmds.setAttr(attr, lock=True, keyable=False) 

        loc_vis = loc + ".visibility"
        cmds.setAttr(loc_vis, lock=True, keyable=False)

        # ------------------------------------------------------------------- 
        # 02. CREATE AN OFFSET GROUP.
        # ------------------------------------------------------------------- 
        offset = loc + "_offset"

        # If an offset group already exists, just add the locator to it.
        if cmds.objExists(offset):
            cmds.parent(loc, offset)
        else:
            cmds.group(loc, name=offset)
            cmds.parentConstraint(obj, offset)
        
        # Hide unrelated attributes.
        formatted_attrs = [f"{offset}.{attr}" for attr in attr_to_lock_and_hide]
        for attr in formatted_attrs:
           cmds.setAttr(attr, lock=True, keyable=False) 

        # Lock main attributes.
        formatted_attrs = [f"{offset}.{attr}" for attr in attr_to_lock]
        for attr in formatted_attrs:
            cmds.setAttr(attr, lock=True) 

    # End with follow locators selected.
    cmds.select(follow_locators)