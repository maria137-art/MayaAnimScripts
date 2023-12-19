"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_constraint_snippets.py
# VERSION: 0001
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
import mr_constraint_snippets
importlib.reload(mr_constraint_snippets)

# Use any of the following:
mr_constraint_snippets.parent_maintain_offset()
mr_constraint_snippets.point_maintain_offset()
mr_constraint_snippets.orient_maintain_offset()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2023-12-19 - 0001:
# 	- First pass.
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds

def parent_maintain_offset():
	sel = cmds.ls(selection=True)
	cmds.parentConstraint(maintainOffset=True)
	cmds.select(sel[0])

def point_maintain_offset():
	sel = cmds.ls(selection=True)
	cmds.orientConstraint(maintainOffset=True)
	cmds.select(sel[0])

def orient_maintain_offset():
	sel = cmds.ls(selection=True)
	cmds.orientConstraint(maintainOffset=True)
	cmds.select(sel[0])