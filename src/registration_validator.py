from my_project import registration


class RegistrationValidator:
    """Класс вычислений/валидации: единственный метод - проверка регистрации из ЛР1."""

    def validate(self, login, password, password_confirm):
        """Возвращает (результат: bool, сообщение_об_ошибке: str)."""
        return registration(login, password, password_confirm)