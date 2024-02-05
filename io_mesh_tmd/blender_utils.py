def create_and_link_mesh(name, faces, points, global_matrix):
    """
    Create a blender mesh and object called name from a list of
    *points* and *faces* and link it in the current scene.
    """

    import array
    from itertools import chain
    import bpy

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points, [], faces)

    mesh.transform(global_matrix)

    # update mesh to allow proper display
    mesh.validate(clean_customdata=False)  # *Very* important to not remove lnors here!

    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)