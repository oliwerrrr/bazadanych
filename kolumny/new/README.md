# Dokumentacja Projektu Testów Wydajnościowych Bazy Danych Hogwarts

Ten dokument opisuje architekturę, konfigurację i sposób użycia środowiska do testowania wydajności dwóch schematów bazy danych Oracle: wierszowego (OLTP) i kolumnowego (In-Memory).

## 1. Architektura Schematów

Projekt wykorzystuje dwa oddzielne schematy w bazie danych Oracle do porównania wydajności:

1.  **`HOGWARD` (Wierszowy/Tradycyjny):** Standardowy schemat zoptymalizowany pod kątem transakcji (OLTP). Wszystkie dane są przechowywane w tradycyjnym formacie wierszowym.
2.  **`COLUMNS_HOGWARD` (Kolumnowy/Analityczny):** Schemat wykorzystujący technologię **In-Memory Column Store** dla kluczowych tabel. Jest zoptymalizowany pod kątem zapytań analitycznych (OLAP).

## 2. Zastosowanie In-Memory Column Store (Baza Kolumnowa)

W schemacie `COLUMNS_HOGWARD` celowo wybrano konkretne tabele do załadowania do pamięci w formacie kolumnowym. Wybór ten jest podyktowany chęcią maksymalnego przyspieszenia zapytań analitycznych i raportowych, które stanowią główne obciążenie w tym projekcie.

Słowo kluczowe `INMEMORY` w pliku `02_create_columnar_structure.sql` włącza tę funkcjonalność.

### Tabele objęte optymalizacją In-Memory:

-   `GRADES`
-   `POINTS`
-   `STUDENTS`
-   `STUDENTS_SUBJECTS`
-   `SUBJECTS`

### Uzasadnienie Wyboru

Strategia polegała na zidentyfikowaniu największych tabel oraz tych, które są najczęściej wykorzystywane w złożonych operacjach, takich jak agregacje i złączenia (JOIN).

1.  **`GRADES` i `POINTS` (Tabele Faktów):**
    -   **Charakterystyka:** Są to bezsprzecznie największe tabele w systemie, przechowujące miliony rekordów (każda ocena i każdy przyznany punkt).
    -   **Powód:** Zapytania analityczne, takie jak "oblicz średnią ocen dla domu" czy "znajdź najlepiej punktujących uczniów w danym miesiącu", wymagają przeskanowania i zagregowania ogromnych ilości danych z tych tabel. Magazyn kolumnowy jest tu idealny, ponieważ pozwala na odczytanie z pamięci tylko tych kolumn, które są potrzebne do obliczeń (np. `value`, `student_id`), zamiast całych wierszy, co dramatycznie redukuje ilość operacji I/O i przyspiesza działanie.

2.  **`STUDENTS` (Kluczowa Tabela Wymiarów):**
    -   **Charakterystyka:** Jest to centralna tabela, łącząca się z niemal każdą inną (punkty, oceny, domy, przedmioty). Jest często i gęsto filtrowana (np. po roku, po domu).
    -   **Powód:** Umieszczenie jej w pamięci radykalnie przyspiesza operacje filtrowania i złączeń z wielkimi tabelami `GRADES` i `POINTS`. Dzięki temu całe zapytania wykonują się szybciej.

3.  **`STUDENTS_SUBJECTS` i `SUBJECTS` (Wsparcie dla Złączeń):**
    -   **Charakterystyka:** `STUDENTS_SUBJECTS` to tabela łącząca (many-to-many) pomiędzy uczniami a przedmiotami. `SUBJECTS` to słownik przedmiotów.
    -   **Powód:** Przyspieszenie operacji złączeń jest jednym z kluczowych atutów In-Memory Column Store. Umieszczenie tych tabel w pamięci sprawia, że skomplikowane złączenia (`STUDENTS` -> `STUDENTS_SUBJECTS` -> `SUBJECTS` -> `GRADES`) są wykonywane znacznie wydajniej.

### Tabele Pominięte

-   `TEACHERS`, `HOUSES`, `DORMITORIES`, `QUIDDITCH_TEAM_MEMBERS`, `GRADES_ENUM`
-   **Powód:** Są to relatywnie małe tabele pomocnicze (tzw. "małe tabele wymiarów"). Korzyść z umieszczenia ich w pamięci In-Memory byłaby nieproporcjonalnie mała w stosunku do zużycia cennej pamięci RAM. Tradycyjny, wierszowy bufor bazy danych Oracle doskonale radzi sobie z obsługą tak małych tabel, więc nie stanowią one wąskiego gardła wydajności. 