import argparse
import re
import yaml
import sys

def remove_comments(text):
    """Удаляет многострочные комментарии из текста."""
    text = re.sub(r'\{\{!--.*?\--\}\}', '', text, flags=re.DOTALL)
    return text.strip()

def parse_arrays(text):
    """Обрабатывает массивы и возвращает их в виде словаря."""
    pattern = r'\[(.*?)\]'
    arrays = {}
    for match in re.finditer(pattern, text):
        values = [v.strip() for v in match.group(1).split(';')]
        array_name = f'array_{len(arrays)}'
        arrays[array_name] = values
        text = text.replace(match.group(0), array_name)
    return arrays, text

def parse_constants(text):
    """Обрабатывает объявления констант и возвращает их в виде словаря."""
    pattern = r'def\s+([_a-zA-Z]+)\s*=\s*(\d+|@"[^"]*")'
    constants = {}
    
    for match in re.finditer(pattern, text):
        name, value = match.groups()
        constants[name] = value.strip()
    
    return constants

def evaluate_expressions(text, constants):
    """Заменяет выражения вида $(имя) на значения констант."""
    pattern = r'\$\(([_a-zA-Z]+)\)'
    
    def replace_constant(match):
        const_name = match.group(1)
        return constants.get(const_name, f'${{{const_name}}}')  # Возвращаем оригинал, если не найдено

    return re.sub(pattern, replace_constant, text)

def transform_input_to_yaml(input_text):
    """Обрабатывает входной текст и возвращает результат в формате YAML."""
    text = remove_comments(input_text)
    
    # Сначала обрабатываем константы
    constants = parse_constants(text)
    
    # Затем обрабатываем массивы
    arrays, text = parse_arrays(text)
    
    # Вычисляем значения констант в тексте
    text = evaluate_expressions(text, constants)

    # Создаем выходной словарь для YAML
    output_data = {
        'arrays': arrays,
        'constants': constants,
    }

    # Заменяем значения в массивах на вычисленные значения
    for array_name in arrays.keys():
        arrays[array_name] = [evaluate_expressions(value, constants) for value in arrays[array_name]]

    return yaml.dump(output_data)

if __name__ == '__main__':
    # Чтение из стандартного ввода
    input_text = sys.stdin.read()
    
    # Преобразование текста в YAML
    output_yaml = transform_input_to_yaml(input_text)
    
    # Вывод результата в стандартный вывод
    print(output_yaml)
