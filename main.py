import os
import glob
import shutil
import subprocess
from itertools import product
from typing import List, Dict


def load_library(folder: str) -> str:
    """Loads and concatenates all font definition files from the specified library folder."""
    libraries_dir = f'Libraries/{folder}'
    combined_content = ''

    try:
        for file_path in glob.glob(os.path.join(libraries_dir, '*.txt')):
            with open(file_path, 'r', encoding='utf-8') as file:
                combined_content += file.read() + '\n'
    except Exception as e:
        print(f"Error loading library from {libraries_dir}: {e}")

    return combined_content


def is_key_line(line):
    """Identifies character definition art and section separators.

    Key art can be:
    - Single pipe '|' acting as a section separator
    - Lines with pipe characters forming a complete separator
    - Lines with space-separated symbols defining new characters
    """
    return line.count('|') < 2


def parse_key(line):
    """Extracts character symbols from definition art."""
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
    2. Data art contain 4 rows of |separated| art segments
    3. Each art segment column represents different variant

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
    # For comfort reading file names
    return sanitized[:15]


def get_character_representations(char: str, dictionaries: List[Dict]) -> List[List[str]]:
    """ Collect all possible representations of a character from all dictionaries. """
    all_reps = []
    for dictionary in dictionaries:
        all_reps.extend(dictionary.get(char, []))
    return all_reps or [["    ", "    ", "    ", "    "]]  # Default empty representation

def build_initial_art(input_string: str, char_to_rep: Dict[str, List[str]]) -> List[str]:
    """ Construct initial ASCII art art by combining character representations. """
    lines = ["", "", "", ""]
    for char in input_string:
        char_rep = char_to_rep[char]
        for i in range(4):
            if i < len(char_rep):  # Handle case when representation has <4 art
                lines[i] += char_rep[i] + " "
            else:
                lines[i] += "     "  # Default empty space
    return lines


def add_padding_and_borders(lines: List[str]) -> List[str]:
    """ Add padding and borders to the ASCII art art. """
    for padding in range(11):
        padded_lines = [" " * padding + line for line in lines]
        # Check if all positions 11, 23, 35, etc., are spaces
        is_valid = True
        for line in padded_lines:
            for i in range(11, len(line), 12):
                if i >= len(line) or line[i] != " ":
                    is_valid = False
                    break
            if not is_valid:
                break
        if is_valid:
            # Add borders
            bordered_lines = []
            for line in padded_lines:
                # Add the first '|'
                bordered_line = "|" + line
                # Replace every 12th character (starting from index 12) with '|'
                bordered_line = list(bordered_line)  # Convert to list for easy mutation
                for i in range(12, len(bordered_line), 12):
                    bordered_line[i] = "|"

                # Find the last '|'
                last_pipe_index = "".join(bordered_line).rfind("|")
                # Characters after the last '|'
                chars_after_last_pipe = len(bordered_line) - last_pipe_index - 1
                # If there are characters after the last '|', add spaces to make it 11 characters
                if chars_after_last_pipe > 0:
                    spaces_to_add = 11 - chars_after_last_pipe
                    bordered_line.extend([" "] * spaces_to_add)
                    # Add the final '|'
                    bordered_line.append("|")

                bordered_line = "".join(bordered_line)  # Convert back to string
                bordered_lines.append(bordered_line)
            return bordered_lines
    return None  # No valid padding found


def generate_ascii_art_combinations(input_string: str, dictionaries: List[Dict]) -> List[List[str]]:
    """ Generate all valid ASCII art combinations for input string. """
    unique_chars = list(set(input_string))
    char_options = {char: get_character_representations(char, dictionaries) for char in unique_chars}
    valid_arts = []

    for combination in product(*[char_options[char] for char in unique_chars]):
        char_to_rep = {char: rep for char, rep in zip(unique_chars, combination)}
        if not all(char in char_to_rep for char in input_string):
            continue

        lines = build_initial_art(input_string, char_to_rep)
        bordered_lines = add_padding_and_borders(lines)
        if bordered_lines:
            valid_arts.append(bordered_lines)

    return valid_arts


def print_ascii_art(art: List[str]) -> None:
    print('\n'.join(art))
    print()


def print_ascii_arts(arts: List[List[str]], start_number: int = 1) -> None:
    """
    Print generated ASCII arts with numbering, in reverse order.
    Also display the number of blocks, which is the number of '|' in a line minus 1.
    The option number is preserved based on the original order.
    If there are more than 15 arts, display a message before printing.
    """

    # Iterate over the reversed list but keep the original indices
    for i in range(len(arts) - 1, -1, -1):
        art = arts[i]
        # Calculate the option number based on the original index
        option_number = start_number + i
        num_blocks = art[0].count("|") - 1
        print(f"Option {option_number} (Blocks: {num_blocks}):")
        print_ascii_art(art)
    if len(arts) > 15:
        print(f"Wow! Your computer just made {len(arts)} arts! Now try to pick one.....\n")

def select_art(arts: List[List[str]], start_number: int = 1) -> List[str]:
    """
    Prompt the user to select an art by its option number.
    Returns the selected art.
    """
    while True:
        try:
            # Get user input
            selected_option = int(input("Which option do we continue to work with? "))
            # Convert to 0-based index
            selected_index = selected_option - start_number
            # Validate the index
            if 0 <= selected_index < len(arts):
                return arts[selected_index]
            else:
                print(f"Invalid option. Please enter a number between {start_number} and {len(arts) + start_number - 1}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def ask_for_shift() -> str:
    """
    Ask the user if they want to shift the art left, right, proceed to the next step, or quit.
    Accepts 'left', 'right', 'next', 'quit' or 'l', 'r', 'p', 'n', 'q'.
    Returns 'left', 'right', 'next', or 'quit'.
    """
    while True:
        response = input("Do you want to shift the art left, right, proceed, or quit? ").strip().lower()
        if response in ["left", "right", "next", "quit", "l", "r", "p", "n", "q"]:
            # Map 'l', 'r', 'p', 'n', 'q' to full words
            if response == "l":
                return "left"
            elif response == "r":
                return "right"
            elif response in ["p", "n"]:
                return "next"
            elif response == "q":
                return "quit"
            else:
                return response
        else:
            print("Invalid input. Please enter 'left', 'right', 'next', 'quit', or 'l', 'r', 'p', 'n', 'q'.")


def remove_bars(data):
    # Убираем лишние символы и разбиваем строки
    processed_data = []
    for line in data:
        # Убираем первый и последний символ '|'
        line = line.strip('|')
        # Разбиваем строку по символу '|'
        processed_line = line.split('|')
        # Убираем лишние пробелы и добавляем в результирующий список
        processed_data.append(processed_line)
    return processed_data


def double_spaces(data):
    # Удваиваем пробелы в каждой строке
    doubled_data = []
    for row in data:
        doubled_row = [item.replace(' ', '  ') for item in row]  # Удваиваем пробелы в каждой подстроке
        doubled_data.append(doubled_row)
    return doubled_data


def save_art_to_files(art, name):
    # Создаем папку Results, если она не существует
    results_folder = 'Results'
    os.makedirs(results_folder, exist_ok=True)

    # Путь к папке с именем name
    specific_folder = os.path.join(results_folder, name)

    # Если папка уже существует, удаляем её содержимое
    if os.path.exists(specific_folder):
        shutil.rmtree(specific_folder)

    # Создаем новую папку с именем name
    os.makedirs(specific_folder)

    # Перебираем элементы art и записываем их в файлы
    for i in range(len(art[0])):
        # Создаем имя файла
        file_name = f"cyberpunked_{name}_{i + 1}.stendhal"
        file_path = os.path.join(specific_folder, file_name)

        # Записываем данные в файл
        with open(file_path, 'w', encoding='utf-8') as f:
            # Записываем заголовок
            f.write(f'title: cyberpunked_{name}_{i + 1}\n')
            # Записываем строку 'lines:'
            f.write('lines:\n')
            # Записываем артовые строки с префиксом '#- '
            for j in range(len(art)):
                f.write(f'#- {art[j][i]}\n')


def main():
    """Main workflow controller for generating cyberpunk-style Minecraft signs."""
    library_1 = parse_string(load_library('1-wide'))
    library_3 = parse_string(load_library('3-wide'))
    library_5 = parse_string(load_library('5-wide'))

    library_135 = [library_3, library_1, library_5]

    # while True:
    user_text = get_user_input()

    arts_135 = generate_ascii_art_combinations(user_text, library_135)

    print_ascii_arts(arts_135)
    selected_art = select_art(arts_135, start_number=1)
    print_ascii_art(selected_art)
    # while True:
    #     answer = ask_for_shift()
    #     if answer == 'left' or answer == 'right':
    #         selected_art = shift_art(selected_art, answer)
    #     else:
    #         break
    #     print_ascii_art(selected_art)

    clean_name = sanitize_filename(user_text)

    selected_art = remove_bars(selected_art)
    selected_art = double_spaces(selected_art)
    save_art_to_files(selected_art, clean_name)

    subprocess.Popen(f'explorer "{os.path.abspath(f'Results/{clean_name}')}"')
    print("Copy generated files to minecraft/config/stendhal/signs/")


if __name__ == "__main__":
    main()
