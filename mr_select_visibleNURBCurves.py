import maya.cmds as cmds

def mr_select_visibleNURBCurves():
    # get all NURBS curves in the scene
    nurbs_curves = cmds.ls(type='nurbsCurve')
    
    # select only visible NURBS curve transforms
    visible_nurbs_transforms = []
    for curve in nurbs_curves:
        if cmds.getAttr(curve + '.visibility'):
            nurbs_transform = cmds.listRelatives(curve, parent=True, fullPath=True)[0]
            visible_nurbs_transforms.append(nurbs_transform)
    
    # select visible NURBS curve transforms
    cmds.select(visible_nurbs_transforms, replace=True)
