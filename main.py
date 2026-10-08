import logging
import sys
import re
import os


os.makedirs("logs", exist_ok=True)

log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/file_txt.log", encoding="utf-8")
    ]
)

BLACK_LIST = [
    "admin",
    "administrator",
    "user",
    "test",
    "support"
]

def mask_password(password):
    result = ""

    for char in password:
        result += chr(ord(char)+ 1)
    return result

def check_login(login):

    if not login:
        return False, "Логин не может быть пустым"

    phone_pattern = r"^\+\d-\d{3}-\d{3}-\d{4}$"

    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if re.fullmatch(phone_pattern, login):
        return True, ""

    if re.fullmatch(email_pattern, login):
        return True, ""

    if len(login) < 5:
        return False, "Логин должен содержать минимум 5 символов"

    if not re.fullmatch(r"[A-Za-z0-9_]+", login):
        return False, "Логин может содержать только латинские буквы, цифры и _"

    if login.lower() in BLACK_LIST:
        return False, "Логин находится в черном списке"

    return True, ""


def check_password(password):

    if not password:
        return False, "Пароль не может быть пустым"

    if len(password) < 7:
        return False, "Пароль должен содержать минимум 7 символов"

    if not re.fullmatch(r"[А-Яа-яЁё0-9!@#$%^&*()_+\-=\[\]{};:'\",.<>/?\\|`~]+", password):
        return False, "Пароль содержит недопустимые символы"

    if not re.search(r"[А-ЯЁ]", password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"

    if not re.search(r"[а-яё]", password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"

    if not re.search(r"\d", password):
        return False, "Пароль должен содержать хотя бы одну цифру"

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>/?\\|`~]", password):
        return False, "Пароль должен содержать хотя бы один специальный символ"

    return True, ""


def registration(login, password, password_confirm):

    logging.info(
        "Получен запрос регистрации: login=%s, password=%s, confirmation=%s",
        login,
        mask_password(password),
        mask_password(password_confirm)
    )

    try:
        valid, message = check_login(login)

        if not valid:
            logging.exception("Регистрация отклонена: %s", message)
            return False, message

        valid, message = check_password(password)

        if not valid:
            logging.exception("Регистрация отклонена: %s", message)
            return False, message

        if not password_confirm:
            message = "Подтверждение пароля не может быть пустым"
            logging.exception("Регистрация отклонена: %s", message)
            return False, message

        if password != password_confirm:
            message = "Пароль и подтверждение пароля не совпадают"
            logging.exception("Регистрация отклонена: %s", message)
            return False, message

        logging.info("Регистрация пользователя %s успешно выполнена", login)

        return True, ""

    except Exception as ex:
        logging.exception("Произошла ошибка при регистрации")
        logging.exception(ex)

        return False, "Произошла внутренняя ошибка"


def main():
    logging.info("Приложение запущено")

    print("Регистрация пользователя")

    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    password_confirm = input("Подтвердите пароль: ")

    result, message = registration(
        login,
        password,
        password_confirm
    )

    print()

    if result:
        print("Результат: True")
        print("Сообщение: ")
    else:
        print("Результат: False")
        print("Сообщение:", message)

    logging.info("Приложение завершено")


if __name__ == "__main__":
    main()

