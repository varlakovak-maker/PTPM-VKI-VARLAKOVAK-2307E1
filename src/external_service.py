import logging
from abc import ABC, abstractmethod


class ExternalService(ABC):

    @abstractmethod
    def send(self, message):
        """Передаёт строку стороннему процессу. Возвращает True при успехе."""



class EmailService(ExternalService):
    def send(self, message):
        logging.info("[EmailService] Имитация отправки: %s", message)
        return True
