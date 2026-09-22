import bpy
import os


def load_image(filename: str) -> bpy.types.Image:
    return bpy.data.images.load(os.path.join(os.path.dirname(bpy.data.filepath), filename))


def image_to_transparency_mask(image: bpy.types.Image) -> list[list[bool]]:
    width, height = image.size
    return [
        [image.pixels[:][(y * width + x) * 4 + 3] > 0.0 for x in range(width)]
        for y in range(height)
    ]


def image_to_rgb_array(image: bpy.types.Image) -> list[list[list[float]]]:
    width, height = image.size

    return [
        [
            [
                image.pixels[:][(y * width + x) * 4],
                image.pixels[:][(y * width + x) * 4 + 1],
                image.pixels[:][(y * width + x) * 4 + 2],
            ]
            for x in range(width)
        ]
        for y in range(height)
    ]


def main() -> None:
    image = load_image("ExampleImage.png")
    print(image_to_transparency_mask(image))
    print(image_to_rgb_array(image))


if __name__ == "__main__":
    main()
