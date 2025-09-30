import bpy
import os

blend_file_dir: str = os.path.dirname(bpy.data.filepath)

image: bpy.types.Image = bpy.data.images.load(os.path.join(blend_file_dir, "./ExampleImage.png"))
print(image.channels)

# Get image dimensions
width = image.size[0]
height = image.size[1]
print(f"Image size: {width}x{height}")

# Create a new mesh and object
mesh = bpy.data.meshes.new("PixelMesh")
obj = bpy.data.objects.new("PixelObject", mesh)

# Link object to the scene
bpy.context.collection.objects.link(obj)

# Create vertices at each pixel position
vertices = []
for y in range(height):
    for x in range(width):
        # Create vertex at (x, y, 0) position
        vertices.append((float(x), float(y), 0.0))

# Update mesh with vertices
mesh.from_pydata(vertices, [], [])
mesh.update()

print(f"Created {len(vertices)} vertices")

