# Random helpful Python snippets for Autodesk Maya.

# ------------------------------------------------------------------------------ #

import sys

def print_list_of_all_Maya_script_directories():
    script_dirs = []
    for path in sys.path:
        if 'maya' in path.lower() and 'scripts' in path.lower():
            script_dirs.append(path)
    print(script_dirs)

# ------------------------------------------------------------------------------ #

def execute_script():
    exec( open('C:/Users/User/Documents/maya/modules/mr_tools/scripts/mcScripts/aimSpace.py').read() )

# ------------------------------------------------------------------------------ #
