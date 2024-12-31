from fuzzingbook.GrammarFuzzer import GrammarFuzzer
import random
import struct
import io
from PIL import Image

class BMPFuzzer:
    def __init__(self):
        self.fuzzer = None
        self.width = None
        self.height = None
        self.define_bmp_grammar()

    def define_bmp_grammar(self):
        """Define the grammar dynamically based on width and height."""
        self.width = random.randint(1, 10)  # Width between 1 and 10 pixels
        self.height = random.randint(1, 10)  # Height between 1 and 10 pixels

        row_size = (self.width * 3 + 3) & ~3  # Row size aligned to 4 bytes
        pixel_data_size = row_size * self.height
        file_size = 14 + 40 + pixel_data_size  # Header + InfoHeader + Pixel Data

        self.bmp_grammar = {
            "<start>": ["<header><info_header><pixel_data>"],

            # BMP Header (14 bytes)
            "<header>": [
                "BM<file_size><reserved><data_offset>"
            ],
            "<file_size>": [self.to_little_endian_str(file_size, 4)],
            "<reserved>": ["\x00\x00\x00\x00"],
            "<data_offset>": ["\x36\x00\x00\x00"],

            # Info Header (40 bytes)
            "<info_header>": [
                "<info_size><width><height><planes><bpp><compression><image_size><xppm><yppm><colors_used><important_colors>"
            ],
            "<info_size>": ["\x28\x00\x00\x00"],  # Info header size = 40 bytes
            "<width>": [self.to_little_endian_str(self.width, 4)],
            "<height>": [self.to_little_endian_str(self.height, 4)],
            "<planes>": ["\x01\x00"],  # 1 color plane
            "<bpp>": ["\x18\x00"],  # 24 bits per pixel (RGB)
            "<compression>": ["\x00\x00\x00\x00"],  # No compression (BI_RGB)
            "<image_size>": [self.to_little_endian_str(pixel_data_size, 4)],
            "<xppm>": ["\x13\x0B\x00\x00"],  # Horizontal resolution: 2835 pixels/meter
            "<yppm>": ["\x13\x0B\x00\x00"],  # Vertical resolution: 2835 pixels/meter
            "<colors_used>": ["\x00\x00\x00\x00"],  # No palette (all colors used)
            "<important_colors>": ["\x00\x00\x00\x00"],  # All colors are important

            # Pixel Data (Dynamic based on width and height)
            "<pixel_data>": ["<row>" * self.height],
            "<row>": ["<pixel>" * self.width + "<padding>"],
            "<pixel>": [
                "\xFF\x00\x00",  # Red
                "\x00\xFF\x00",  # Green
                "\x00\x00\xFF",  # Blue
                "\xFF\xFF\xFF",  # White
                "\x00\x00\x00"   # Black
            ],
            "<padding>": ["\x00" * (row_size - self.width * 3)]  # Align rows to 4 bytes
        }

        self.fuzzer = GrammarFuzzer(self.bmp_grammar)

    def redefine_bmp_grammar(self):
        """Redefine the grammar with new random dimensions."""
        self.width = random.randint(1, 100)  # Width between 1 and 10 pixels
        self.height = random.randint(1, 100)  # Height between 1 and 10 pixels
        self.define_bmp_grammar()

    @staticmethod
    def to_little_endian(value, length):
        """Convert an integer to little-endian format as a byte string."""
        return struct.pack("<I", value)[:length]

    @staticmethod
    def to_little_endian_str(value, length):
        """Convert an integer to little-endian format as a string."""
        return struct.pack("<I", value)[:length].decode('latin1')

    def generate_valid_bmp(self):
        self.redefine_bmp_grammar()  # Update grammar with new dimensions
        print(f"Width: {self.width}, Height: {self.height}")
        return self.fuzzer.fuzz()

    def show_bmp(self, data):
        try:
            # Load BMP data into memory and show it
            bmp_stream = io.BytesIO(data.encode('latin1'))
            image = Image.open(bmp_stream)
            image.show()
            image.close()
        except Exception as e:
            print(f"Error displaying BMP: {e}")

# Usage example
if __name__ == "__main__":
    bmp_fuzzer = BMPFuzzer()
    for i in range(5):
        # Generate a valid BMP file
        bmp_data = bmp_fuzzer.generate_valid_bmp()

        # Show the BMP image
        bmp_fuzzer.show_bmp(bmp_data)
