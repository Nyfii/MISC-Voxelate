import bpy
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


def main() -> None:
    image = load_image("ExampleImage.png")
    print(image_to_transparency_mask(image))
    print(image_to_rgb_array(image))
    print_image_pixels(image)


if __name__ == "__main__":
    main()
