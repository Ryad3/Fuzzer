import random
from PIL import Image, UnidentifiedImageError
import os
import sys

class ByteMutationFuzzer:
    def __init__(self, seed_file, output_dir, format):
        self.seed_file = seed_file
        self.population = [seed_file]
        self.output_dir = output_dir
        self.format = format
        os.makedirs(output_dir, exist_ok=True)

    def byteflip(self, content):
        """Flip a random byte in the file content."""
        index = random.randint(0, len(content) - 1)
        original_byte = content[index]
        flipped_byte = random.randint(0, 255)  # Replace the byte with a random value
        print(f"Byteflip Mutation: Index {index}, Original Byte {hex(original_byte)}, Flipped Byte {hex(flipped_byte)}")
        return content[:index] + bytes([flipped_byte]) + content[index + 1:]

    def insert_byte(self, content):
        """Insert a random byte at a random position."""
        index = random.randint(0, len(content))
        random_byte = random.randint(0, 255)
        print(f"Insert Byte Mutation: Index {index}, Inserted Byte {hex(random_byte)}")
        return content[:index] + bytes([random_byte]) + content[index:]

    def delete_byte(self, content):
        """Delete a random byte from the file content."""
        if len(content) == 0:
            return content
        index = random.randint(0, len(content) - 1)
        print(f"Delete Byte Mutation: Index {index}, Deleted Byte {hex(content[index])}")
        return content[:index] + content[index + 1:]

    def mutate(self, content):
        """Apply a random mutation (byteflip, insert byte, or delete byte) to the content."""
        mutation = random.choice([self.byteflip, self.insert_byte, self.delete_byte])
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
                img.verify()  # Verify the image integrity
            return True
        except (FileNotFoundError, ValueError, TypeError) as e: # OSError, UnidentifiedImageError
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

    _, file_extension = os.path.splitext(seed_file)

    print("\nRunning ByteMutationFuzzer with byte-level mutations:")
    byte_fuzzer = ByteMutationFuzzer(seed_file, output_dir, file_extension)
    byte_fuzzer.run(mutations=10000000)