# Voxelate

Lets you import an image as a voxel-style 3D mesh in Blender.

Be aware that the imported mesh will have a maniform grid-like topology, however for the UVs, the UV-vertices at the edges are set in slightly, otherwise, when on the edge they would be Z-fighting with the adjacent transparent pixel, which just results in flickering. This makes the UV-map a bit difficult to use later on.

> [!Warning]
> I somehow made the code really slow. It takes a couple of seconds for creating a mesh from a 32x32 Image. I would not recommend using this for images much larger than this until I updated it to be faster.

## Install

1. Package the `src/` to a `.zip` file with the folder itself being the root and import it into Blender (or get it from the releases if I have set them up)
2. In Blender import the addon from local disc (open **Edit -> Preferences -> Add-ons -> The Arrow Dropdown in the top corner -> Install from disc** and select the ZIP-folder). Enable it if not enabled automatically.

## Usage

In the 3D Viewporet, you can create a new Mesh with **Add (Ctrl + A) -> Image -> Image as Voxelmesh** and then select the image.

This currently supports a bunch of file formats even ones that don't make sense as they don't support transparency like `.jpeg`. In theory it should support `.bmp`, `.exr`, `.hdr`, `.jp(e)g`, `.png`, `.tga`, `.tif(f)`, `.webp`, however I have only really tested `.png`.

## ToDo

Here are some thing I would like to add whenever I find time for it. I actively update this list, so if notice that an entry disappeared I either added it or thought the idea was stupid.

- Centering the pivot of the object
- Adding import options for the name, material and UV offset
- Improving performance
- Adjustable thickness
