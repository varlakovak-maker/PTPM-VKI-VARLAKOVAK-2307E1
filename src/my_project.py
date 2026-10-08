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
BLACK_LIST = ["admin", "administrator", "user", "test", "support"]


def mask_password(password):
    # FIX 1: раньше каждый символ сдвигался на +1 (обратимо, пароль утекал в лог),
    # а при None падал TypeError. Теперь - только звездочки.
    if password is None:
        return ""
    return "*" * len(password)


def check_login(login):
    if not login:
        return False, "Логин не может быть пустым"
    # FIX 2: [0-9] вместо \d - иначе принимались юникодные цифры (например, арабо-индийские)
    phone_pattern = r"^\+[0-9]-[0-9]{3}-[0-9]{3}-[0-9]{4}$"
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if re.fullmatch(phone_pattern, login):
        return True, ""
    if re.fullmatch(email_pattern, login):
        return True, ""
    # FIX 3: проверка черного списка перед проверкой длины,
    # иначе "user" и "test" (4 символа) никогда не доходили до черного списка
    if login.lower() in BLACK_LIST:
        return False, "Логин находится в черном списке"
    if len(login) < 5:
        return False, "Логин должен содержать минимум 5 символов"
    if not re.fullmatch(r"[A-Za-z0-9_]+", login):
        return False, "Логин может содержать только латинские буквы, цифры и _"
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
    if not re.search(r"[0-9]", password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>/?\\|`~]", password):
        return False, "Пароль должен содержать хотя бы один специальный символ"
    return True, ""


def registration(login, password, password_confirm):
    try:
        # FIX 4: логирование перенесено внутрь try - раньше mask_password(None)
        # ронял функцию исключением вместо возврата (False, сообщение)
        logging.info(
            "Получен запрос регистрации: login=%s, password=%s, confirmation=%s",
            login,
            mask_password(password),
            mask_password(password_confirm)
        )
        valid, message = check_login(login)
        if not valid:
            # FIX 5: logging.exception вне except писал ложный traceback "NoneType: None"
            # на уровне ERROR; обычный отказ - это WARNING
            logging.warning("Регистрация отклонена: %s", message)
            return False, message
        valid, message = check_password(password)
        if not valid:
            logging.warning("Регистрация отклонена: %s", message)
            return False, message
        if not password_confirm:
            message = "Подтверждение пароля не может быть пустым"
            logging.warning("Регистрация отклонена: %s", message)
            return False, message
        if password != password_confirm:
            message = "Пароль и подтверждение пароля не совпадают"
            logging.warning("Регистрация отклонена: %s", message)
            return False, message
        logging.info("Регистрация пользователя %s успешно выполнена", login)
        return True, ""
    except Exception:
        logging.exception("Произошла ошибка при регистрации")
        return False, "Произошла внутренняя ошибка"


def main():
    logging.info("Приложение запущено")
    print("Регистрация пользователя")
    login = input("Введите логин: ")
    password = input("Введите пароль: ")
    password_confirm = input("Подтвердите пароль: ")
    result, message = registration(login, password, password_confirm)
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
