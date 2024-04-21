"""
Программа переводит данные из csv-файла в json-файл, меняет форматирование и
преобразует данные о спортсменах из одних единиц измерения в другие.

Автор: Гашев Константин
"""

import csv
import json
import re

DELIMETER_FOR_CSV = ','
EXPECTED_AMOUNT_OF_PARAMS = 5
FLOAT_PATTERN = r'^\d+?\.\d+?$'
INDENT_FOR_JSON = 4
POUNDS_TO_KILOGRAMS = 2.2062
SANTIMETERS_TO_INCHES = 2.54


def calculate_age(age: str) -> str:
    """Округление значения возраста спортсмена до ближайшего целого числа."""
    return str(round(float(age)))


def calculate_height(height: str) -> str:
    """Перевод роста спортсмена из дюймов в сантиметры."""
    return str(round(float(height) * SANTIMETERS_TO_INCHES))


def calculate_weight(weight: str) -> str:
    """Перевод веса спортсмена из фунтов в килограммы."""
    return str(round(float(weight) // POUNDS_TO_KILOGRAMS))


def check_item_completness(data: dict) -> bool:
    """Проверка полноты данных о спортсмене перед записью в результат."""
    return len(data) == EXPECTED_AMOUNT_OF_PARAMS


def check_item_instance(key: str, value: str) -> bool:
    """Проверка всех значений на пустоту и параметров на числовой формат."""
    param_list = ['Height(inches)', 'Weight(lbs)', 'Age']
    if value is None or len(value) == 0:
        return False
    elif key in param_list:
        if not value.isdigit():
            if re.match(FLOAT_PATTERN, value) is None:
                return False
    return True


def clear_item(data: str) -> str:
    """Очистка данных о спортсменах от лишних символов при чтении csv."""
    return ''.join([letter.replace('\"', '') for letter in str(data)])


def report_to_console(
        result: list, failed_data_amount: int, failed_data: list
) -> None:
    """Создание и вывод в консоль отчета об успешном выполнении программы."""
    successful_data = len(result)
    report = (
        'Работа программы завершена в штатном режиме.\n'
        f'Количество спортсменов, добавленных в файл: {successful_data}.\n'
    )
    if failed_data_amount > 0:
        report += (
            'Количество спортсменов, не добавленных в итоговый файл, '
            f'из-за ошибок в первичных данных: {failed_data_amount}.\n'
            f'Спортсмены, данные которых не были добавлены в итоговый файл: '
            f'{", ".join(map(str, failed_data))}.\n'
        )
    else:
        report += 'Все поступившие данные успешно обработаны.\n'
    report += f'Результаты записаны в файл "{json_file_path}".'
    print(report)


def csv_to_json(csv_file_path: csv, json_file_path: json) -> None:
    """
    Основная функция, выполняющая:
    - чтение csv-файла с данными о спортсменах;
    - вызов функции проверки значений;
    - переименование столбцов для итогового json-файла;
    - вызов других функций для преобразования возраста, роста и веса;
    - вызов функции для проверки данных на комплектность;
    - запись обработанных данных в json-файл;
    - вызов функции для вывода отчета в консоль.
    """
    result = []
    failed_data_amount = 0
    failed_data = []
    with open(csv_file_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(
            csv_file,
            delimiter=DELIMETER_FOR_CSV,
            skipinitialspace=True,
            quoting=csv.QUOTE_NONE,
        )
        for row in reader:
            cleared_data = {}
            for key, value in row.items():
                new_value = clear_item(value)
                new_key = clear_item(key)
                if new_key == 'Team':
                    continue
                if not check_item_instance(new_key, new_value):
                    continue
                if new_key == 'Height(inches)':
                    new_key = 'Height'
                    new_value = calculate_height(new_value)
                elif new_key == 'Weight(lbs)':
                    new_key = 'Weight'
                    new_value = calculate_weight(new_value)
                elif new_key == 'Age':
                    new_value = calculate_age(new_value)
                cleared_data[new_key] = new_value
            if check_item_completness(cleared_data):
                result.append(cleared_data)
            else:
                failed_data_amount += 1
                failed_data.append(cleared_data.get('Name', 'Nameless man'))
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(result, indent=INDENT_FOR_JSON))
    report_to_console(result, failed_data_amount, failed_data)


if __name__ == '__main__':
    csv_file_path = 'mlb_players.csv'
    json_file_path = 'data.json'
    try:
        csv_to_json(csv_file_path, json_file_path)
    except FileNotFoundError:
        print(
            'Программа не может быть выполнена!\n'
            f'Источник данных (файл "{csv_file_path}") не обнаружен.'
        )
