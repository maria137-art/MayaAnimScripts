"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_find_constraint_targets_and_drivers.py
# VERSION: 0004
#
# CREATORS: Maria Robertson
# CREDIT: Tim van Huseen (for MEL version of Select the Constrainer)
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Use mr_find_targets_of_selected() to select any constraint targets of the selected objects.
# 
# Use mr_find_drivers_of_selected() to select any drivers of selected objects that are constrained by them.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

import importlib

import mr_find_constraint_targets_and_drivers
importlib.reload(mr_find_constraint_targets_and_drivers)

# ANY OF THE FOLLOWING

mr_find_constraint_targets_and_drivers.mr_find_targets_of_selected()

mr_find_constraint_targets_and_drivers.mr_find_drivers_of_selected()

mr_find_constraint_targets_and_drivers.mr_deselect_selected_if_constrained()

# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# How to find driver of selected object: https://forums.cgsociety.org/t/how-to-query-a-connectionsOfSelected-target-list-without-knowing-the-constraint-type/1309588/2
#
# Tim van Huseen's Select The Constrainer(s) script':
# https://forums.autodesk.com/t5/maya-ideas/constraint-objects-view-or-select-the-object-it-s-constraint-to/idi-p/7960702
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-28 - 0005:
# - Updating mr_find_targets_of_selected, so it prints in the original order.
# - Did this, as the reversed order inteferred with mr_tempPin_pivotFromSelectionSet 0008.
#
#
# 2023-07-03 - 0004:
#   - Fixed selection for multiple drivers, with mr_find_drivers_of_selected.
#
# 2023-06-26 - 0003:
#   - Added mr_deselect_selected_if_constrained().
#
# 2023-06-25 - 0002:
#   - Converted and combined MEL scripts into Python here.
#   - Added print commands for clarity.
#
# ------------------------------------------------------------------------------ #
"""

from collections import OrderedDict
import maya.cmds as cmds


def mr_find_targets_of_selected():
    selected = cmds.ls(selection=True)

    if not selected:
        print("No objects selected.")
        return

    unique_targets = OrderedDict()
    
    for obj in selected:
        conns = cmds.listConnections(obj, type="constraint") or []
         # Find parents of any of the constraint connections.
        targets = cmds.listRelatives(conns, parent=True) or []
        
        # If a target is not yet in unique_targets, add it there.
        for target in targets:
            if target not in unique_targets:
                unique_targets[target] = None

    # Maintain the oroginal order list.
    targets_in_order = list(unique_targets.keys())

    if targets_in_order:
        print("Targets found:")
        for target in targets_in_order:
            print(target)
        cmds.select(targets_in_order)
    else:
        print("No targets found.")


def mr_find_drivers_of_selected():
    selected = cmds.ls(selection=True)
    cmds.select(cl=True)
    
    if not selected:
        print("No objects selected.")

    else: 
        for target_obj in selected:
            constraints_of_selected = cmds.listRelatives(target_obj, typ="constraint")
            
            if constraints_of_selected:
                print("Target: {}.".format(target_obj))       
                
                drivers = []
                
                for n in range(len(constraints_of_selected)):
                    conns = cmds.listConnections(constraints_of_selected[n], connections=1)
                    
                    for mtrx in range(20):
                        destination_connection = constraints_of_selected[n] + ".target[{}].targetParentMatrix".format(mtrx)
                        
                        try:
                            index = conns.index(destination_connection)
                            driver_obj = conns[index+1]
                            if driver_obj not in drivers:
                                cmds.select(driver_obj, add=True)
                                drivers.append(driver_obj)
                                print("Driver: {}.\n".format(driver_obj))       
                        except ValueError:
                            break
            else:
                print("No constraints found.")


def mr_deselect_selected_if_constrained():
    selected = cmds.ls(selection=True)
    if not selected:
        print("No objects selected.")
    else: 
        for target_obj in selected:
            constraints_of_selected = cmds.listRelatives(target_obj, typ="constraint")
            
            if constraints_of_selected:
                cmds.select(target_obj, deselect=True)
