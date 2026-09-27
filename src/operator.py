import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from typing import TYPE_CHECKING

from .generator import create_voxel_mesh

# This is soo stupid. stub_internal does not exist in blender and only in the stubs
# so I need to throw it out during runtime
if TYPE_CHECKING:
    from bpy.stub_internal.rna_enums import OperatorReturnItems, OperatorTypeFlagItems

# Registers as a blender operator, which from what I understand is just an action,
# that can be invoked by a button press. And ImportHelper is for File loading.
# Also this naming convention is complete ass.
class IMPORT_IMAGE_OT_voxel_mesh(  # pyright: ignore[reportIncompatibleMethodOverride]
    bpy.types.Operator, ImportHelper
):
    bl_idname: str = "import_image.voxel_mesh"
    bl_label: str = "Image as Voxelmesh"
    bl_description: str = "Create a voxel mesh from an image"
    if TYPE_CHECKING:
        bl_options: set[OperatorTypeFlagItems]
    bl_options = {"REGISTER", "UNDO"}

    # Such a joke lol; TypeChecking is false at runtime, but for Pyright
    # apparently this is the way to tell it that filepath will exist on
    # runtime, as it gets added by ImportHelper (???)
    if TYPE_CHECKING:
        filepath: str

    # Should maybe exclude file types without transparency at some point.
    filter_glob: StringProperty(
        default="*.bmp;*.exr;*.hdr;*.jpeg;*.jpg;*.png;*.tga;*.tif;*.tiff;*.webp",
        options={"HIDDEN"},
    )  # pyright: ignore[reportInvalidTypeForm] I give up

    # Called when a file is chosen
    def execute(self, context: bpy.types.Context) -> "set[OperatorReturnItems]":
        # I guess I should keep the try-catch for corrupted files.
        try:
            image: bpy.types.Image = bpy.data.images.load(
                self.filepath, check_existing=True
            )
        except RuntimeError as error:
            self.report({"ERROR"}, f"Could not load image: {error}")
            return {"CANCELLED"}

        mesh: bpy.types.Object = create_voxel_mesh(
            image=image,
            name=image.name,
            center=True,
            do_create_material=True,
            uv_offset=0.01,
        )
        for selected_object in context.selected_objects or list():
            selected_object.select_set(False)
        mesh.select_set(True)
        context.view_layer.objects.active = mesh

        return {"FINISHED"}


# Draw Menu Item
def draw_image_voxel_mesh(self: bpy.types.Menu, context: bpy.types.Context) -> None:
    layout = self.layout
    if layout is None:
        return

    layout.operator(IMPORT_IMAGE_OT_voxel_mesh.bl_idname)


def register() -> None:
    bpy.utils.register_class(IMPORT_IMAGE_OT_voxel_mesh)
    bpy.types.VIEW3D_MT_image_add.append(draw_image_voxel_mesh)


def unregister() -> None:
    bpy.types.VIEW3D_MT_image_add.remove(draw_image_voxel_mesh)
    bpy.utils.unregister_class(IMPORT_IMAGE_OT_voxel_mesh)
