from collections import UserDict
from datetime import datetime, timedelta
import re

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date. Ensure the date is valid and in DD.MM.YYYY format")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone number not found")

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            new_phone_obj = Phone(new_phone)
            self.phones.remove(phone_obj)
            self.phones.append(new_phone_obj)
        else:
            raise ValueError("Old phone number not found")

    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        birthday = self.birthday.value if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if not record.birthday:
                continue
            bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            bday_this_year = bday.replace(year=today.year)
            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)
            days_until = (bday_this_year - today).days
            if 0 <= days_until <= 7:
                congratulation_date = bday_this_year
                if congratulation_date.weekday() >= 5:  # Saturday (5) or Sunday (6)
                    days_to_monday = 7 - congratulation_date.weekday()
                    congratulation_date += timedelta(days=days_to_monday)
                upcoming.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y")
                })
        return upcoming

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


# Декоратор для обробки помилок введення
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "This contact does not exist."
        except ValueError as e:
            return str(e) if str(e) else "Invalid input. Check arguments."
        except IndexError:
            return "Not enough arguments. Try again."
    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.strip().lower(), args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    raise KeyError


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return "; ".join(p.value for p in record.phones) if record.phones else "No phones"
    raise KeyError


@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts saved."
    return str(book)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    raise KeyError


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return record.birthday.value if record.birthday else "No birthday set"
    raise KeyError


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input:
            print("Empty input. Please try again.")
            continue
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()



    