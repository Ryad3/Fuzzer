import random
from PIL import Image, UnidentifiedImageError
import os
import sys

class MutationFuzzer:
    def __init__(self, seed_file, output_dir, format):
        self.seed_file = seed_file
        self.population = [seed_file]
        self.output_dir = output_dir
        self.format = format
        os.makedirs(output_dir, exist_ok=True)

    def bitflip(self, content):
        """Flip a random bit in the file content."""
        index = random.randint(0, len(content) - 1)
        bit_position = random.randint(0, 7)
        original_byte = content[index]
        flipped_byte = original_byte ^ (1 << bit_position)
        print(f"Bitflip Mutation: Index {index}, Bit Position {bit_position}, Original Byte {bin(original_byte)}, Flipped Byte {bin(flipped_byte)}")
        return content[:index] + bytes([flipped_byte]) + content[index + 1:]

    def insert_bit(self, content):
        """Insert a random bit at a random position."""
        index = random.randint(0, len(content) - 1)
        bit_position = random.randint(0, 7)
        original_byte = content[index]
        new_byte = (original_byte & ~(1 << bit_position)) | (random.randint(0, 1) << bit_position)
        print(f"Insert Bit Mutation: Index {index}, Bit Position {bit_position}, Original Byte {bin(original_byte)}, New Byte {bin(new_byte)}")
        return content[:index] + bytes([new_byte]) + content[index + 1:]

    def delete_bit(self, content):
        """Delete a random bit at a random position."""
        index = random.randint(0, len(content) - 1)
        bit_position = random.randint(0, 7)
        original_byte = content[index]
        new_byte = original_byte & ~(1 << bit_position)
        print(f"Delete Bit Mutation: Index {index}, Bit Position {bit_position}, Original Byte {bin(original_byte)}, New Byte {bin(new_byte)}")
        return content[:index] + bytes([new_byte]) + content[index + 1:]

    def mutate(self, content):
        """Apply a random mutation (bitflip, insert bit, or delete bit) to the content."""
        mutation = random.choice([self.bitflip, self.insert_bit, self.delete_bit])
        return mutation(content)

    def create_candidate(self):
        """Create a new candidate by mutating a population member."""
        candidate = random.choice(self.population)
        print(f"Chosen file for mutation: {candidate}")
        try:
            with open(candidate, 'rb') as f:
                content = f.read()
            mutated_content = self.mutate(content)
            mutated_file = os.path.join(self.output_dir, f"mutated_{random.randint(0, 1_000_000)}" + self.format)
            with open(mutated_file, 'wb') as f:
                f.write(mutated_content)
            return mutated_file
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return None

    def test_candidate(self, candidate):
        """Test the candidate file with PIL.Image.open."""
        if candidate is None:
            return False
        try:
            with Image.open(candidate) as img:
                pass
            return True
        except (FileNotFoundError, ValueError, TypeError, UnidentifiedImageError, OSError, Image.DecompressionBombError) as e: # UnidentifiedImageError, OSError
            print(f"Test error: {e}")
            return False

    def run(self, mutations=100):
        """Run the fuzzer for a given number of iterations."""
        for _ in range(mutations):
            candidate = self.create_candidate()
            if candidate and self.test_candidate(candidate):
                print(f"[PASS] {candidate} added to population.")
                self.population.append(candidate)
            elif candidate:
                print(f"[FAIL] {candidate} did not pass.")
                os.remove(candidate)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 fuzz.py <seed_image_file>")
        sys.exit(1)

    seed_file = sys.argv[1]
    output_dir = "populations"
    # Determine the file extension
    _, file_extension = os.path.splitext(seed_file)
    fuzzer = MutationFuzzer(seed_file, output_dir, file_extension)
    fuzzer.run(mutations=10000000)