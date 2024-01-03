"""
# ------------------------------------------------------------------------------ #
# SCRIPT: mr_toggleWindows.py
# VERSION: 0002
#
# CREATORS: Maria Robertson
# CREDIT: Malcolm Andrieshyn (malcolm_341) / siproductions (CGSociety)
# ---------------------------------------
#
# ---------------------------------------
# DESCRIPTION: 
# ---------------------------------------
# A collection of functions to toggle window visibility. 
# Makes working with windows faster, without needing to load them each time.
#
# ---------------------------------------
# RUN COMMAND:
# ---------------------------------------
import importlib
import mr_toggleWindows
importlib.reload(mr_toggleWindows)

# USE ANY OF THE FOLLOWING:
mr_toggleWindows.toggle_hotkeyEditor()
mr_toggleWindows.toggle_scriptEditor()
mr_toggleWindows.toggle_undocked_window_visibility()
mr_toggleWindows.reset_undocked_windows_topLeft()

# ---------------------------------------
# CHANGELOG:
# ---------------------------------------
# 2024-01-03 - 0002:
#   - Bug fix for toggle_scriptEditor().
#
# 2023-12-30 - 0001:
#   - Adding following scripts:
#       - mr_toggle_undockedWindows.mel.
#       - mr_toggle_hotkeyEditor.mel
#       - mr_toggle_undockedWindows.mel
#       - mr_resetWindows.py
# ------------------------------------------------------------------------------ #
"""

import maya.cmds as cmds
import maya.mel as mel

def toggle_scriptEditor():
    '''
    # ------------------------------------------------------------------------------ #
    # CREDIT: Malcolm Andrieshyn (malcolm_341)
    # Thanks to malcolm_341 for the idea, initially for working around Maya 2022 memory freeze:
    # https://forums.autodesk.com/t5/maya-forum/maya-2022-freezing-when-opening-script-editor/td-p/10292666 
    # ------------------------------------------------------------------------------ #
    '''
    mel.eval("scriptEditorInfo -ch;")

    script_editor = "scriptEditorPanel1Window"
    if cmds.window(script_editor, query=True, exists=True):
        mel.eval(f"toggleWindowVisibility {script_editor};")
    else:
        mel.eval("tearOffPanel \"Script Editor\" \"scriptEditor\" true ;")

# ------------------------------------------------------------------------------ #
def toggle_hotkeyEditor():
    hotkey_editor = cmds.window("HotkeyEditor", query=True, exists=True)
    if hotkey_editor:
        mel.eval("toggleWindowVisibility HotkeyEditor;")
    else:
        mel.eval("hotkeyEditorWindow")

# ------------------------------------------------------------------------------ #
def toggle_undocked_window_visibility():
    '''
    # ------------------------------------------------------------------------------ #
    # CREDIT: siproductions (CGSociety): https://forums.cgsociety.org/t/close-all-maya-windows/1357835/4
    # Thanks to siproductions for MEL example.
    # ------------------------------------------------------------------------------ #
    '''
    # ------------------------------------------------------------------- 
    # 01. INITIALIZE VARIABLES.
    # ------------------------------------------------------------------- 
    undocked_windows = cmds.lsUI(windows=True)
    windows_to_ignore = ["CommandWindow", "ConsoleWindow", "MayaWindow", "ColorEditor"]

    # Remove windows_to_ignore from undocked_windows.
    windows_to_toggle = [win for win in undocked_windows if win not in windows_to_ignore]

    # Set integer to use as conditioning
    toggle_visible_windows_condition = 0

    # ------------------------------------------------------------------- 
    # 01. DETERMINE HOW WINDOWS SHOULD BE TOGGLED.
    # ------------------------------------------------------------------- 
    for win in windows_to_toggle:
        if cmds.window(win, query=True, visible=True):
            # If any window is visisble, set the integer to 1 to trigger rest of script.
            toggle_visible_windows_condition = 1
            break

    # ------------------------------------------------------------------- 
    # 01. TOGGLE WINDOWS.
    # ------------------------------------------------------------------- 
    if toggle_visible_windows_condition == 0:
        # print("Toggling on undocked window visiblility.")
        for win in windows_to_toggle:
            cmds.window(win, edit=True, visible=True)

    if toggle_visible_windows_condition == 1:
        # print("Toggling off undocked window visiblility.")
        for win in windows_to_toggle:
            cmds.window(win, edit=True, visible=False)

# ------------------------------------------------------------------------------ #
def reset_undocked_windows_topLeft():
    '''
    # ------------------------------------------------------------------------------ #
    # DESCRIPTION: 
    # Reposition undocked windows to the top left corner of the screen.
    # Helpful when windows move too far off-screen.
    # ------------------------------------------------------------------------------ #
    '''
    undocked_windows = cmds.lsUI(windows=True)  
    windows_to_ignore = ["CommandWindow", "ConsoleWindow", "MayaWindow", "ColorEditor"]  
    windows_to_reset = [win for win in undocked_windows if win not in windows_to_ignore]

    for win in windows_to_reset:
        cmds.window(win, edit=True, topLeftCorner=[0, 0])