import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import src.main as app
from src.controller import Controller
from src.database import RegistrationDatabase
from src.external_service import EmailService, ExternalService
from src.registration_validator import RegistrationValidator
from src.user_interface import ConsoleUserInterface, UserInterface

LOGIN = "john_doe"
PASSWORD = "Пароль1!"
KEY = (LOGIN, PASSWORD, PASSWORD)


class TestAbstractInterfaces(unittest.TestCase):
    def test_user_interface_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            UserInterface()

    def test_external_service_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            ExternalService()


class TestConsoleUserInterface(unittest.TestCase):
    def test_get_user_data_reads_three_values_from_input(self):
        with patch("builtins.input", side_effect=[LOGIN, PASSWORD, "подтверждение"]) as fake_input:
            data = ConsoleUserInterface().get_user_data()
        self.assertEqual(data, (LOGIN, PASSWORD, "подтверждение"))
        self.assertEqual(fake_input.call_count, 3)


class TestEmailService(unittest.TestCase):
    def test_send_only_simulates_and_reports_success(self):
        with self.assertLogs(level="INFO") as logs:
            self.assertTrue(EmailService().send("тестовое сообщение"))
        self.assertIn("тестовое сообщение", "\n".join(logs.output))


class TestRegistrationDatabase(unittest.TestCase):
    def setUp(self):
        self.db = RegistrationDatabase(":memory:")

    def tearDown(self):
        self.db.close()

    def test_added_record_can_be_read_back(self):
        self.db.add_record(*KEY, False, "Ошибка")
        self.assertEqual(
            self.db.get_record(*KEY),
            {"login": LOGIN, "password": PASSWORD, "password_confirm": PASSWORD,
             "auth_result": False, "error_message": "Ошибка"},
        )

    def test_missing_record_returns_none(self):
        self.assertIsNone(self.db.get_record(*KEY))

    def test_record_is_identified_by_all_three_fields(self):
        self.db.add_record(*KEY, True)
        self.assertIsNone(self.db.get_record(LOGIN, PASSWORD, "другое подтверждение"))

    def test_adding_same_key_twice_keeps_single_updated_record(self):
        self.db.add_record(*KEY, False, "старая ошибка")
        self.db.add_record(*KEY, True)
        record = self.db.get_record(*KEY)
        self.assertTrue(record["auth_result"])
        self.assertEqual(record["error_message"], "")

    def test_delete_removes_existing_record(self):
        self.db.add_record(*KEY, True)
        self.assertTrue(self.db.delete_record(*KEY))
        self.assertIsNone(self.db.get_record(*KEY))

    def test_delete_of_missing_record_returns_false(self):
        self.assertFalse(self.db.delete_record(*KEY))


class TestRegistrationValidator(unittest.TestCase):
    def test_validate_delegates_to_registration_function(self):
        with patch("src.registration_validator.registration", return_value=(True, "")) as fake:
            self.assertEqual(RegistrationValidator().validate(*KEY), (True, ""))
        fake.assert_called_once_with(*KEY)


class TestControllerWithMocks(unittest.TestCase):
    """Модульные тесты: все четыре зависимости заменены заглушками."""

    def setUp(self):
        self.validator = Mock(spec=RegistrationValidator)
        self.database = Mock(spec=RegistrationDatabase)
        self.ui = Mock(spec=UserInterface)
        self.service = Mock(spec=ExternalService)
        self.ui.get_user_data.return_value = KEY
        self.controller = Controller(self.validator, self.database, self.ui, self.service)

    def test_unknown_data_is_validated_saved_and_sent(self):
        self.database.get_record.return_value = None
        self.validator.validate.return_value = (False, "Ошибка")

        result = self.controller.run()

        self.assertEqual(result, (False, "Ошибка"))
        self.validator.validate.assert_called_once_with(*KEY)
        self.database.add_record.assert_called_once_with(*KEY, False, "Ошибка")
        self.service.send.assert_called_once_with("Результат: False; сообщение: Ошибка")

    def test_known_data_is_taken_from_database_without_validation(self):
        self.database.get_record.return_value = {"auth_result": True, "error_message": ""}

        result = self.controller.run()

        self.assertEqual(result, (True, ""))
        self.validator.validate.assert_not_called()
        self.database.add_record.assert_not_called()
        self.service.send.assert_called_once_with("Результат: True; сообщение: нет ошибок")


class TestControllerIntegration(unittest.TestCase):
    """Интеграционные тесты: реальные валидатор и SQLite (в памяти);
    заглушки только для ввода пользователя и внешнего сервера."""

    def setUp(self):
        self.db = RegistrationDatabase(":memory:")
        self.service = Mock(spec=ExternalService)
        self.validator = RegistrationValidator()
        self.controller = Controller(self.validator, self.db, ConsoleUserInterface(), self.service)

    def tearDown(self):
        self.db.close()

    def test_new_valid_registration_goes_through_all_layers(self):
        with patch("builtins.input", side_effect=[LOGIN, PASSWORD, PASSWORD]):
            result = self.controller.run()

        self.assertEqual(result, (True, ""))
        self.assertTrue(self.db.get_record(*KEY)["auth_result"])
        self.service.send.assert_called_once_with("Результат: True; сообщение: нет ошибок")

    def test_rejected_registration_is_stored_with_error_message(self):
        with patch("builtins.input", side_effect=[LOGIN, PASSWORD, "Пароль1?"]):
            result, message = self.controller.run()

        self.assertFalse(result)
        record = self.db.get_record(LOGIN, PASSWORD, "Пароль1?")
        self.assertFalse(record["auth_result"])
        self.assertEqual(record["error_message"], message)
        self.assertIn(message, self.service.send.call_args.args[0])

    def test_repeated_request_is_answered_from_database(self):
        answers = [LOGIN, PASSWORD, PASSWORD] * 2
        with patch("builtins.input", side_effect=answers), \
                patch.object(self.validator, "validate", wraps=self.validator.validate) as spy:
            first = self.controller.run()
            second = self.controller.run()

        self.assertEqual(first, second)
        self.assertEqual(spy.call_count, 1)
        self.assertEqual(self.service.send.call_count, 2)

    def test_different_data_are_validated_independently(self):
        answers = [LOGIN, PASSWORD, PASSWORD, "", PASSWORD, PASSWORD]
        with patch("builtins.input", side_effect=answers):
            good = self.controller.run()
            bad = self.controller.run()

        self.assertTrue(good[0])
        self.assertFalse(bad[0])
        self.assertFalse(self.db.get_record("", PASSWORD, PASSWORD)["auth_result"])
        self.assertEqual(self.service.send.call_count, 2)


class TestMainEntryPoint(unittest.TestCase):
    def test_main_runs_whole_scenario_with_patched_input(self):
        with patch("builtins.input", side_effect=[LOGIN, PASSWORD, PASSWORD]), \
                patch("builtins.print") as fake_print:
            result = app.main(":memory:")

        self.assertTrue(result)
        fake_print.assert_any_call("Результат:", True)


if __name__ == "__main__":
    unittest.main()
