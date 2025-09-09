import bpy
import os

blend_file_dir: str = os.path.dirname(bpy.data.filepath)

image: bpy.types.Image = bpy.data.images.load(os.path.join(blend_file_dir, "./ExampleImage.png"))
print(image.channels)

