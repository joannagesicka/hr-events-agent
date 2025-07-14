# Instrukcja wdrożenia HR Events Agent

Ta instrukcja przeprowadzi Cię przez proces wdrożenia automatycznego agenta do aktualizacji strony z wydarzeniami HR.

## Spis treści

1. [Wymagania](#wymagania)
2. [Krok 1: Fork repozytorium](#krok-1-fork-repozytorium)
3. [Krok 2: Włączenie GitHub Pages](#krok-2-włączenie-github-pages)
4. [Krok 3: Konfiguracja GitHub Actions](#krok-3-konfiguracja-github-actions)
5. [Krok 4: Testowanie agenta](#krok-4-testowanie-agenta)
6. [Krok 5: Dostosowanie źródeł danych](#krok-5-dostosowanie-źródeł-danych)
7. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
8. [Ręczne dodawanie wydarzeń](#ręczne-dodawanie-wydarzeń)

## Wymagania

- Konto GitHub (darmowe)
- Podstawowa znajomość Git (opcjonalnie)

## Krok 1: Fork repozytorium

1. Zaloguj się na swoje konto GitHub
2. Przejdź do repozytorium HR Events Agent (link do Twojego repozytorium)
3. Kliknij przycisk "Fork" w prawym górnym rogu
4. Poczekaj na utworzenie kopii repozytorium na Twoim koncie

![Fork repozytorium](https://docs.github.com/assets/cb-23088/images/help/repository/fork_button.png)

## Krok 2: Włączenie GitHub Pages

1. Przejdź do swojej kopii repozytorium
2. Kliknij zakładkę "Settings" (Ustawienia)
3. W menu bocznym wybierz "Pages"
4. W sekcji "Source" wybierz:
   - Branch: `gh-pages`
   - Folder: `/ (root)`
5. Kliknij "Save"

![GitHub Pages](https://docs.github.com/assets/cb-47677/images/help/pages/select-gh-pages-or-master-as-source.png)

6. Po chwili zobaczysz komunikat z URL Twojej strony (format: `https://twoja-nazwa.github.io/hr-events-agent`)
7. Zapisz ten URL - to będzie stały adres Twojej strony z wydarzeniami HR

## Krok 3: Konfiguracja GitHub Actions

GitHub Actions jest już skonfigurowane w repozytorium, ale musisz upewnić się, że jest włączone:

1. Przejdź do zakładki "Actions" w Twoim repozytorium
2. Jeśli zobaczysz komunikat o wyłączonych workflow, kliknij "I understand my workflows, go ahead and enable them"
3. Powinieneś zobaczyć workflow "Update HR Events" na liście

![GitHub Actions](https://docs.github.com/assets/cb-40551/images/help/repository/actions-tab.png)

## Krok 4: Testowanie agenta

Przetestuj, czy agent działa poprawnie:

1. Przejdź do zakładki "Actions"
2. Kliknij na workflow "Update HR Events"
3. Kliknij przycisk "Run workflow" po prawej stronie
4. Potwierdź uruchomienie workflow

![Run workflow](https://docs.github.com/assets/cb-53822/images/help/repository/workflow-dispatch.png)

5. Poczekaj na zakończenie workflow (może potrwać 1-2 minuty)
6. Po zakończeniu, odwiedź URL Twojej strony GitHub Pages, aby sprawdzić czy działa

## Krok 5: Dostosowanie źródeł danych

Możesz dostosować źródła danych, z których agent zbiera informacje:

1. Przejdź do pliku `scripts/scraper.py` w Twoim repozytorium
2. Kliknij ikonę edycji (ołówek)
3. Znajdź sekcję `SOURCES` (około linii 25)
4. Dodaj lub usuń źródła według potrzeb
5. Kliknij "Commit changes" na dole strony

```python
SOURCES = [
    "https://hrlityczny.pl/wydarzenia-hr-w-2025-roku/",
    "https://www.pb.pl/konferencje/",
    # Dodaj własne źródła tutaj
]
```

## Rozwiązywanie problemów

### Problem: Workflow kończy się błędem

1. Przejdź do zakładki "Actions"
2. Kliknij na nieudany workflow
3. Sprawdź logi błędów
4. Najczęstsze problemy:
   - Błędy w skrypcie scraper.py
   - Problemy z dostępem do źródeł danych
   - Problemy z formatem danych

### Problem: Strona nie wyświetla się poprawnie

1. Sprawdź czy branch `gh-pages` został utworzony
2. Sprawdź ustawienia GitHub Pages
3. Upewnij się, że workflow zakończył się sukcesem
4. Odczekaj kilka minut - GitHub Pages może potrzebować czasu na aktualizację

## Ręczne dodawanie wydarzeń

Możesz ręcznie dodać wydarzenie bez czekania na automatyczne wykrycie:

1. Przejdź do pliku `data/events.json` w Twoim repozytorium
2. Kliknij ikonę edycji (ołówek)
3. Dodaj nowe wydarzenie do tablicy `events` według poniższego formatu:

```json
{
  "id": "unikalne-id-wydarzenia",
  "title": "Tytuł wydarzenia",
  "date": "2025-08-31",
  "location": "Warszawa",
  "category": "HR",
  "status": "Potwierdzone",
  "isNew": true,
  "description": "Opis wydarzenia...",
  "tags": ["tag1", "tag2", "tag3"],
  "pricing": "Darmowy",
  "hasDeadline": false,
  "addedDate": "2025-07-10"
}
```

4. Kliknij "Commit changes" na dole strony
5. GitHub Actions automatycznie zaktualizuje stronę

---

Gratulacje! Masz teraz działającego agenta, który automatycznie aktualizuje stronę z wydarzeniami HR każdego dnia o 6:00 rano. Strona jest dostępna pod stałym URL, a wszystkie aktualizacje są wykonywane automatycznie.

W razie pytań lub problemów, skontaktuj się ze mną przez Manus.

