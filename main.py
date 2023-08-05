import os
import numpy as np
from PIL import Image, ImageOps
from alive_progress import alive_bar


class Error:
    class NoImagesFound(Exception):
        pass


class Blurer:
    def __init__(self, debug: bool = False, size: int = 3):
        self.images = self.find_image()
        self.debug = debug
        self.size = size
        self.process_image(self.images)

        if self.size % 2 == 0:
            self.size += 1  # Make sure that size is always odd.

        if self.size == 3:
            self.size += 2


    def find_image(self) -> list:
        file_formats = ['png', 'jpeg', 'jpg']
        files = list()
        input_directory = "input"
        for file in os.listdir(input_directory):
            if file.split(".")[1] in file_formats:
                image = Image.open(os.path.join(os.getcwd(), input_directory, file))
                width, height = image.size
                if width < 3 or height < 3:
                    print("Minimum size of an supported image is 3x3! Skipping...")
                    continue
                files.append(os.path.join(os.getcwd(), "input", file))

        if files:
            return files

        raise Error.NoImagesFound(f"No images could be found the {input_directory}. "
                                  f"Accepted File Formats: {' '.join(file_formats)}")

    def scan_pixels_math(self, x, y, width, height, size, layer) -> list:
        scanner = []
        offset = size - 3

        pos = []
        for l in range(1, layer + 1):
            new_x = max(x - l, 0)
            new_y = max(y - l, 0)
            x_coordinate = min(new_x, width - 1)
            y_coordinate = min(new_y, height - 1)

            pos.append((x_coordinate, y_coordinate))

        scanner.append(pos)

        return scanner

    def process_image(self, images):
        for path in images:
            image = Image.open(path)
            width, height = image.size

            print(f"Working on {os.path.basename(path)}\nImage Size: {width}x{height}\nGrid Size : {self.size}x{self.size} ({self.size ** 2})")

            # Convert it to grayscale, for simplicity
            image = ImageOps.grayscale(image)

            img_array = np.array(image)

            # Create a copy of the array to store the blurred image
            blurred_array = np.empty_like(img_array, dtype=np.uint8)

            with alive_bar(width * height, title="Image Processing") as bar:
                for y in range(height):
                    for x in range(width):
                        for layer in range(1, self.size // 2 + 1):
                            current_scan_pixels = self.scan_pixels_math(x, y, width, height, self.size, layer)
                            neighborhood_sum = 0

                            for pos in current_scan_pixels:
                                for scanned_pixel in pos:
                                    sx, sy = scanned_pixel
                                    neighborhood_sum += img_array[sy, sx]

                            blurred_array[y, x] = neighborhood_sum // len(current_scan_pixels[0])
                        bar()

            # Convert the NumPy array back to an Image
            blurred_image = Image.fromarray(blurred_array)

            if not os.path.exists(os.path.join(os.getcwd(), "output")):
                os.mkdir("output")

            blurred_image.save(fp=os.path.join(os.getcwd(), "output", os.path.basename(path)))
            print("Finished Image!!!")


if __name__ == "__main__":
    size = input("Enter Size, the bigger the slower: ")

    try:
        size = int(size)
    except ValueError:
        print("Error Getting size, defaulting to 3.")

    b = Blurer(False, size)
