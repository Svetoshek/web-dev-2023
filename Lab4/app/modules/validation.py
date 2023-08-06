'''Модуль для валидации данных, введенных пользователем
Author: Tatarchuk Mihail
Version: 1.0.0
Date: 14.05.2023'''

# Импорт модуля для регулярных выражений
import re

# Список допустимых символов
VALID_SYMBOLS = '''~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \ | " ' . , : ;'''.split(
)


def checkLogin(login):
    '''Функция, проводящая валидацию логина
    Возвращает множество найденых ошибок'''

    error_list = set()

    if login:
        if re.search('^\d', login):
            error_list.add('Логин не может начинаться с цифры')
        if len(login) < 5:
            error_list.add("Логин должен содержать не менее 5 символов")
        for symbol in login:
            if not (re.search('[a-zA-Z]', symbol) or symbol.isdigit()):
                error_list.add("Допустимы только латинские буквы и цифры")
    elif login == None:
        error_list.add("Поле не может быть пустым")
    return error_list


def checkPassword(password):
    '''Функция, проводящая валидацию пароля
    Возвращает множество найденых ошибок'''

    error_list = set()
    if password:
        if 8 > len(password) or len(password) > 128:
            error_list.add(
                "Длина пароля должна быть не менее 8 и не более 128 символов")
        if not any(symbol.isupper() for symbol in password):
            error_list.add(
                "Пароль должен содержать минимум одну заглавную букву")
        if not any(symbol.islower() for symbol in password):
            error_list.add(
                "Пароль должен содержать минимум одну строчную букву")
        if not any(symbol.isdigit() for symbol in password):
            error_list.add("Пароль должен содержать минимум одну цифру")
        for symbol in password:
            if symbol.isalpha():
                if not( re.search('[a-яА-Я]', symbol) or
                         re.search('[a-zA-Z]', symbol)):
                    error_list.add(
                        "Пароль должен содержать только латинские или кириллические буквы")
            elif symbol.isdigit():
                if not(re.search('[0-9]', symbol)):
                    error_list.add(
                        "Пароль должен содержать только арабские цифры")
            else:
                if symbol == ' ':
                    error_list.add("Пароль не должен содержать пробелов")
                if symbol not in VALID_SYMBOLS:
                    error_list.add("Пароль содержит недопустимые символы")
    elif password == None:
        error_list.add("Поле не может быть пустым")
    return error_list


def checkLastName(last_name):
    '''Функция, проводящая валидацию фамилии
    Возвращает множество найденых ошибок'''

    error_list = set()

    if last_name:
        pass
    elif last_name == None:
        error_list.add("Поле не может быть пустым")
    return error_list


def checkFirstName(first_name):
    '''Функция, проводящая валидацию имени
    Возвращает множество найденых ошибок'''

    error_list = set()

    if first_name:
        pass
    elif first_name == None:
        error_list.add("Поле не может быть пустым")
    return error_list
