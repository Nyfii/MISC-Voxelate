bl_info = {
    "name": "Voxelate",
    "author": "Nyfii",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Add > Image",
    "description": "Create voxel meshes from images",
    "category": "Import-Export",
}

from .operator import register, unregister
