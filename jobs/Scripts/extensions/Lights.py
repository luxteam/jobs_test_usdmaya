def reset_attributes(node_name):
    cmds.setAttr(node_name + ".horizontalFilmAperture", 1, 1, 1, type='double3')
    cmds.setAttr(node_name + ".intensity", 5000)

    if node_name == "spotLightShape1":
        cmds.setAttr(node_name + ".coneAngle", 5000)
        cmds.setAttr(node_name + ".penumbraAngle", 5000)
        cmds.setAttr(node_name + ".dropoff", 5000)
