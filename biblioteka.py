class Book:
    def __init__(self, title, author, total_copies):
        self.__title = title
        self.__author = author
        self.__total_copies = total_copies
        self.__available_copies = total_copies
        self.__reservations = []

    @property
    def title(self):
        return self.__title

    @property
    def author(self):
        return self.__author

    @property
    def total_copies(self):
        return self.__total_copies

    @property
    def available_copies(self):
        return self.__available_copies

    @property
    def borrowed_count(self):
        return self.__total_copies - self.__available_copies

    @property
    def reservations(self):
        return list(self.__reservations)

    def borrow_copy(self):
        if self.__available_copies <= 0:
            return False

        self.__available_copies -= 1
        return True

    def return_copy(self):
        if self.__available_copies < self.__total_copies:
            self.__available_copies += 1
            return True
        return False

    def reserve_for(self, reader):
        if self.__available_copies > 0:
            return False, "Ta ksiazka jest dostepna, nie trzeba jej rezerwowac."

        if reader.login in self.__reservations:
            return False, "Masz juz rezerwacje na ten tytul."

        self.__reservations.append(reader.login)
        return True, "Dodano rezerwacje."

    def has_reservation(self):
        return len(self.__reservations) > 0

    def __str__(self):
        reservation_info = ""
        if self.has_reservation():
            reservation_info = f", rezerwacje: {len(self.__reservations)}"

        return (
            f"{self.__title} - {self.__author} "
            f"(dostepne: {self.__available_copies}/{self.__total_copies}"
            f"{reservation_info})"
        )


class User:
    def __init__(self, login, password, role):
        self._login = login
        self.__password = password
        self._role = role

    @property
    def login(self):
        return self._login

    @property
    def role(self):
        return self._role

    def check_password(self, password):
        return self.__password == password

    def __str__(self):
        return f"{self._login} ({self._role})"


class Reader(User):
    def __init__(self, login, password):
        super().__init__(login, password, "czytelnik")
        self.__borrowed_books = []
        self.__extension_requests = []

    @property
    def borrowed_books(self):
        return list(self.__borrowed_books)

    @property
    def extension_requests(self):
        return list(self.__extension_requests)

    def add_borrowed_book(self, book):
        self.__borrowed_books.append(book)

    def has_borrowed_book(self, book):
        return book in self.__borrowed_books

    def add_extension_request(self, book):
        self.__extension_requests.append(book)


class Librarian(User):
    def __init__(self, login, password):
        super().__init__(login, password, "bibliotekarz")


class Library:
    def __init__(self, books, users):
        self.__books = books
        self.__users = users
        self.__extension_requests = []

    @property
    def books(self):
        return list(self.__books)

    @property
    def users(self):
        return list(self.__users)

    @property
    def extension_requests(self):
        return list(self.__extension_requests)

    def authenticate(self, login, password):
        matching_users = list(
            filter(lambda user: user.login == login and user.check_password(password), self.__users)
        )
        if len(matching_users) == 0:
            return None
        return matching_users[0]

    def find_book_by_title(self, title):
        normalized_title = title.lower().strip()
        matching_books = list(
            filter(lambda book: book.title.lower() == normalized_title, self.__books)
        )
        if len(matching_books) == 0:
            return None
        return matching_books[0]

    # Funkcja wyzszego rzedu: przyjmuje predykat, czyli inna funkcje.
    def filter_books(self, predicate):
        return list(filter(predicate, self.__books))

    def search_books(self, phrase):
        normalized_phrase = phrase.lower().strip()
        return self.filter_books(
            lambda book: normalized_phrase in book.title.lower()
            or normalized_phrase in book.author.lower()
        )

    def available_books(self):
        return self.filter_books(lambda book: book.available_copies > 0)

    def sort_books(self, option):
        sort_keys = {
            "1": lambda book: book.title.lower(),
            "2": lambda book: book.author.lower(),
            "3": lambda book: book.available_copies,
        }
        key_function = sort_keys.get(option)

        if key_function is None:
            return None

        reverse = option == "3"
        return sorted(self.__books, key=key_function, reverse=reverse)

    def borrow_book(self, reader, title):
        book = self.find_book_by_title(title)
        if book is None:
            return False, "Nie znaleziono ksiazki o podanym tytule."

        if not book.borrow_copy():
            return False, "Brak dostepnych sztuk. Mozesz zarezerwowac ten tytul."

        reader.add_borrowed_book(book)
        return True, f"Wypozyczono: {book.title}"

    def reserve_book(self, reader, title):
        book = self.find_book_by_title(title)
        if book is None:
            return False, "Nie znaleziono ksiazki o podanym tytule."

        return book.reserve_for(reader)

    def create_extension_request(self, reader, title):
        book = self.find_book_by_title(title)
        if book is None:
            return False, "Nie znaleziono ksiazki o podanym tytule."

        if not reader.has_borrowed_book(book):
            return False, "Nie masz wypozyczonej tej ksiazki."

        already_requested = any(
            request["reader"] == reader and request["book"] == book and request["status"] == "oczekuje"
            for request in self.__extension_requests
        )
        if already_requested:
            return False, "Prosba o przedluzenie tego tytulu juz oczekuje."

        request = {"reader": reader, "book": book, "status": "oczekuje"}
        self.__extension_requests.append(request)
        reader.add_extension_request(book)
        return True, "Wyslano prosbe o przedluzenie."

    def pending_extension_requests(self):
        return list(
            filter(lambda request: request["status"] == "oczekuje", self.__extension_requests)
        )

    def resolve_extension_request(self, request_number, decision):
        pending_requests = self.pending_extension_requests()

        if request_number < 1 or request_number > len(pending_requests):
            return False, "Nie ma prosby o takim numerze."

        request = pending_requests[request_number - 1]
        if decision == "a":
            request["status"] = "zaakceptowana"
            return True, "Prosba zostala zaakceptowana."

        if decision == "o":
            request["status"] = "odrzucona"
            return True, "Prosba zostala odrzucona."

        return False, "Niepoprawna decyzja."

    def all_borrowings(self):
        readers = list(filter(lambda user: isinstance(user, Reader), self.__users))
        return [
            {"reader": reader.login, "book": book}
            for reader in readers
            for book in reader.borrowed_books
        ]

    def library_statistics(self):
        readers = list(filter(lambda user: isinstance(user, Reader), self.__users))
        sorted_readers = sorted(
            readers,
            key=lambda reader: len(reader.borrowed_books),
            reverse=True,
        )
        reader_stats = list(
            map(lambda reader: (reader.login, len(reader.borrowed_books)), sorted_readers)
        )
        active_borrowings = sum(map(lambda reader: len(reader.borrowed_books), readers))
        books_with_borrowings = list(filter(lambda book: book.borrowed_count > 0, self.__books))
        most_popular_book = None

        if len(books_with_borrowings) > 0:
            most_popular_book = max(books_with_borrowings, key=lambda book: book.borrowed_count)

        reservations_by_title = {
            book.title: book.reservations
            for book in self.__books
            if book.has_reservation()
        }

        return {
            "most_popular_book": most_popular_book,
            "active_borrowings": active_borrowings,
            "reader_stats": reader_stats,
            "reservations_by_title": reservations_by_title,
        }


def print_books(books):
    if len(books) == 0:
        print("Brak ksiazek do wyswietlenia.")
        return

    for index, book in enumerate(books, start=1):
        print(f"{index}. {book}")


def print_borrowings(borrowings):
    if len(borrowings) == 0:
        print("Brak aktywnych wypozyczen.")
        return

    for index, borrowing in enumerate(borrowings, start=1):
        print(f"{index}. {borrowing['book'].title} - czytelnik: {borrowing['reader']}")


def login_user(library):
    attempts_left = 3

    while attempts_left > 0:
        print("\nLOGOWANIE")
        login = input("Login: ").strip()
        password = input("Haslo: ").strip()

        user = library.authenticate(login, password)
        if user is not None:
            print(f"Zalogowano jako {user}")
            return user

        attempts_left -= 1
        print(f"Niepoprawny login lub haslo. Pozostalo prob: {attempts_left}")

    print("Przekroczono limit prob logowania.")
    return None


def show_catalog(library):
    print("\nKATALOG")
    print_books(library.books)


def filter_catalog(library):
    print("\nFILTROWANIE KATALOGU")
    print("1. Szukaj frazy w tytule lub autorze")
    print("2. Pokaz tylko dostepne ksiazki")
    option = input("Wybierz opcje: ").strip()

    if option == "1":
        phrase = input("Podaj fraze: ")
        print_books(library.search_books(phrase))
        return

    if option == "2":
        print_books(library.available_books())
        return

    print("Niepoprawna opcja filtrowania.")


def sort_catalog(library):
    print("\nSORTOWANIE KATALOGU")
    print("1. Wedlug tytulu")
    print("2. Wedlug autora")
    print("3. Wedlug liczby dostepnych sztuk")
    option = input("Wybierz opcje: ").strip()

    sorted_books = library.sort_books(option)
    if sorted_books is None:
        print("Niepoprawna opcja sortowania.")
        return

    print_books(sorted_books)


def borrow_book_menu(library, reader):
    title = input("Podaj tytul ksiazki do wypozyczenia: ")
    success, message = library.borrow_book(reader, title)
    print(message)

    if not success and "Mozesz zarezerwowac" in message:
        decision = input("Czy chcesz zarezerwowac ten tytul? (t/n): ").strip().lower()
        if decision == "t":
            reserve_success, reserve_message = library.reserve_book(reader, title)
            print(reserve_message)


def reserve_book_menu(library, reader):
    title = input("Podaj tytul niedostepnej ksiazki do rezerwacji: ")
    success, message = library.reserve_book(reader, title)
    print(message)


def show_reader_borrowed_books(reader):
    print("\nMOJE WYPOZYCZENIA")
    print_books(reader.borrowed_books)


def request_extension_menu(library, reader):
    if len(reader.borrowed_books) == 0:
        print("Nie masz wypozyczonych ksiazek.")
        return

    show_reader_borrowed_books(reader)
    title = input("Podaj tytul ksiazki do przedluzenia: ")
    success, message = library.create_extension_request(reader, title)
    print(message)


def show_librarian_borrowings(library):
    print("\nAKTYWNE WYPOZYCZENIA")
    print_borrowings(library.all_borrowings())


def handle_extension_requests(library):
    pending_requests = library.pending_extension_requests()

    if len(pending_requests) == 0:
        print("Brak oczekujacych prosb o przedluzenie.")
        return

    print("\nPROSBY O PRZEDLUZENIE")
    for index, request in enumerate(pending_requests, start=1):
        book = request["book"]
        reader = request["reader"]
        reservation_info = "tak" if book.has_reservation() else "nie"
        reserved_by = ", ".join(book.reservations) if book.has_reservation() else "-"
        print(
            f"{index}. {reader.login} prosi o przedluzenie: {book.title} "
            f"| rezerwacja: {reservation_info} | rezerwujacy: {reserved_by}"
        )

    try:
        request_number = int(input("Numer prosby do obslugi: "))
    except ValueError:
        print("Numer musi byc liczba.")
        return

    decision = input("Akceptuj czy odrzuc? (a/o): ").strip().lower()
    success, message = library.resolve_extension_request(request_number, decision)
    print(message)


def show_librarian_statistics(library):
    stats = library.library_statistics()

    print("\nSTATYSTYKI BIBLIOTEKARZA")
    most_popular_book = stats["most_popular_book"]
    if most_popular_book is None:
        print("Najpopularniejsza ksiazka: brak wypozyczen.")
    else:
        print(
            "Najpopularniejsza ksiazka: "
            f"{most_popular_book.title} ({most_popular_book.borrowed_count} wypozyczen)"
        )

    print(f"Liczba aktywnych wypozyczen ogolem: {stats['active_borrowings']}")

    print("\nCzytelnicy wg liczby wypozyczonych ksiazek:")
    for index, (login, borrowed_count) in enumerate(stats["reader_stats"], start=1):
        print(f"{index}. {login}: {borrowed_count}")

    print("\nRezerwacje wg tytulu:")
    if len(stats["reservations_by_title"]) == 0:
        print("Brak aktywnych rezerwacji.")
        return

    for title, readers in stats["reservations_by_title"].items():
        print(f"- {title}: {', '.join(readers)}")


def show_reader_menu():
    print("\nMENU CZYTELNIKA")
    print("1. Przegladaj katalog")
    print("2. Filtruj katalog")
    print("3. Sortuj katalog")
    print("4. Wypozycz ksiazke")
    print("5. Zarezerwuj niedostepna ksiazke")
    print("6. Moje wypozyczenia")
    print("7. Popros o przedluzenie")
    print("8. Wyloguj")


def show_librarian_menu():
    print("\nMENU BIBLIOTEKARZA")
    print("1. Przegladaj katalog")
    print("2. Filtruj katalog")
    print("3. Sortuj katalog")
    print("4. Lista wypozyczen")
    print("5. Obsluga prosb o przedluzenie")
    print("6. Statystyki")
    print("7. Wyloguj")


def run_reader_menu(library, reader):
    is_running = True

    while is_running:
        show_reader_menu()
        choice = input("Wybierz opcje: ").strip()

        if choice == "1":
            show_catalog(library)
        elif choice == "2":
            filter_catalog(library)
        elif choice == "3":
            sort_catalog(library)
        elif choice == "4":
            borrow_book_menu(library, reader)
        elif choice == "5":
            reserve_book_menu(library, reader)
        elif choice == "6":
            show_reader_borrowed_books(reader)
        elif choice == "7":
            request_extension_menu(library, reader)
        elif choice == "8":
            print("Wylogowano.")
            is_running = False
        else:
            print("Niepoprawny wybor.")


def run_librarian_menu(library, librarian):
    is_running = True

    while is_running:
        show_librarian_menu()
        choice = input("Wybierz opcje: ").strip()

        if choice == "1":
            show_catalog(library)
        elif choice == "2":
            filter_catalog(library)
        elif choice == "3":
            sort_catalog(library)
        elif choice == "4":
            show_librarian_borrowings(library)
        elif choice == "5":
            handle_extension_requests(library)
        elif choice == "6":
            show_librarian_statistics(library)
        elif choice == "7":
            print("Wylogowano.")
            is_running = False
        else:
            print("Niepoprawny wybor.")


def create_library():
    books = [
        Book("Lalka", "Boleslaw Prus", 3),
        Book("Pan Tadeusz", "Adam Mickiewicz", 2),
        Book("Quo Vadis", "Henryk Sienkiewicz", 1),
        Book("Ferdydurke", "Witold Gombrowicz", 2),
        Book("Solaris", "Stanislaw Lem", 1),
        Book("Dziady", "Adam Mickiewicz", 0),
    ]

    users = [
        Reader("anna", "haslo123"),
        Reader("marek", "qwerty"),
        Reader("kasia", "biblioteka"),
        Librarian("admin", "admin123"),
    ]

    return Library(books, users)


def main():
    library = create_library()
    print("SYSTEM BIBLIOTEKI - ZADANIE 3")

    user = login_user(library)
    if user is None:
        return

    if isinstance(user, Librarian):
        run_librarian_menu(library, user)
    elif isinstance(user, Reader):
        run_reader_menu(library, user)


if __name__ == "__main__":
    main()
