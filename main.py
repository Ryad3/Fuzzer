import sys
import os
import shutil
from GrammarGeneratorBMP import BMPFuzzer
from GeneratorPNG import PNGFuzzer
from MutationByte import ByteMutationFuzzer
from MutationBit import MutationFuzzer

def clean_directory():
    """Delete all folders in the same directory as this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for item in os.listdir(script_dir):
        item_path = os.path.join(script_dir, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)

def generate_files(file_type, num_files, output_dir, mutation_type, num_mutations):
    """Generate BMP or PNG files and optionally fuzz the first generated file."""
    os.makedirs(output_dir, exist_ok=True)

    seed_file = None
    generated_files = []

    if file_type.lower() == 'bmp':
        bmp_fuzzer = BMPFuzzer()
        for i in range(num_files):
            bmp_data = bmp_fuzzer.generate_valid_bmp()
            file_path = os.path.join(output_dir, f"image_{i + 1}.bmp")
            with open(file_path, 'wb') as f:
                f.write(bmp_data.encode('latin1'))
            print(f"Generated: {file_path}")
            generated_files.append(file_path)
            if i == 0:
                seed_file = file_path

    elif file_type.lower() == 'png':
        png_fuzzer = PNGFuzzer()
        for i in range(num_files):
            file_path = os.path.join(output_dir, f"image_{i + 1}.png")
            width, height = png_fuzzer.generate_png(file_path)
            print(f"Generated: {file_path} with dimensions {width}x{height}")
            generated_files.append(file_path)
            if i == 0:
                seed_file = file_path
    else:
        print("Unsupported file type. Use 'bmp' or 'png'.")
        return

    # Add generated files to the population of the fuzzer
    if mutation_type.lower() == 'byte':
        fuzzer = ByteMutationFuzzer(seed_file, output_dir, os.path.splitext(seed_file)[1])
    elif mutation_type.lower() == 'bit':
        fuzzer = MutationFuzzer(seed_file, output_dir, os.path.splitext(seed_file)[1])
    else:
        print("Unsupported mutation type. Use 'byte' or 'bit'.")
        return

    fuzzer.population.extend(generated_files)
    print(f"Added {len(generated_files)} files to the fuzzer population.")

    # Perform fuzzing on the seed file
    if seed_file:
        print(f"Fuzzing the seed file: {seed_file} using {mutation_type} mutation with {num_mutations} mutations")
        fuzzer.run(mutations=num_mutations)

def fuzz_files(seed_file, mutation_type, output_dir, num_mutations):
    """Fuzz files using byte or bit mutations."""
    _, file_extension = os.path.splitext(seed_file)

    if mutation_type.lower() == 'byte':
        fuzzer = ByteMutationFuzzer(seed_file, output_dir, file_extension)
    elif mutation_type.lower() == 'bit':
        fuzzer = MutationFuzzer(seed_file, output_dir, file_extension)
    else:
        print("Unsupported mutation type. Use 'byte' or 'bit'.")
        return

    fuzzer.run(mutations=num_mutations)

def main():
    clean_directory()

    if len(sys.argv) < 6:
        print("\nUsage:\n")
        print("Generate mode:")
        print("  python main.py generate <file_type> <num_files> <output_dir> <mutation_type> <num_mutations>")
        print("  Example: python main.py generate bmp 10 populations byte 100\n")
        print("Fuzz mode:")
        print("  python main.py fuzz <mutation_type> <num_mutations> <output_dir> <seed_file>")
        print("  Example: python main.py fuzz byte 50 populations image.bmp\n")
        sys.exit(1)

    mode = sys.argv[1].lower()
    option = sys.argv[2]
    num_files_or_mutations = int(sys.argv[3])
    output_dir = sys.argv[4]

    if mode == 'generate':
        if len(sys.argv) < 7:
            print("\nError: Missing arguments for generate mode.")
            print("Usage: python main.py generate <file_type> <num_files> <output_dir> <mutation_type> <num_mutations>")
            sys.exit(1)
        mutation_type = sys.argv[5]
        num_mutations = int(sys.argv[6])
        generate_files(option, num_files_or_mutations, output_dir, mutation_type, num_mutations)

    elif mode == 'fuzz':
        if len(sys.argv) < 6:
            print("\nError: Missing arguments for fuzz mode.")
            print("Usage: python main.py fuzz <mutation_type> <num_mutations> <output_dir> <seed_file>")
            sys.exit(1)

        seed_file = sys.argv[5]
        fuzz_files(seed_file, option, output_dir, num_files_or_mutations)

    else:
        print("\nError: Unsupported mode. Use 'generate' or 'fuzz'.")

if __name__ == "__main__":
    main()