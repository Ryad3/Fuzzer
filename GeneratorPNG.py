import struct
import zlib
import random

class PNGFuzzer:
    
    def png_signature(self):
        """Return PNG signature bytes"""
        return b'\x89PNG\r\n\x1a\n'
    
    def create_chunk(self, chunk_type: bytes, data: bytes) -> bytes:
        """Create a PNG chunk with proper CRC"""
        length = len(data)
        length_bytes = struct.pack('>I', length)  # 4-byte unsigned integer
        crc = zlib.crc32(chunk_type + data)  # CRC calculated on type and data
        crc_bytes = struct.pack('>I', crc)
        
        return length_bytes + chunk_type + data + crc_bytes
    
    def create_ihdr_chunk(self):
        """Create IHDR chunk with basic image properties"""
        width = random.randint(5, 20)
        height = random.randint(5, 20)
        bit_depth = 8
        color_type = 2  # RGB
        compression = 0
        filter_method = 0
        interlace = 0
        
        data = struct.pack('>IIBBBBB', width, height, bit_depth,
                         color_type, compression, filter_method, interlace)
        return self.create_chunk(b'IHDR', data), width, height
    
    def create_idat_chunk(self, width, height):
        """Create IDAT chunk with image data"""
        
        # Create random colored pixels
        def random_color_row():
            return b''.join(bytes([random.randint(0, 255) for _ in range(3)]) for _ in range(width))
        
        # Create scanlines with filter byte 0
        image_data = b''
        for _ in range(height):
            scanline = b'\x00' + random_color_row()  # Filter type 0 + RGB data
            image_data += scanline
        
        compressed_data = zlib.compress(image_data)
        return self.create_chunk(b'IDAT', compressed_data)
    
    def create_iend_chunk(self):
        """Create IEND chunk (always empty)"""
        return self.create_chunk(b'IEND', b'')
    
    def generate_png(self, filename: str):
        """Generate a valid PNG file"""
        
        # Generate the actual PNG data
        ihdr_chunk, width, height = self.create_ihdr_chunk()
        idat_chunk = self.create_idat_chunk(width, height)
        iend_chunk = self.create_iend_chunk()
        
        data = (self.png_signature() +
                ihdr_chunk +
                idat_chunk +
                iend_chunk)
        
        with open(filename, 'wb') as f:
            f.write(data)
        
        return width, height

if __name__ == "__main__":
    png_fuzzer = PNGFuzzer()
    width, height = png_fuzzer.generate_png("fuzzed_image.png")
    print(f"Generated PNG with dimensions: {width}x{height}")