class Controller:
    """Сквозной сценарий: ввод -> БД или вычисление -> отправка результата -> возврат."""

    def __init__(self, validator, database, user_interface, external_service):
        self._validator = validator
        self._database = database
        self._user_interface = user_interface
        self._external_service = external_service

    def run(self):
        login, password, password_confirm = self._user_interface.get_user_data()

        record = self._database.get_record(login, password, password_confirm)
        if record is None:
            result, message = self._validator.validate(login, password, password_confirm)
            self._database.add_record(login, password, password_confirm, result, message)
        else:
            result, message = record["auth_result"], record["error_message"]

        self._external_service.send(self._format_result(result, message))
        return result, message

    @staticmethod
    def _format_result(result, message):
        return f"Результат: {result}; сообщение: {message or 'нет ошибок'}"
