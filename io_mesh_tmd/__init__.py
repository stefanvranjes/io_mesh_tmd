bl_info = {
    "name": "TMD format",
    "author": "Stefan Vranjes",
    "version": (1, 0, 0),
    "blender": (2, 81, 6),
    "location": "File > Import-Export",
    "description": "Import-Export TMD files",
    "category": "Import-Export",
}

import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    axis_conversion,
)
from bpy.types import (
    Operator,
    OperatorFileListElement,
)

@orientation_helper(axis_forward='Y', axis_up='Z')
class ImportTMD(Operator, ImportHelper):
    bl_idname = "import_mesh.tmd"
    bl_label = "Import TMD"
    bl_description = "Load TMD mesh data"
    bl_options = {'UNDO'}

    filename_ext = ".tmd"

    filter_glob: StringProperty(
        default="*.tmd",
        options={'HIDDEN'},
    )
    files: CollectionProperty(
        name="File Path",
        type=OperatorFileListElement,
    )
    directory: StringProperty(
        subtype='DIR_PATH',
    )
    global_scale: FloatProperty(
        name="Scale",
        soft_min=0.001, soft_max=1000.0,
        min=1e-6, max=1e6,
        default=1.0,
    )
    use_scene_unit: BoolProperty(
        name="Scene Unit",
        description="Apply current scene's unit (as defined by unit scale) to imported data",
        default=False,
    )
    use_facet_normal: BoolProperty(
        name="Facet Normals",
        description="Use (import) facet normals (note that this will still give flat shading)",
        default=False,
    )

    def execute(self, context):
        import os
        from mathutils import Matrix
        from . import tmd_utils
        from . import blender_utils

        paths = [os.path.join(self.directory, name.name) for name in self.files]

        scene = context.scene

        global_scale = self.global_scale
        if scene.unit_settings.system != 'NONE' and self.use_scene_unit:
            global_scale /= scene.unit_settings.scale_length

        global_matrix = axis_conversion(
            from_forward=self.axis_forward,
            from_up=self.axis_up,
        ).to_4x4() @ Matrix.Scale(global_scale, 4)

        if not paths:
            paths.append(self.filepath)

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        if bpy.ops.object.select_all.poll():
            bpy.ops.object.select_all(action='DESELECT')

        for path in paths:
            objName = bpy.path.display_name_from_filepath(path)
            indices, pts = tmd_utils.read_tmd(path)
            blender_utils.create_and_link_mesh(objName, indices, pts, global_matrix)

        return {'FINISHED'}
    
    def draw(self, context):
        pass

class TMD_PT_import_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_MESH_OT_tmd"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "global_scale")
        layout.prop(operator, "use_scene_unit")

        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")

class TMD_PT_import_geometry(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Geometry"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_MESH_OT_tmd"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "use_facet_normal")

@orientation_helper(axis_forward='Y', axis_up='Z')
class ImportTMD2(Operator, ImportHelper):
    bl_idname = "import_mesh.tmd2"
    bl_label = "Import TMD2"
    bl_description = "Load TMD2 mesh data"
    bl_options = {'UNDO'}

    filename_ext = ".tmd2"

    filter_glob: StringProperty(
        default="*.tmd2",
        options={'HIDDEN'},
    )
    files: CollectionProperty(
        name="File Path",
        type=OperatorFileListElement,
    )
    directory: StringProperty(
        subtype='DIR_PATH',
    )
    global_scale: FloatProperty(
        name="Scale",
        soft_min=0.001, soft_max=1000.0,
        min=1e-6, max=1e6,
        default=1.0,
    )
    use_scene_unit: BoolProperty(
        name="Scene Unit",
        description="Apply current scene's unit (as defined by unit scale) to imported data",
        default=False,
    )
    use_facet_normal: BoolProperty(
        name="Facet Normals",
        description="Use (import) facet normals (note that this will still give flat shading)",
        default=False,
    )

    def execute(self, context):
        import os
        from mathutils import Matrix
        from . import tmd_utils
        from . import blender_utils

        paths = [os.path.join(self.directory, name.name) for name in self.files]

        scene = context.scene

        global_scale = self.global_scale
        if scene.unit_settings.system != 'NONE' and self.use_scene_unit:
            global_scale /= scene.unit_settings.scale_length

        global_matrix = axis_conversion(
            from_forward=self.axis_forward,
            from_up=self.axis_up,
        ).to_4x4() @ Matrix.Scale(global_scale, 4)

        if not paths:
            paths.append(self.filepath)

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')

        if bpy.ops.object.select_all.poll():
            bpy.ops.object.select_all(action='DESELECT')

        for path in paths:
            objName = bpy.path.display_name_from_filepath(path)
            indices, nors, pts = tmd_utils.read_tmd2(path)
            nors = nors if self.use_facet_normal else None
            blender_utils.create_and_link_mesh2(objName, indices, nors, pts, global_matrix)

        return {'FINISHED'}
    
    def draw(self, context):
        pass

class TMD2_PT_import_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_MESH_OT_tmd2"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "global_scale")
        layout.prop(operator, "use_scene_unit")

        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")

class TMD2_PT_import_geometry(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Geometry"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_MESH_OT_tmd2"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "use_facet_normal")

def menu_import(self, context):
    self.layout.operator(ImportTMD.bl_idname, text="Tmd (.tmd)")

def menu_import2(self, context):
    self.layout.operator(ImportTMD2.bl_idname, text="Tmd2 (.tmd2)")

classes = (
    ImportTMD, 
    TMD_PT_import_transform, 
    TMD_PT_import_geometry,
    ImportTMD2, 
    TMD2_PT_import_transform, 
    TMD2_PT_import_geometry
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_import)
    bpy.types.TOPBAR_MT_file_import.append(menu_import2)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    bpy.types.TOPBAR_MT_file_import.remove(menu_import2)


if __name__ == "__main__":
    register()
