import bpy
import bmesh
import os
from collections.abc import Sequence
from typing import Tuple, cast


def load_image(filename: str) -> bpy.types.Image:
    return bpy.data.images.load(
        os.path.join(os.path.dirname(bpy.data.filepath), filename)
    )


def get_image_data(image: bpy.types.Image) -> Tuple[int, int, Sequence[float]]:
    return (image.size[0], image.size[1], cast(Sequence[float], image.pixels))


def image_to_transparency_mask(image: bpy.types.Image) -> list[list[bool]]:
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


def transparency_mask_to_mesh(
    image: bpy.types.Image, name: str = "VoxelatedImage"
) -> bpy.types.Object:

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
    width, height, _ = get_image_data(image)
    mesh.location.x = -width / 2
    mesh.location.y = -height / 2


def main() -> None:
    image: bpy.types.Image = load_image("ExampleImage.png")
    mesh: bpy.types.Object = transparency_mask_to_mesh(image)
    center_mesh(mesh, image)


if __name__ == "__main__":
    main()
