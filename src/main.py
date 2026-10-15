from src.controller import Controller
from src.database import RegistrationDatabase
from src.external_service import EmailService
from registration_validator import RegistrationValidator
from user_interface import ConsoleUserInterface


def main(db_path="registration.db"):
    database = RegistrationDatabase(db_path)
    try:
        controller = Controller(
            RegistrationValidator(), database, ConsoleUserInterface(), EmailService()
        )
        result, message = controller.run()
    finally:
        database.close()
    print("Результат:", result)
    print("Сообщение:", message)
    return result


if __name__ == "__main__":  # pragma: no cover
    main()
