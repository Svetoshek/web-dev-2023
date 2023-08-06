'''Модуль предназначен для выполнения проверки номера телефона на соответствие заданным форматам'''

# Импортирование модуля для работы с регулярными выражениями
import re


def checking_phone_number_for_available_format(tel):
    '''Функция для проверки телефонных номеров на соответствие доступным форматам
    В задании лабораторной работы №2 установлены следующие допустимые форматы
    * +7 (123) 456-75-90
    * 8(123)4567590
    * 123.456.75.90'''

    # Список допустимых форматов
    available_phone_number_format = [
        # Для номеров в формате `+7 (123) 456-75-90`
        r'\+\d{1}\s{1}\(\d{3}\)\s{1}\d{3}-\d{2}-\d{2}',
        # Для номеров в формате `8(123)4567590`
        r'\d?\(\d{3}\)\d{7}',
        # Для номеров в формате `123.456.75.90`
        r'\d{3}\.\d{3}\.\d{2}\.\d{2}',
    ]

    for mask in available_phone_number_format:
        result_search = re.search(mask, tel)
        '''Осуществляется проверка на: существование сопадения, 
        совпадение длины введенного номера и длины совпашей подстроки,
        т.к. подстрока должна быть равна номеру'''
        if result_search and len(result_search.group()) == len(tel):
            return result_search.group()

    return False


# лучше error_message
def why_error_occurred(tel):
    '''Функция, выводящая причину ошибки'''
    count_digit = 0
    available_symbols = ' ()-.+'
    for symbol in tel:
        if symbol.isdigit():
            count_digit += 1
        else:
            if symbol not in available_symbols:
                return "Недопустимый ввод. В номере телефона встречаются недопустимые символы."

    if tel[0:2] == '+7' or tel[0] == '8':
        if count_digit != 11:
            return "Недопустимый ввод. Неверное количество цифр."
    else:
        if (count_digit != 10):
            return "Недопустимый ввод. Неверное количество цифр."

    return False


# лучше format_number, а остальное вынести в описание
def converting_phone_number_into_single_format(tel):
    '''Функция для преобразования телефонного номера в единый формат
    Важно! Разрешенные форматы номеров представлены 
    в описании к функции checking_phone_number_for_available_format()'''
    digits = []
    text_error = 'ERROR! Произошла ошибка во время преобразования '
    'номера телефона в единый формат'
    for symbol in tel:
        if symbol.isdigit():
            digits.append(symbol)
    # Для номеров, не содержащих `+7` или `8
    if len(digits) == 10:
        d = digits
        return f'8-{d[0]}{d[1]}{d[2]}-{d[3]}{d[4]}{d[5]}-{d[6]}{d[7]}-{d[8]}{d[9]}'
    # Для номеров, начинающихся с `+7` или `8`
    elif len(digits) == 11:
        if tel[0:2] == '+7' or tel[0] == '8':
            d = digits[1:]
            return f'8-{d[0]}{d[1]}{d[2]}-{d[3]}{d[4]}{d[5]}-{d[6]}{d[7]}-{d[8]}{d[9]}'
        else:
            print(text_error)
            return False
    else:
        print(text_error)
        return False


def check_number(tel):
    '''Функция проверяющая номер телефона
    Возвращает словарь, содержащий:
    * result - результат_проверки;
    * message - возвращаемое_значение_проверки'''
    result = checking_phone_number_for_available_format(tel)
    if result:
        return {'result': True,
                'message': converting_phone_number_into_single_format(result)}
    else:
        return {'result': False,
                'message': why_error_occurred(tel)}


if __name__ == '__main__':
    # Список номеров необходимых для автоматической проверки
    tel_numbers_for_check = [
        # Номера приведенные в лабораторной работе №2 в качестве допустимых
        '+7 (123) 456-75-90',
        '8(123)4567590',
        '123.456.75.90',
        # Возможные неверные форматы номеров
        '+7 (***) 456-75-90',
        '+7(4555)345-34-345',
        '8(***)4567590',
        '8(8123)4567590',
        '123.456.75*90',
        '123.456.75.900',
        # Пример другой ошибки
        '+72345675900',
    ]

    text_error = '\033[31m{text}\033[0m'
    for tel in tel_numbers_for_check:
        print('\nВыполняется проверка для номера телефона: ', tel)
        result_check = check_number(tel)
        if (result_check['result']):
            print('\033[32mall right for', result_check['message'], '\033[0m')
        else:
            if result_check['message']:
                print(text_error.format(text=result_check['message']))
