# HR Events Agent 🤖

Automatyczny agent do zbierania i aktualizowania wydarzeń HR w Polsce.

## 🚀 Funkcje

- ✅ **Automatyczne zbieranie** nowych wydarzeń HR z internetu
- ✅ **Codzienne aktualizacje** o 6:00 rano
- ✅ **Automatyczne usuwanie** przeszłych wydarzeń
- ✅ **Jeden stały URL** - brak nowych linków przy aktualizacjach
- ✅ **Responsywna strona** z filtrowaniem i wyszukiwaniem
- ✅ **Darmowy hosting** na GitHub Pages

## 🏗️ Architektura

```
├── .github/workflows/
│   └── update-events.yml     # GitHub Actions workflow
├── src/
│   ├── index.html           # Strona główna
│   ├── script.js            # Logika frontendu
│   └── style.css            # Style CSS
├── data/
│   └── events.json          # Baza danych wydarzeń
├── scripts/
│   └── scraper.py           # Skrypt zbierający dane
└── README.md
```

## 🔄 Jak to działa

1. **GitHub Actions** uruchamia się codziennie o 6:00
2. **Skrypt Python** przeszukuje internet w poszukiwaniu nowych wydarzeń HR
3. **Dane** są aktualizowane w pliku `events.json`
4. **Strona** jest automatycznie przebudowywana i publikowana
5. **GitHub Pages** serwuje zaktualizowaną stronę pod stałym URL

## 📅 Harmonogram

- **06:00** - Zbieranie nowych wydarzeń
- **00:00** - Usuwanie przeszłych wydarzeń
- **Co godzinę** - Aktualizacja liczników dni do deadline

## 🛠️ Instalacja

1. **Fork** tego repozytorium
2. **Włącz GitHub Pages** w ustawieniach repo
3. **Skonfiguruj GitHub Actions** (automatycznie aktywne)
4. **Gotowe!** Strona będzie dostępna pod `https://twoja-nazwa.github.io/hr-events-agent`

## 📊 Źródła danych

Agent automatycznie monitoruje:
- hrlityczny.pl
- pb.pl/konferencje
- stronakadry.pl
- crossweb.pl/wydarzenia/hr
- konferencjanowoczesnegohr.pl
- monikasmulewicz.pl
- hrtrends.pl
- eventbrite.pl
- meetup.com

## 🔧 Konfiguracja

Wszystkie ustawienia w pliku `.github/workflows/update-events.yml`:
- Harmonogram uruchamiania
- Źródła danych do monitorowania
- Filtry wydarzeń

## 📈 Monitoring

Agent automatycznie:
- Loguje wszystkie operacje
- Wysyła powiadomienia o błędach
- Śledzi liczbę znalezionych wydarzeń

## 🤝 Współpraca

Możesz ręcznie dodać wydarzenie:
1. Edytuj plik `data/events.json`
2. Commit i push
3. Strona zaktualizuje się automatycznie

---

**Stworzony przez Manus AI** 🤖

