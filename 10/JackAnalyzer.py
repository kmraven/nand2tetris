import sys, os
from typing import List
from CompilationEngine import CompilationEngine


def main(root_dir: str, jack_files: List[str]) -> None:
    os.makedirs(os.path.join(root_dir, "compile_test"), exist_ok=True)
    for jack_file in jack_files:
        print(f"Compiling {os.path.join(root_dir, jack_file)}")
        ce = CompilationEngine(
            jack_filepath=os.path.join(root_dir, jack_file),
            xml_filepath=os.path.join(root_dir, f"compile_test/{os.path.splitext(jack_file)[0]}.xml"),
        )
        print(f"Class name list: {ce.class_name_list}")
    print("Compilation complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <jack_file | jack_directory>")
        sys.exit(1)
    jack_path = sys.argv[1]
    if not os.path.exists(jack_path):
        print(f"Error: The file or directory '{jack_path}' does not exist.")
        sys.exit(1)
    if os.path.isdir(jack_path):
        root_dir = jack_path
        jack_files = [os.path.basename(f) for f in os.listdir(jack_path) if f.endswith('.jack')]
        if not jack_files:
            print(f"No .jack files found in directory: {jack_path}")
            sys.exit(1)
    else:
        if not jack_path.endswith('.jack'):
            print(f"Error: The file '{jack_path}' is not a .jack file.")
            sys.exit(1)
        root_dir = '.'
        jack_files = [jack_path]
    main(root_dir, jack_files)
