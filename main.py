import os
import glob
import shutil
import subprocess


def load_library():
    """Loads and concatenates all font definition files from Libraries/ directory."""
    libraries_dir = 'Libraries/'
    combined_content = ''

    for file_path in glob.glob(os.path.join(libraries_dir, '*.txt')):
        with open(file_path, 'r', encoding='utf-8') as file:
            combined_content += file.read() + '\n'

    return combined_content


def is_key_line(line):
    """Identifies character definition lines and section separators.

    Key lines can be:
    - Single pipe '|' acting as a section separator
    - Lines with pipe characters forming a complete separator
    - Lines with space-separated symbols defining new characters
    """
    return line.count('|') < 2


def parse_key(line):
    """Extracts character symbols from definition lines."""
    stripped = line.strip()
    if stripped == '|':
        return ('|',)
    parts = stripped.split()
    return tuple(parts) if parts else (' ',)


def transpose_matrix(data):
    """Restructures row-based art data into column-based variants.

    Transposition enables handling multiple width variants stored as columns.
    Example for 2 variants:
    Original rows: [["v1r1", "v2r1"], ["v1r2", "v2r2"]]
    After transpose: [["v1r1", "v1r2"], ["v2r1", "v2r2"]]
    """
    max_cols = max(len(row) for row in data) if data else 1
    return [[row[col] if col < len(row) else '' for row in data]
            for col in range(max_cols)]


def parse_string(input_str):
    """Parses font definition string into structured character data.

    Format specification:
    1. Key line starts with symbols or separator:
       - "A B C" - defines symbols using those characters
       - "|" - section separator
    2. Data lines contain 4 rows of |separated| art segments
    3. Each art segment column represents different width variant

    Example:
    A B
    |seg1_v1|seg1_v2|
    |seg2_v1|seg2_v2|
    |seg3_v1|seg3_v2|
    |seg4_v1|seg4_v2|
    """

    parsed_data = {}
    current_key = None
    current_block = []

    for line in input_str.strip().split('\n'):
        if is_key_line(line):
            if current_key is not None:
                # Handling the blank
                transposed = transpose_matrix(current_block)
                # Double spaces required for proper alignment in Minecraft
                transposed = [[elem.replace(' ', '  ') for elem in row] for row in transposed]
                for key_part in current_key:
                    parsed_data[key_part] = transposed
                current_block = []
            current_key = parse_key(line)
        else:
            elements = [elem for elem in line.split('|')[1:-1]]
            if elements:
                current_block.append(elements)

    if current_key:
        transposed = transpose_matrix(current_block)
        transposed = [[elem.replace(' ', '  ') for elem in row] for row in transposed]
        for key_part in current_key:
            parsed_data[key_part] = transposed

    return parsed_data


def get_user_input(prompt="Enter Text for cyberpunking: "):
    """Gets and validates non-empty input from user."""
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input


def split_into_blocks(input_string):
    """Splits input into 3-character blocks, padding with spaces if needed.

    Maintains strict space-only padding for Minecraft sign compatibility.
    """
    blocks = [input_string[i:i + 3] for i in range(0, len(input_string), 3)]

    if len(blocks[-1]) != 3:
        blocks[-1] = blocks[-1].ljust(3)
        print("Warning: Name isn't evenly divided into signs, padding with spaces")

    return blocks


def prepare_output_directory(name):
    """Creates fresh output directory in Results/ folder."""
    base_dir = 'Results'
    output_dir = os.path.join(base_dir, name)

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def generate_sign_files(character_blocks, output_dir, font_data, short_name):
    """Generates .stendhal sign files for Minecraft mod.

    Uses width variant 0 (6-space/3-block wide art) from font definitions.

    Args:
        :param character_blocks:    List of 3-character strings to render
        :param output_dir:          Target directory for files
        :param font_data:           Processed font definitions from parse_string()
        :param short_name:          Base name for generated files
    """
    for idx, block in enumerate(character_blocks, 1):
        filename = f"cyberpunked_{short_name}_{idx}.stendhal"
        file_path = os.path.join(output_dir, filename)

        # Access width variant 0 (6-space wide art)
        char1 = font_data[block[0]][0]  # [0] selects the 6-space width variant
        char2 = font_data[block[1]][0]
        char3 = font_data[block[2]][0]

        lines = [
            f"{char1[0]}  {char2[0]}  {char3[0]}",  # Top row of the sign
            f"{char1[1]}  {char2[1]}  {char3[1]}",  # Second row
            f"{char1[2]}  {char2[2]}  {char3[2]}",  # Third row
            f"{char1[3]}  {char2[3]}  {char3[3]}"  # Bottom row
        ]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"title: {filename[:-8]}\nlines:\n")
            f.write('\n'.join(f"#- {line}" for line in lines))


def sanitize_filename(name):
    """Replaces Windows-prohibited characters with Unicode alternatives.

    Ensures filenames are Minecraft-compatible and Windows-safe.
    """
    char_replacements = {
        '<': '⧀', '>': '⧁', ':': 'ː',
        '"': '`', '/': '⧸', '\\': '⧹',
        '|': 'ǀ', '?': '？', '*': '⁎',
        '\t': '    '
    }
    sanitized = ''.join(char_replacements.get(c, c) for c in name)
    sanitized = sanitized.rstrip(' .')
    return sanitized[:255]


def main():
    """Main workflow controller for generating cyberpunk-style Minecraft signs."""
    font_data = parse_string(load_library())

    while True:
        user_text = get_user_input()
        clean_name = sanitize_filename(user_text[:15])
        character_blocks = split_into_blocks(user_text)
        output_dir = prepare_output_directory(clean_name)

        generate_sign_files(character_blocks, output_dir, font_data, clean_name)
        subprocess.Popen(f'explorer "{os.path.abspath(output_dir)}"')

        print("Copy generated files to minecraft/config/stendhal/signs/")


if __name__ == "__main__":
    main()
