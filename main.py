import os
import glob
import shutil
import subprocess


def load_library():
    libraries_folder = 'Libraries/'

    libraries = glob.glob(os.path.join(libraries_folder, '*.txt'))

    combined_library = ''

    for file_path in libraries:
        with open(file_path, 'r', encoding='utf-8') as file:
            combined_library += file.read() + '\n'

    return combined_library


def parse_string(input_str):
    def is_key_line(line):
        stripped = line.strip()
        return stripped == '|' or stripped.count('|') < 2

    def parse_key(line):
        stripped = line.strip()
        if stripped == '|':
            return ('|',)
        parts = stripped.split()
        return tuple(parts) if parts else (' ',)

    def process_data_line(line, current_data):
        elements = [elem for elem in line.split('|')[1:-1]]
        if elements:
            current_data.append(elements)

    def transpose_matrix(data):
        if not data:
            return []
        max_cols = max(len(row) for row in data)
        return [
            [row[col] for row in data if col < len(row)]
            for col in range(max_cols)
        ]

    def save_data_to_result(data, key, result):
        transposed = transpose_matrix(data)
        # Spaces need to be doubled to align squares in minecraft
        transposed = [[element.replace(' ', '  ') for element in row] for row in transposed]
        for key_part in key:
            result[key_part] = transposed

    lines = input_str.strip().split('\n')
    result = {}
    current_key = None
    current_data = []

    for line in lines:
        if is_key_line(line):
            if current_key is not None:
                save_data_to_result(current_data, current_key, result)
                current_data = []
            current_key = parse_key(line)
        else:
            process_data_line(line, current_data)

    if current_key is not None:
        save_data_to_result(current_data, current_key, result)

    return result


def get_text(prompt="Enter Text for cyberpunking: "):
    user_input = input(prompt)
    return user_input


def divide_string(string):
    # Удаляем пробелы в начале и конце строки
    string = string.strip()

    # Разбиваем строку на блоки по 3 символа
    blocks = [string[i:i + 3] for i in range(0, len(string), 3)]

    # Проверяем длину последнего блока
    if len(blocks[-1]) != 3:
        # Дополняем последний блок пробелами до 3 символов
        blocks[-1] = blocks[-1].ljust(3)
        print("The name isn't evenly divided into signs, but I'll continue.")
        print(blocks)
    return blocks


def create_folder(name):
    results_dir = 'Results'
    folder_path = os.path.join(results_dir, name)

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    if os.path.exists(folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    else:
        os.makedirs(folder_path)
    return name


def create_files(array, folder, library, short_name):
    results_dir = 'Results'
    folder_path = os.path.join(results_dir, folder)

    # Убедимся, что папка существует
    os.makedirs(folder_path, exist_ok=True)

    for index, text in enumerate(array, start=1):  # Начинаем счетчик с 1
        tagged_text = f"cyberpunked_{short_name}_{index}"

        # Определяем путь к файлу
        file_path = os.path.join(folder_path, f"{tagged_text}.stendhal")

        # Форматируем содержимое файла
        file_content = (f"title: {tagged_text}\n"
                        f"lines:\n" +
                        "#- " + library[text[0]][0][0] + '  ' + library[text[1]][0][0] + '  ' +
                        library[text[2]][0][0] + "\n" +
                        "#- " + library[text[0]][0][1] + '  ' + library[text[1]][0][1] + '  ' +
                        library[text[2]][0][1] + "\n" +
                        "#- " + library[text[0]][0][2] + '  ' + library[text[1]][0][2] + '  ' +
                        library[text[2]][0][2] + "\n" +
                        "#- " + library[text[0]][0][3] + '  ' + library[text[1]][0][3] + '  ' +
                        library[text[2]][0][3] + "\n")

        # Записываем содержимое в файл
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(file_content)


def open_explorer_in_folder(folder):
    # Определяем полный путь к папке
    folder_path = os.path.abspath(folder)

    # Открываем проводник Windows в указанной папке
    subprocess.Popen(f'explorer "{folder_path}"')


def main():
    library = load_library()
    library = parse_string(library)

    while True:
        user_input = ''
        while user_input == '':
            user_input = get_text()
        stripped_user_input = user_input[:15]
        user_input = divide_string(user_input)

        folder_name = create_folder(stripped_user_input)
        create_files(user_input, folder_name, library, stripped_user_input)

        open_explorer_in_folder(f'Results/{stripped_user_input}')

        print("Now copy all the files in the opened window and paste into minecraft/config/stendhal/signs/.")


if __name__ == "__main__":
    main()
