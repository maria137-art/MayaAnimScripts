def mr_create_null_offset(mode):
    sel = cmds.ls(selection=True)
    start_time = cmds.playbackOptions(q=True, min=True)
    end_time = cmds.playbackOptions(q=True, max=True)
    
    valid_objects = []
    keyed_objects = []
    nulls_for_keyed_objects = []
    static_objects = []

    # Check if any of selected are already in offset groups.
    for item in sel:
        parent = cmds.listRelatives(item, parent=True)

        if parent and parent[0].endswith("_offset_grp"):
            print("NOTE: The selected item is already in an offset_grp.")
            continue
        elif item.endswith("_offset_grp"):
            print("NOTE: The selected item is an offset group.")
            continue

        else:
            valid_objects.append(item)   

            attrs = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]
            for attr in attrs:
                cmds.setAttr(item + attr, lock=False)

            has_keyframes = cmds.keyframe(item, query=True, keyframeCount=True)
            if has_keyframes:
                keyed_objects.append(item)
            else:
                static_objects.append(item)
    
    # If items are keyed, bake them to spare locators, to hold their worldspace position.
    if keyed_objects:
        cmds.select(keyed_objects)
        mr_bakeToWorldspace.main("both")
    
    # Create nulls, and match position and orientation          
    for item in valid_objects:
        parent = cmds.listRelatives(item, parent=True)
        null = cmds.group(empty=True, name=item + "_offset_grp")
        cmds.parentConstraint(item, null)

        if item in keyed_objects:
            nulls_for_keyed_objects.append(null) 

        elif item in static_objects:
            cmds.delete(null + "_parentConstraint1")
        
        # Parent the nulls.      
        if parent:
            cmds.parent(null, parent[0])
        cmds.parent(item, null)

    if mode == "static":
        # Lock attributes of offset group
        attrs += [".sx", ".sy", ".sz", ".v"]
        for attr in attrs:
            cmds.setAttr(null + attr, lock=True)
        
        if keyed_objects:
            cmds.refresh(suspend=True)
            cmds.bakeResults(
                keyed_objects,
                simulation=True,
                time=(start_time, end_time),
                sampleBy=1,
                attribute=['translateX', 'translateY', 'translateZ, rotateX, rotateY, rotateZ'],
                disableImplicitControl=True,
                preserveOutsideKeys=True,
                sparseAnimCurveBake=False,
                removeBakedAttributeFromLayer=False,
                removeBakedAnimFromLayer=False,
                bakeOnOverrideLayer=False,
                minimizeRotation=True,
                controlPoints=False
            )
            cmds.filterCurve()
            cmds.refresh(suspend=False)
            
    if mode == "keyed":
        if nulls_for_keyed_objects:
            cmds.refresh(suspend=True)
            cmds.bakeResults(
                nulls_for_keyed_objects,
                simulation=True,
                time=(start_time, end_time),
                sampleBy=1,
                disableImplicitControl=True,
                preserveOutsideKeys=True,
                sparseAnimCurveBake=False,
                removeBakedAttributeFromLayer=False,
                removeBakedAnimFromLayer=False,
                bakeOnOverrideLayer=False,
                minimizeRotation=True,
                controlPoints=False
            )
            cmds.filterCurve()
            cmds.delete(nulls_for_keyed_objects, constraints=True)
            cmds.refresh(suspend=False)

        # Key original selection, before deleting their drivers
        cmds.setKeyframe(sel, attribute='translateX')
        cmds.setKeyframe(sel, attribute='translateY')
        cmds.setKeyframe(sel, attribute='translateZ')
        cmds.setKeyframe(sel, attribute='rotateX')
        cmds.setKeyframe(sel, attribute='rotateY')
        cmds.setKeyframe(sel, attribute='rotateZ')

    # Delete drivers.
    cmds.select(sel)
    mr_find_constraint_targets_and_drivers.mr_find_drivers_of_selected()
    cmds.delete()

    if mode == "static":
        # Set keys on the original selection to default values (to not double the motion)
        cmds.select(sel)
        set_transform_values_to_default()

    # Finish script by selecting the last item
    last_item = sel[-1]
    cmds.select(last_item, replace=True)