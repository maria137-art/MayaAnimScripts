"""
# ------------------------------------------------------------------------------ #
# SCRIPT: find_constraint_targets_and_drivers.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# CREDIT: Tim van Huseen (for MEL version of Select the Constrainer)
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Use find_constraint_targets_of_selected() to select any constraint targets of the selected objects.
# 
# Use find_constraint_drivers() to select any drivers of selected objects that are constrained by them.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------

mr_find_targets_of_selected()

mr_find_drivers_of_selected()

# ---------------------------------------
# RESEARCH THAT HELPED:
# ---------------------------------------
# How to find driver of selected object - https://forums.cgsociety.org/t/how-to-query-a-connectionsOfSelected-target-list-without-knowing-the-constraint-type/1309588/2
#
# Tim van Huseen's Select The Constrainer's script':
# https://forums.autodesk.com/t5/maya-ideas/constraint-objects-view-or-select-the-object-it-s-constraint-to/idi-p/7960702
#
# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-06-25 - 0002
# Converted and combined MEL scripts into Python here.
# Added print commands for clarity.
#
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds


def mr_find_targets_of_selected():
    selected = cmds.ls(selection=True)

    if not selected:
        print("No objects selected.")
        return
    
    unique_targets = set()  # Set to store the unique targets
    
    for obj in selected:
        conns = cmds.listConnections(obj, type="constraint") or []        
        targets = cmds.listRelatives(conns, parent=True) or [] # Find parents of any constraint connections
        unique_targets.update(targets)
    
    if unique_targets:
        unique_targets.difference_update(selected)  # Remove original selection from unique_targets
    
        for target in unique_targets:
            print("Target found: {}".format(target))       
        cmds.select(list(unique_targets))  # Convert the set back to a list and select the targets
    else:
        print("No targets found.")



def mr_find_drivers_of_selected():

    selected = cmds.ls(selection=True)
    if not selected:
        print("No objects selected.")

    else: 
        for target_obj in selected:
            constraints_of_selected = cmds.listRelatives(target_obj, typ="constraint")
            
            if constraints_of_selected:
                print("Target: {}.".format(target_obj))       
                cmds.select(cl=True)
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