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

class ImportTMD():
    bl_idname = "import_mesh.tmd"
    bl_label = "Import TMD"
    bl_description = "Load TMD triangle mesh data"
    bl_options = {'UNDO'}

    filename_ext = ".tmd"

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

def menu_import(self, context):
    self.layout.operator(ImportTMD.bl_idname, text="Tmd (.tmd)")

classes = (
    ImportTMD
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
