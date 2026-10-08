import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from my_project import check_login, check_password, mask_password, registration

GOOD_PASSWORD = "Пароль1!"
GOOD_LOGIN = "john_doe"


class TestCheckLogin(unittest.TestCase):
    def test_empty_login_is_rejected(self):
        self.assertEqual(check_login(""), (False, "Логин не может быть пустым"))

    def test_none_login_is_rejected(self):
        self.assertEqual(check_login(None), (False, "Логин не может быть пустым"))

    def test_valid_phone_is_accepted(self):
        self.assertEqual(check_login("+7-999-123-4567"), (True, ""))

    def test_phone_with_wrong_group_length_is_rejected(self):
        self.assertFalse(check_login("+7-99-123-4567")[0])

    def test_phone_with_unicode_digits_is_rejected(self):
        self.assertFalse(check_login("+\u0667-999-123-4567")[0])

    def test_valid_email_is_accepted(self):
        self.assertEqual(check_login("user.name+tag@example.com"), (True, ""))

    def test_email_without_domain_zone_is_rejected(self):
        self.assertFalse(check_login("user@example")[0])

    def test_latin_login_with_underscore_and_digits_is_accepted(self):
        self.assertEqual(check_login("john_doe1"), (True, ""))

    def test_login_of_4_chars_is_rejected_by_length(self):
        self.assertEqual(check_login("abcd"), (False, "Логин должен содержать минимум 5 символов"))

    def test_login_of_5_chars_is_accepted_at_boundary(self):
        self.assertEqual(check_login("abcde"), (True, ""))

    def test_cyrillic_login_is_rejected(self):
        self.assertEqual(check_login("логин123"),
                         (False, "Логин может содержать только латинские буквы, цифры и _"))

    def test_login_with_space_is_rejected(self):
        self.assertFalse(check_login("john doe")[0])

    def test_blacklisted_login_is_rejected_case_insensitively(self):
        self.assertEqual(check_login("AdMiN"), (False, "Логин находится в черном списке"))

    def test_short_blacklisted_login_gets_blacklist_message(self):
        self.assertEqual(check_login("test"), (False, "Логин находится в черном списке"))


class TestCheckPassword(unittest.TestCase):
    def test_empty_password_is_rejected(self):
        self.assertEqual(check_password(""), (False, "Пароль не может быть пустым"))

    def test_password_of_6_chars_is_rejected_by_length(self):
        self.assertEqual(check_password("Аб1!аб"),
                         (False, "Пароль должен содержать минимум 7 символов"))

    def test_password_of_7_chars_is_accepted_at_boundary(self):
        self.assertEqual(check_password("Аб1!абв"), (True, ""))

    def test_latin_letters_are_rejected_as_invalid_chars(self):
        self.assertEqual(check_password("Password1!"),
                         (False, "Пароль содержит недопустимые символы"))

    def test_password_with_space_is_rejected(self):
        self.assertEqual(check_password("Пароль 1!"),
                         (False, "Пароль содержит недопустимые символы"))

    def test_password_without_uppercase_is_rejected(self):
        self.assertEqual(check_password("пароль1!"),
                         (False, "Пароль должен содержать хотя бы одну заглавную букву"))

    def test_password_without_lowercase_is_rejected(self):
        self.assertEqual(check_password("ПАРОЛЬ1!"),
                         (False, "Пароль должен содержать хотя бы одну строчную букву"))

    def test_password_without_digit_is_rejected(self):
        self.assertEqual(check_password("Пароль!!"),
                         (False, "Пароль должен содержать хотя бы одну цифру"))

    def test_password_without_special_char_is_rejected(self):
        self.assertEqual(check_password("Пароль12"),
                         (False, "Пароль должен содержать хотя бы один специальный символ"))


class TestMaskPassword(unittest.TestCase):
    def test_mask_hides_every_character(self):
        masked = mask_password(GOOD_PASSWORD)
        self.assertEqual(len(masked), len(GOOD_PASSWORD))
        self.assertEqual(set(masked), {"*"})

    def test_mask_of_empty_string_is_empty(self):
        self.assertEqual(mask_password(""), "")


class TestRegistration(unittest.TestCase):
    def test_valid_data_registers_successfully(self):
        self.assertEqual(registration(GOOD_LOGIN, GOOD_PASSWORD, GOOD_PASSWORD), (True, ""))

    def test_invalid_login_returns_login_error(self):
        self.assertEqual(registration("", GOOD_PASSWORD, GOOD_PASSWORD),
                         (False, "Логин не может быть пустым"))

    def test_invalid_password_returns_password_error(self):
        self.assertEqual(registration(GOOD_LOGIN, "пароль1!", "пароль1!"),
                         (False, "Пароль должен содержать хотя бы одну заглавную букву"))

    def test_empty_confirmation_is_rejected(self):
        self.assertEqual(registration(GOOD_LOGIN, GOOD_PASSWORD, ""),
                         (False, "Подтверждение пароля не может быть пустым"))

    def test_mismatching_confirmation_is_rejected(self):
        self.assertEqual(registration(GOOD_LOGIN, GOOD_PASSWORD, "Пароль1?"),
                         (False, "Пароль и подтверждение пароля не совпадают"))

    def test_none_password_does_not_crash(self):
        self.assertEqual(registration(GOOD_LOGIN, None, None),
                         (False, "Пароль не может быть пустым"))

    def test_non_string_login_returns_internal_error(self):
        self.assertEqual(registration(12345, GOOD_PASSWORD, GOOD_PASSWORD),
                         (False, "Произошла внутренняя ошибка"))

    def test_rejection_is_logged_as_warning_not_error(self):
        with self.assertLogs(level="DEBUG") as cm:
            registration("", GOOD_PASSWORD, GOOD_PASSWORD)
        rejected = [r for r in cm.records if "отклонена" in r.getMessage()]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0].levelname, "WARNING")

    def test_plain_password_is_not_written_to_log(self):
        with self.assertLogs(level="DEBUG") as cm:
            registration(GOOD_LOGIN, GOOD_PASSWORD, GOOD_PASSWORD)
        shifted = "".join(chr(ord(c) + 1) for c in GOOD_PASSWORD)
        for record in cm.records:
            self.assertNotIn(GOOD_PASSWORD, record.getMessage())
            self.assertNotIn(shifted, record.getMessage())


if __name__ == "__main__":
    unittest.main()
