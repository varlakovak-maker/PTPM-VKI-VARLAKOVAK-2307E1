from abc import ABC, abstractmethod


class UserInterface(ABC):

    @abstractmethod
    def get_user_data(self):
        """Возвращает кортеж (логин, пароль, подтверждение пароля)."""

class ConsoleUserInterface(UserInterface):

    def get_user_data(self):
        login = input("Введите логин: ")
        password = input("Введите пароль: ")
        password_confirm = input("Подтвердите пароль: ")
        return login, password, password_confirm
