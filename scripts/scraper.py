#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HR Events Scraper
-----------------
Automatyczny skrypt do zbierania danych o wydarzeniach HR w Polsce.
Uruchamiany codziennie przez GitHub Actions.
"""

import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# Konfiguracja
SOURCES = [
    "https://hrlityczny.pl/wydarzenia-hr-w-2025-roku/",
    "https://www.pb.pl/konferencje/",
    "https://stronakadry.pl/",
    "https://crossweb.pl/wydarzenia/hr/",
    "https://www.konferencjanowoczesnegohr.pl/",
    "https://monikasmulewicz.pl/konferencja-hr/",
    "https://hrtrends.pl/",
]

# Ścieżki plików
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(ROOT_DIR, "data", "events.json")
LOG_FILE = os.path.join(ROOT_DIR, "data", "scraper_log.txt")

# Nagłówki HTTP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
}


def log_message(message):
    """Zapisuje wiadomość do pliku logów."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")


def load_events():
    """Ładuje istniejące wydarzenia z pliku JSON."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        # Jeśli plik nie istnieje lub jest pusty, tworzymy nową strukturę
        return {"events": [], "lastUpdate": datetime.now().isoformat(), "totalEvents": 0, "newEvents": 0, "eventsWithDeadlines": 0}


def save_events(data):
    """Zapisuje wydarzenia do pliku JSON."""
    # Aktualizacja metadanych
    data["lastUpdate"] = datetime.now().isoformat()
    data["totalEvents"] = len(data["events"])
    data["newEvents"] = sum(1 for event in data["events"] if event.get("isNew", False))
    data["eventsWithDeadlines"] = sum(1 for event in data["events"] if event.get("hasDeadline", False))
    
    # Zapisanie do pliku
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def remove_past_events(data):
    """Usuwa wydarzenia, które już się odbyły."""
    today = datetime.now().date()
    before_count = len(data["events"])
    
    data["events"] = [
        event for event in data["events"]
        if datetime.fromisoformat(event["date"]).date() >= today
    ]
    
    after_count = len(data["events"])
    removed_count = before_count - after_count
    
    if removed_count > 0:
        log_message(f"Usunięto {removed_count} przeszłych wydarzeń")
    
    return data


def update_days_to_deadline(data):
    """Aktualizuje liczbę dni pozostałych do deadline."""
    today = datetime.now().date()
    
    for event in data["events"]:
        if event.get("hasDeadline", False) and "deadline" in event:
            deadline_date = datetime.fromisoformat(event["deadline"]).date()
            days_left = (deadline_date - today).days
            
            # Jeśli deadline minął, usuwamy flagę hasDeadline
            if days_left < 0:
                event["hasDeadline"] = False
                log_message(f"Deadline minął dla wydarzenia: {event['title']}")
    
    return data


def scrape_events():
    """Główna funkcja scrapująca wydarzenia."""
    log_message("Rozpoczynam zbieranie danych o wydarzeniach HR")
    
    # Ładowanie istniejących wydarzeń
    data = load_events()
    
    # Usuwanie przeszłych wydarzeń
    data = remove_past_events(data)
    
    # Aktualizacja dni do deadline
    data = update_days_to_deadline(data)
    
    # Tworzenie słownika istniejących wydarzeń dla łatwego wyszukiwania
    existing_events = {event["title"].lower(): event for event in data["events"]}
    
    # Licznik nowych wydarzeń
    new_events_count = 0
    
    # Przeszukiwanie źródeł
    for source_url in SOURCES:
        try:
            log_message(f"Przeszukuję źródło: {source_url}")
            
            # Pobieranie strony
            response = requests.get(source_url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            # Parsowanie HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Przykładowa logika wyszukiwania wydarzeń (do dostosowania dla każdego źródła)
            events_found = extract_events_from_page(soup, source_url)
            
            # Dodawanie nowych wydarzeń
            for event in events_found:
                event_title_lower = event["title"].lower()
                
                # Sprawdzanie czy wydarzenie już istnieje
                if event_title_lower not in existing_events:
                    # Generowanie unikalnego ID
                    event_id = generate_event_id(event["title"])
                    
                    # Dodawanie dodatkowych pól
                    event["id"] = event_id
                    event["isNew"] = True
                    event["addedDate"] = datetime.now().strftime("%Y-%m-%d")
                    
                    # Dodawanie wydarzenia do danych
                    data["events"].append(event)
                    existing_events[event_title_lower] = event
                    
                    new_events_count += 1
                    log_message(f"Dodano nowe wydarzenie: {event['title']}")
            
            # Przerwa między zapytaniami
            time.sleep(2)
            
        except Exception as e:
            log_message(f"Błąd podczas przeszukiwania {source_url}: {str(e)}")
    
    # Sortowanie wydarzeń chronologicznie
    data["events"].sort(key=lambda x: x["date"])
    
    # Zapisywanie zaktualizowanych danych
    save_events(data)
    
    log_message(f"Zakończono zbieranie danych. Dodano {new_events_count} nowych wydarzeń.")
    return new_events_count


def extract_events_from_page(soup, source_url):
    """
    Ekstrahuje wydarzenia z HTML strony.
    Ta funkcja musi być dostosowana do struktury każdej strony źródłowej.
    """
    events = []
    
    # Przykładowa implementacja - w rzeczywistości trzeba dostosować do każdego źródła
    # To jest tylko szkielet, który trzeba wypełnić specyficzną logiką dla każdej strony
    
    domain = urlparse(source_url).netloc
    
    if "hrlityczny.pl" in domain:
        # Logika dla hrlityczny.pl
        event_elements = soup.select(".event-card, .event-container, article.event")
        for element in event_elements:
            try:
                title_elem = element.select_one("h2, .event-title, .title")
                date_elem = element.select_one(".date, .event-date, time")
                location_elem = element.select_one(".location, .event-location, .place")
                
                if title_elem and date_elem:
                    title = title_elem.get_text(strip=True)
                    date_text = date_elem.get_text(strip=True)
                    location = location_elem.get_text(strip=True) if location_elem else "Polska"
                    
                    # Parsowanie daty (przykład)
                    date = parse_date(date_text)
                    
                    # Tworzenie wydarzenia
                    event = {
                        "title": title,
                        "date": date,
                        "location": location,
                        "category": detect_category(title),
                        "status": "Do potwierdzenia",
                        "description": extract_description(element),
                        "tags": extract_tags(title),
                        "pricing": "Do sprawdzenia",
                        "hasDeadline": False,
                        "url": extract_url(element, source_url)
                    }
                    
                    events.append(event)
            except Exception as e:
                log_message(f"Błąd podczas parsowania wydarzenia: {str(e)}")
    
    # Podobne bloki dla innych źródeł...
    
    return events


def generate_event_id(title):
    """Generuje unikalny ID wydarzenia na podstawie tytułu."""
    # Usuwanie znaków specjalnych i zamiana na małe litery
    base = re.sub(r'[^\w\s]', '', title.lower())
    # Zamiana spacji na myślniki
    base = re.sub(r'\s+', '-', base)
    # Dodanie losowego sufiksu dla unikalności
    random_suffix = uuid.uuid4().hex[:6]
    return f"{base}-{random_suffix}"


def parse_date(date_text):
    """Parsuje datę z tekstu do formatu ISO."""
    # Przykładowa implementacja - w rzeczywistości trzeba obsłużyć różne formaty dat
    try:
        # Próba parsowania różnych formatów dat
        formats = [
            "%d.%m.%Y", "%d-%m-%Y", "%Y-%m-%d",
            "%d %B %Y", "%d %b %Y",
            "%B %d, %Y", "%b %d, %Y"
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_text, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Jeśli nie udało się sparsować, próbujemy wyciągnąć rok, miesiąc i dzień
        year_match = re.search(r'20\d{2}', date_text)
        month_match = re.search(r'(styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)', date_text, re.IGNORECASE)
        day_match = re.search(r'\b(\d{1,2})\b', date_text)
        
        if year_match and month_match and day_match:
            year = year_match.group(0)
            month = {
                'styczeń': 1, 'luty': 2, 'marzec': 3, 'kwiecień': 4, 'maj': 5, 'czerwiec': 6,
                'lipiec': 7, 'sierpień': 8, 'wrzesień': 9, 'październik': 10, 'listopad': 11, 'grudzień': 12
            }[month_match.group(0).lower()]
            day = int(day_match.group(0))
            
            return f"{year}-{month:02d}-{day:02d}"
        
        # Jeśli wszystko zawiedzie, zwracamy datę za miesiąc jako przybliżenie
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    except Exception:
        # W przypadku błędu, zwracamy datę za miesiąc
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")


def detect_category(title):
    """Wykrywa kategorię wydarzenia na podstawie tytułu."""
    title_lower = title.lower()
    
    if any(keyword in title_lower for keyword in ["konkurs", "ranking", "nagroda", "award"]):
        return "Konkursy"
    elif any(keyword in title_lower for keyword in ["ai", "sztuczna inteligencja", "machine learning"]):
        return "AI w HR"
    elif any(keyword in title_lower for keyword in ["tech", "digital", "technologia", "it"]):
        return "HR Tech"
    elif any(keyword in title_lower for keyword in ["wellbeing", "dobrostan", "zdrowie", "well-being"]):
        return "Wellbeing"
    else:
        return "HR"


def extract_description(element):
    """Ekstrahuje opis wydarzenia z elementu HTML."""
    desc_elem = element.select_one(".description, .event-description, .content, p")
    if desc_elem:
        return desc_elem.get_text(strip=True)
    return "Szczegóły wkrótce."


def extract_tags(title):
    """Generuje tagi na podstawie tytułu wydarzenia."""
    # Przykładowe słowa kluczowe do wyszukiwania
    keywords = [
        "hr", "rekrutacja", "talent", "employer branding", "onboarding", "offboarding",
        "wellbeing", "benefity", "wynagrodzenia", "kompetencje", "rozwój", "szkolenia",
        "przywództwo", "zarządzanie", "kultura organizacyjna", "zaangażowanie", "motywacja",
        "technologia", "ai", "automatyzacja", "digitalizacja", "transformacja", "innowacje",
        "prawo pracy", "compliance", "bhp", "różnorodność", "inkluzywność", "równość",
        "konferencja", "warsztat", "szkolenie", "webinar", "kongres", "summit", "forum"
    ]
    
    title_lower = title.lower()
    tags = []
    
    # Dodawanie tagów na podstawie słów kluczowych
    for keyword in keywords:
        if keyword in title_lower:
            tags.append(keyword)
    
    # Jeśli mamy mniej niż 3 tagi, dodajemy domyślne
    if len(tags) < 3:
        default_tags = ["hr", "wydarzenie", "konferencja"]
        for tag in default_tags:
            if tag not in tags:
                tags.append(tag)
                if len(tags) >= 5:
                    break
    
    return tags[:5]  # Maksymalnie 5 tagów


def extract_url(element, source_url):
    """Ekstrahuje URL wydarzenia z elementu HTML."""
    url_elem = element.select_one("a.more, a.details, a.event-link, a[href*='event']")
    if url_elem and url_elem.has_attr("href"):
        url = url_elem["href"]
        # Jeśli URL jest względny, dodajemy domenę
        if not url.startswith(("http://", "https://")):
            parsed_source = urlparse(source_url)
            base_url = f"{parsed_source.scheme}://{parsed_source.netloc}"
            url = f"{base_url}{url if url.startswith('/') else '/' + url}"
        return url
    return source_url


if __name__ == "__main__":
    try:
        # Tworzenie katalogu logów, jeśli nie istnieje
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        
        # Uruchomienie scrapera
        new_events = scrape_events()
        
        # Wyjście z kodem sukcesu
        sys.exit(0)
    except Exception as e:
        log_message(f"Krytyczny błąd: {str(e)}")
        sys.exit(1)

