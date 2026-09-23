import bpy
import bmesh
import os
import re
from collections.abc import Sequence
from typing import Tuple, cast


def image_base_name(image_name: str) -> str:
    name_without_duplicate_suffix = re.sub(r"\.\d{3}$", "", image_name)
    return os.path.splitext(re.sub(r"\.\d{3}$", "", image_name))[0]


def load_image(filename: str) -> bpy.types.Image:
    # TODO: Currently assumes filename exists beside the current Blender file
    return bpy.data.images.load(
        os.path.join(os.path.dirname(bpy.data.filepath), filename)
    )


def get_image_data(image: bpy.types.Image) -> Tuple[int, int, Sequence[float]]:
    # TODO: Currenlty assumes image has accessible RGBA pixel data and supports Transparency (Not sure if all loaded images automatically get added an alpha channel
    return (image.size[0], image.size[1], cast(Sequence[float], image.pixels))


def image_to_transparency_mask(image: bpy.types.Image) -> list[list[bool]]:
    # TODO: Currently assumes image pixels are arranged as RGBA values
    width, height, pixels = get_image_data(image)

    return [
        [pixels[(y * width + x) * 4 + 3] > 0.0 for x in range(width)]
        for y in range(height - 1, -1, -1)
    ]


def image_to_rgb_array(image: bpy.types.Image) -> list[list[list[float]]]:
    width, height, pixels = get_image_data(image)

    return [
        [
            [
                pixels[(y * width + x) * 4],
                pixels[(y * width + x) * 4 + 1],
                pixels[(y * width + x) * 4 + 2],
            ]
            for x in range(width)
        ]
        for y in range(height - 1, -1, -1)
    ]


def print_image_pixels(image: bpy.types.Image) -> None:
    width, height, pixels = get_image_data(image)

    for y in range(height - 1, -1, -1):
        print(
            "".join(
                "#" if pixels[(y * width + x) * 4 + 3] != 0.0 else " "
                for x in range(width)
            )
        )


def generate_mesh_from_transparency_mask(
    image: bpy.types.Image, name: str = "Voxel Mesh"
) -> bpy.types.Object:
    # TODO: Currently assumes the mask dimensions match the image and creates a new mesh

    width, height, _ = get_image_data(image)
    transparency_mask: list[list[bool]] = image_to_transparency_mask(image)
    mesh: bpy.types.Mesh = bpy.data.meshes.new(name)
    obj: bpy.types.Object = bpy.data.objects.new(name, mesh)
    bm: bmesh.types.BMesh = bmesh.new()
    vertices: dict[tuple[int, int, int], bmesh.types.BMVert] = dict()

    bpy.context.collection.objects.link(obj)

    def get_vertex(x: int, y: int, z: int) -> bmesh.types.BMVert:
        key: tuple[int, int, int] = (x, y, z)
        if key not in vertices:
            vertices[key] = bm.verts.new((float(x), float(y), float(z)))
        return vertices[key]

    for row, mask_row in enumerate(transparency_mask):
        y: int = height - row - 1
        for x, is_opaque in enumerate(mask_row):
            if not is_opaque:
                continue

            # Bottom and top faces.
            bm.faces.new(
                (
                    get_vertex(x, y, 0),
                    get_vertex(x, y + 1, 0),
                    get_vertex(x + 1, y + 1, 0),
                    get_vertex(x + 1, y, 0),
                )
            )
            bm.faces.new(
                (
                    get_vertex(x, y, 1),
                    get_vertex(x + 1, y, 1),
                    get_vertex(x + 1, y + 1, 1),
                    get_vertex(x, y + 1, 1),
                )
            )

            # Side Faces
            if x == 0 or not mask_row[x - 1]:
                bm.faces.new(
                    (
                        get_vertex(x, y, 0),
                        get_vertex(x, y, 1),
                        get_vertex(x, y + 1, 1),
                        get_vertex(x, y + 1, 0),
                    )
                )
            if x == width - 1 or not mask_row[x + 1]:
                bm.faces.new(
                    (
                        get_vertex(x + 1, y, 0),
                        get_vertex(x + 1, y + 1, 0),
                        get_vertex(x + 1, y + 1, 1),
                        get_vertex(x + 1, y, 1),
                    )
                )
            if row == 0 or not transparency_mask[row - 1][x]:
                bm.faces.new(
                    (
                        get_vertex(x, y + 1, 0),
                        get_vertex(x, y + 1, 1),
                        get_vertex(x + 1, y + 1, 1),
                        get_vertex(x + 1, y + 1, 0),
                    )
                )
            if row == height - 1 or not transparency_mask[row + 1][x]:
                bm.faces.new(
                    (
                        get_vertex(x, y, 0),
                        get_vertex(x + 1, y, 0),
                        get_vertex(x + 1, y, 1),
                        get_vertex(x, y, 1),
                    )
                )

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj


def center_mesh(mesh: bpy.types.Object, image: bpy.types.Image) -> None:
    # TODO: Currently assumes mesh is the object generated from image
    width, height, _ = get_image_data(image)
    mesh.location.x = -width / 2
    mesh.location.y = -height / 2

# This methods requires a "blank" material as setup as it expects
# a PrincipledBSDF as well as a material out to be existant already
def create_material(
    object: bpy.types.Object, image: bpy.types.Image
) -> bpy.types.Material:
    # TODO: Currently assumes object is a mesh and the default material output nodes exist

    image_name: str = image_base_name(image.name)
    material: bpy.types.Material = bpy.data.materials.new(name=image_name)
    material.use_nodes = True

    node_tree: bpy.types.NodeTree = cast(bpy.types.NodeTree, material.node_tree)
    nodes: bpy.types.Nodes = node_tree.nodes
    links: bpy.types.NodeLinks = node_tree.links

    image_texture_node: bpy.types.ShaderNodeTexImage = cast(
        bpy.types.ShaderNodeTexImage, nodes.new("ShaderNodeTexImage")
    )
    principled_node: bpy.types.ShaderNodeBsdfPrincipled = cast(
        bpy.types.ShaderNodeBsdfPrincipled, nodes.get("Principled BSDF")
    )
    output_node: bpy.types.ShaderNodeOutputMaterial = cast(
        bpy.types.ShaderNodeOutputMaterial, nodes.get("Material Output")
    )

    image_texture_node.image = image
    image_texture_node.location = (-400, 0)
    roughness_socket: bpy.types.NodeSocketFloat = cast(
        bpy.types.NodeSocketFloat, principled_node.inputs["Roughness"]
    )
    roughness_socket.default_value = 0.8

    links.new(
        image_texture_node.outputs["Color"],
        principled_node.inputs["Base Color"],
    )
    links.new(
        principled_node.outputs["BSDF"],
        output_node.inputs["Surface"],
    )

    mesh_data: bpy.types.Mesh = cast(bpy.types.Mesh, object.data)
    mesh_data.materials.append(material)

    return material


def main() -> None:
    image: bpy.types.Image = load_image("ExampleImage.png")
    image_name: str = image_base_name(image.name)
    mesh: bpy.types.Object = generate_mesh_from_transparency_mask(image, image_name)
    center_mesh(mesh, image)
    create_material(mesh, image)


if __name__ == "__main__":
    main()
