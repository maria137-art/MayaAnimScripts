"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_constraint_utilities.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# Custom constraint functions, made so that only the driver object is selected afterwards.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_constraint_utilities
importlib.reload(mr_constraint_utilities)

# Use any of the following:
mr_constraint_utilities.parent_maintain_offset()
mr_constraint_utilities.point_maintain_offset()
mr_constraint_utilities.orient_maintain_offset()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-30 - 0002:
# - Adding check for if nothing is selected.
#
# 2023-12-19 - 0001:
# 	- First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def parent_maintain_offset():
	sel = cmds.ls(selection=True)
	if sel:
		cmds.parentConstraint(maintainOffset=True)
		cmds.select(sel[0])
	else:
		cmds.warning("No selected objects found.")

def point_maintain_offset():
	sel = cmds.ls(selection=True)
	if sel:
		cmds.orientConstraint(maintainOffset=True)
		cmds.select(sel[0])
	else:
		cmds.warning("No selected objects found.")

def orient_maintain_offset():
	sel = cmds.ls(selection=True)
	if sel:
		cmds.orientConstraint(maintainOffset=True)
		cmds.select(sel[0])
	else:
		cmds.warning("No selected objects found.")