import bpy
import bmesh
import os
import re
from collections.abc import Sequence
from typing import cast

from mathutils import Vector


def image_base_name(image_name: str) -> str:
    return os.path.splitext(re.sub(r"\.\d{3}$", "", image_name))[0]


def load_image(filename: str) -> bpy.types.Image:
    # TODO: Currently assumes filename exists beside the current Blender
    # file
    return bpy.data.images.load(
        os.path.join(os.path.dirname(bpy.data.filepath), filename)
    )


def get_image_data(image: bpy.types.Image) -> tuple[int, int, Sequence[float]]:
    # TODO: Currently assumes image has accessible RGBA pixel data and supports
    # Transparency (Not sure if all loaded images automatically get added an
    # alpha channel)

    # Some sort of weird update introduced a regression here. Theoretically for
    # Blender itself It works to just unpack the sequence directly, however
    # Pyright complains. I dont like red squiggly lines
    size: Sequence[int] = cast(Sequence[int], image.size)
    return size[0], size[1], cast(Sequence[float], image.pixels)


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
    # TODO: Currently assumes the mask dimensions match the image and creates
    # a new mesh

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


# This method requires a "blank" material as setup as it expects a
# PrincipledBSDF as well as a material out to be existant already
def create_material(
    object: bpy.types.Object, image: bpy.types.Image
) -> bpy.types.Material:
    # TODO: Currently assumes object is a mesh and the default material output
    # nodes exist

    image_name: str = image_base_name(image.name)
    material: bpy.types.Material = bpy.data.materials.new(name=image_name)

    node_tree: bpy.types.NodeTree = cast(bpy.types.NodeTree, material.node_tree)
    nodes: bpy.types.Nodes = node_tree.nodes
    links: bpy.types.NodeLinks = node_tree.links

    # This is also some sort of Stub problems with the Blender 5.1 going up
    # from 4.3 There has to be a better way to write this to make the LSP
    # happy, but I cannot be bothered to find it.
    image_texture_node: bpy.types.ShaderNodeTexImage = cast(
        bpy.types.ShaderNodeTexImage, nodes.new("ShaderNodeTexImage")
    )
    principled_node: bpy.types.ShaderNodeBsdfPrincipled = cast(
        bpy.types.ShaderNodeBsdfPrincipled, nodes.get("Principled BSDF")
    )
    output_node: bpy.types.ShaderNodeOutputMaterial = cast(
        bpy.types.ShaderNodeOutputMaterial, nodes.get("Material Output")
    )
    principled_inputs: bpy.types.NodeInputs = cast(
        bpy.types.NodeInputs, principled_node.inputs
    )
    principled_outputs: bpy.types.NodeOutputs = cast(
        bpy.types.NodeOutputs, principled_node.outputs
    )
    texture_outputs: bpy.types.NodeOutputs = cast(
        bpy.types.NodeOutputs, image_texture_node.outputs
    )
    material_inputs: bpy.types.NodeInputs = cast(
        bpy.types.NodeInputs, output_node.inputs
    )

    image_texture_node.image = image
    image_texture_node.interpolation = "Closest"
    image_texture_node.location = (-800, 0)

    # Same 5.1 problem here as on the top part of the method
    roughness_socket: bpy.types.NodeSocketFloat = cast(
        bpy.types.NodeSocketFloat, principled_inputs.get("Roughness")
    )
    roughness_socket.default_value = 0.8

    base_color_socket: bpy.types.NodeSocket = cast(
        bpy.types.NodeSocket, principled_inputs.get("Base Color")
    )
    color_output_socket: bpy.types.NodeSocket = cast(
        bpy.types.NodeSocket, texture_outputs.get("Color")
    )
    bsdf_output_socket: bpy.types.NodeSocket = cast(
        bpy.types.NodeSocket, principled_outputs.get("BSDF")
    )
    surface_input_socket: bpy.types.NodeSocket = cast(
        bpy.types.NodeSocket, material_inputs.get("Surface")
    )

    links.new(color_output_socket, base_color_socket)
    links.new(bsdf_output_socket, surface_input_socket)

    mesh_data: bpy.types.Mesh = cast(bpy.types.Mesh, object.data)
    mesh_data.materials.append(material)

    return material


def create_uv(
    object: bpy.types.Object, image: bpy.types.Image, uv_offset: float = 0.001
) -> bpy.types.MeshUVLoopLayer:
    width, height, _ = get_image_data(image)
    mesh_data: bpy.types.Mesh = cast(bpy.types.Mesh, object.data)
    uv_layer: bpy.types.MeshUVLoopLayer = mesh_data.uv_layers.new(name=image.name)
    # For the Side-faces there is some z-fighting since the polygon is on the
    # edge between the 0-Alpha and 1-Alpha Pixels. This microstep which nudges
    # the polygon to the "Colorful" pixel should fix it. The size is arbitrary
    # and can probably be even smaller In any case the UV map is fucked for
    # later usage. This also makes the function waaaay more complicated than
    # it probably should be
    microstep: float = uv_offset

    def is_opaque(x: int, y: int) -> bool:
        # I hope that the image_to_transparency_mask call here gets optimzied
        # away somehow otherwise this is the peak inefficient
        return (
            0 <= x < width
            and 0 <= y < height
            and image_to_transparency_mask(image)[height - y - 1][x]
        )

    for polygon in mesh_data.polygons:
        # This also is some sort of weird change in blender 5.1 to make the
        # typehints happy. It should work to just pass this without the cast.
        coordinates: list[Vector] = [
            mesh_data.vertices[index].co
            for index in cast(Sequence[int], polygon.vertices)
        ]
        min_x: int = int(min(vertex.x for vertex in coordinates))
        min_y: int = int(min(vertex.y for vertex in coordinates))
        max_x: int = int(max(vertex.x for vertex in coordinates))
        max_y: int = int(max(vertex.y for vertex in coordinates))

        if abs(polygon.normal.x) > 0.5:
            pixel_x: int = min_x if polygon.normal.x < 0 else max_x - 1
            pixel_y: int = min_y
        elif abs(polygon.normal.y) > 0.5:
            pixel_x: int = min_x
            pixel_y: int = min_y if polygon.normal.y < 0 else max_y - 1
        else:
            pixel_x: int = min_x
            pixel_y: int = min_y

        for loop_index in range(
            polygon.loop_start, polygon.loop_start + polygon.loop_total
        ):
            x: float = mesh_data.vertices[mesh_data.loops[loop_index].vertex_index].co.x
            y: float = mesh_data.vertices[mesh_data.loops[loop_index].vertex_index].co.y

            # Microsteps
            if x == pixel_x and not is_opaque(pixel_x - 1, pixel_y):
                x += microstep
            elif x == pixel_x + 1 and not is_opaque(pixel_x + 1, pixel_y):
                x -= microstep
            if y == pixel_y and not is_opaque(pixel_x, pixel_y - 1):
                y += microstep
            elif y == pixel_y + 1 and not is_opaque(pixel_x, pixel_y + 1):
                y -= microstep

            uv_layer.data[loop_index].uv = (x / width, y / height)

    return uv_layer


def create_voxel_mesh(
    image: bpy.types.Image,
    name: str,
    center: bool,
    do_create_material: bool,
    uv_offset: float,
) -> bpy.types.Object:
    mesh: bpy.types.Object = generate_mesh_from_transparency_mask(image, name)
    if center:
        center_mesh(mesh, image)
    if do_create_material:
        create_material(mesh, image)
    create_uv(mesh, image, uv_offset)
    return mesh
