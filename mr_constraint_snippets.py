"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_constraint_utilities.py
# VERSION: 0003
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

# USE ANY OF THE FOLLOWING:
mr_constraint_utilities.parent_constraint()
mr_constraint_utilities.point_constraint()
mr_constraint_utilities.orient_constraint()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-30 - 0003:
#	- Adding options for maintainOffset.
#
# 2023-12-30 - 0002:
# 	- Adding check for if nothing is selected.
#
# 2023-12-19 - 0001:
# 	- First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

# ------------------------------------------------------------------------------ #
def parent_constraint(maintain_offset=True):
	sel = cmds.ls(selection=True)
	if sel:
		if maintain_offset:
			cmds.parentConstraint(maintainOffset=True)
		else:
			cmds.parentConstraint()
		cmds.select(sel[0])

# ------------------------------------------------------------------------------ #
def point_constraint(maintain_offset=True):
	sel = cmds.ls(selection=True)
	if sel:
		if maintain_offset:
			cmds.pointConstraint(maintainOffset=True)
		else:
			cmds.pointConstraint()
		cmds.select(sel[0])

# ------------------------------------------------------------------------------ #
def orient_constraint(maintain_offset=True):
	sel = cmds.ls(selection=True)
	if sel:
		if maintain_offset:
			cmds.orientConstraint(maintainOffset=True)
		else:
			cmds.orientConstraint()
		cmds.select(sel[0])