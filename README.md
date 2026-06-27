# Biblioteka - zadanie 3

Rozwiązanie części 3 z programowania wysokopoziomowego: rozszerzenie aplikacji bibliotecznej o elementy programowania funkcyjnego.

Projekt zawiera też poprawną bazę z części 2, czyli wersję obiektową z rolą czytelnika i bibliotekarza.

## Pliki

- `biblioteka.py` - główna aplikacja konsolowa.
- `README.md` - opis projektu i instrukcja uruchomienia.

## Uruchomienie

```bash
python biblioteka.py
```

## Dane testowe

Czytelnicy:

| Login | Hasło |
| --- | --- |
| anna | haslo123 |
| marek | qwerty |
| kasia | biblioteka |

Bibliotekarz:

| Login | Hasło |
| --- | --- |
| admin | admin123 |

## Zakres z części 2

Program zawiera:

- klasy `Book`, `User`, `Reader`, `Librarian`, `Library`,
- dziedziczenie: `Reader` i `Librarian` dziedziczą po `User`,
- hermetyzację przez pola prywatne i properties,
- metodę `__str__`,
- osobne menu dla czytelnika i bibliotekarza,
- wypożyczanie książek,
- listę wypożyczeń dla bibliotekarza,
- prośby o przedłużenie wypożyczenia i ich obsługę przez bibliotekarza.

## Zakres z części 3

Program rozszerza bibliotekę o:

- filtrowanie katalogu po frazie w tytule lub autorze,
- filtrowanie tylko dostępnych książek,
- sortowanie katalogu po tytule, autorze lub liczbie dostępnych sztuk,
- rezerwację niedostępnego tytułu,
- informację o rezerwacjach przy obsłudze próśb o przedłużenie,
- statystyki bibliotekarza,
- funkcję wyższego rzędu `filter_books`, która przyjmuje predykat filtrowania.

W nowych funkcjonalnościach użyto m.in. `lambda`, `filter`, `map`, `sorted` oraz comprehensions.

## Jak wrzucić na GitHuba

1. Wejdź do swojego repozytorium na GitHubie.
2. Utwórz nowy folder albo nową gałąź dla zadania 3.
3. Wrzuć pliki `biblioteka.py` i `README.md`.
4. Zrób commit z opisem, np. `Dodanie rozwiązania zadania 3`.
5. Do oddania wyślij link do repozytorium albo do folderu z zadaniem 3.
