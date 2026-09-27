# Voxelate

Lets you import an image as a voxel-style 3D mesh in Blender.

Be aware that the imported mesh will have a maniform grid-like topology, however for the UVs, the UV-vertices at the edges are set in slightly, otherwise, when on the edge they would be Z-fighting with the adjacent transparent pixel, which just results in flickering. This makes the UV-map a bit difficult to use later on.

> [!Warning]
> I somehow made the code really slow. It takes a couple of seconds for creating a mesh from a 32x32 Image. I would not recommend using this for images much larger than this until I updated it to be faster.

## Install

1. Package the `src/` to a `.zip` file with the folder itself being the root and import it into Blender (or get it from the releases if I have set them up)
2. In Blender import the addon from local disc (open **Edit -> Preferences -> Add-ons -> The Arrow Dropdown in the top corner -> Install from disc** and select the ZIP-folder). Enable it if not enabled automatically.
