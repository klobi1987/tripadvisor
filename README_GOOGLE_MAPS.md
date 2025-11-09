# Google Maps Reviews Scraper - Vodič

Ovaj scraper automatski izvlači **sve** Google Maps recenzije za vaše restorane koristeći Selenium browser automation.

## 🎯 Što radi?

- ✅ Otvara Google Maps stranicu restorana u browseru
- ✅ Automatski klika na "Reviews" tab
- ✅ Sortira recenzije (po novosti)
- ✅ Automatski scrolla i učitava **SVE** recenzije
- ✅ Klika na sve "Read more" buttone da proširi pun tekst
- ✅ Izvlači sve podatke: ime, rating, tekst, datum, odgovor vlasnika
- ✅ Sprema u CSV i JSON format

## 📋 Preduvjeti

### 1. Python (verzija 3.7+)
```bash
python3 --version
```

### 2. Instalacija biblioteka
```bash
pip install selenium
```

### 3. ChromeDriver

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver
```

**macOS:**
```bash
brew install chromedriver
```

**Windows:**
1. Preuzmi sa: https://chromedriver.chromium.org/
2. Raspakuj i dodaj u PATH

## 🚀 Kako koristiti?

### Korak 1: Dodaj Google Maps URL-ove

Prvo moraš pronaći Google Maps URL-ove za svaki restoran:

1. Idi na **Google Maps** (https://maps.google.com)
2. Pretraži restoran (npr. "Restaurant Nautika Dubrovnik")
3. Klikni na restoran
4. Kopiraj URL iz browser address bar-a
5. Dodaj URL u `google_maps_scraper.py`

**Primjer URL-a:**
```
https://www.google.com/maps/place/Restaurant+Nautika/@42.6403529,18.1061635,17z/data=...
```

**Otvori `google_maps_scraper.py` i pronađi RESTAURANTS dictionary (linija ~14):**
```python
RESTAURANTS = {
    "Arsenal": {
        "name": "Arsenal Restaurant",
        "url": "https://www.google.com/maps/place/...",  # 👈 OVDJE DODAJ URL
        "location": "Dubrovnik"
    },
    "Panorama": {
        "name": "Restaurant Panorama",
        "url": "https://www.google.com/maps/place/...",  # 👈 OVDJE DODAJ URL
        "location": "Dubrovnik"
    },
    # ... itd
}
```

### Korak 2: Pokreni scraper

```bash
python3 google_maps_scraper.py
```

**Što će se dogoditi:**

1. 🌐 Otvara Chrome browser (vidiš ga)
2. 🔄 Učitava Google Maps stranicu prvog restorana
3. 📜 Automatski scrolla i učitava sve recenzije
4. 💾 Sprema podatke u CSV i JSON
5. ⏸️  Čeka 10 sekundi
6. 🔁 Prelazi na sljedeći restoran
7. ✅ Na kraju zatvara browser i prikazuje statistiku

### Korak 3: Provjeri rezultate

Nakon završetka dobit ćeš:

- **`google_maps_reviews.csv`** - Sve recenzije u CSV formatu
- **`google_maps_reviews.json`** - Sve recenzije u JSON formatu
- **`debug_google_maps_*.html`** - Debug fajlovi (za troubleshooting)

## ⚙️ Konfiguracija

Otvori `google_maps_scraper.py` i pronađi `main()` funkciju (linija ~489):

```python
# Configuration
HEADLESS = False  # True = bez GUI, False = vidiš browser
MAX_SCROLLS = 200  # Broj scrollova (200 je dovoljno za većinu restorana)
```

### Headless Mode

Ako želiš da scraper radi **u pozadini** (bez vidljivog browsera):

```python
HEADLESS = True
```

### Broj Scrollova

Ako restoran ima **jako puno** recenzija (500+), povećaj:

```python
MAX_SCROLLS = 500
```

## 📊 Output Format (CSV)

| Kolona | Opis |
|--------|------|
| `restaurant` | Ime restorana |
| `reviewer_name` | Ime recenzenta |
| `reviewer_local_guide` | Je li Local Guide (True/False) |
| `reviewer_total_reviews` | Ukupan broj recenzija ovog korisnika |
| `rating` | Broj zvjezdica (1-5) |
| `review_text` | Puni tekst recenzije |
| `review_date` | Datum recenzije (npr. "3 months ago") |
| `owner_response` | Odgovor vlasnika (ako postoji) |
| `owner_response_date` | Datum odgovora vlasnika |
| `photos_count` | Broj fotografija u recenziji |
| `scraped_at` | Timestamp kada je izvučeno |
| `source` | Uvijek "Google Maps" |

## 🔧 Troubleshooting

### Problem: "Selenium not installed"
**Rješenje:**
```bash
pip install selenium
```

### Problem: "ChromeDriver not found"
**Rješenje (Linux):**
```bash
sudo apt-get install chromium-chromedriver
```

**Rješenje (macOS):**
```bash
brew install chromedriver
```

**Rješenje (Windows):**
1. Preuzmi sa: https://chromedriver.chromium.org/
2. Raspakuj u `C:\chromedriver\`
3. Dodaj `C:\chromedriver\` u PATH environment variable

### Problem: "No reviews found"
**Mogući uzroci:**
1. Google Maps promijenio HTML strukturu → provjeri `debug_*.html` fajlove
2. URL nije ispravan → provjeri da li URL pokazuje na restoran
3. Malo scrollova → povećaj `MAX_SCROLLS`

**Rješenje:**
```python
MAX_SCROLLS = 300  # Povećaj broj scrollova
```

### Problem: Browser se zatvori prerano
**Rješenje:** Dodaj `input()` na kraj skripte da zadržiš browser otvorenim:

```python
# Na kraju main() funkcije, prije cleanup()
input("Press ENTER to close browser...")
scraper.cleanup()
```

### Problem: "Certificate error" ili "SSL error"
**Rješenje:** Dodaj u Chrome options:
```python
chrome_options.add_argument('--ignore-certificate-errors')
```

## 💡 Savjeti

### 1. Pokreni prvo na jednom restoranu
Da testiraš da sve radi, komentiraj ostale restorane:

```python
RESTAURANTS = {
    "Nautika": {
        "name": "Restaurant Nautika",
        "url": "https://...",
        "location": "Dubrovnik"
    },
    # "Arsenal": { ... },  # Komentirano
    # "Panorama": { ... },  # Komentirano
}
```

### 2. Headless mode za produkciju
Kada sve radi, koristi headless mode za brže izvođenje:
```python
HEADLESS = True
```

### 3. Rate limiting
Scraper već ima built-in delays:
- 2 sekunde između scrollova
- 10 sekundi između restorana
- Random delays za "Read more" buttone

**NE smanjuj delays!** Google može blokirati IP ako si preagresivan.

### 4. Backup podataka
Spremi CSV fajlove odmah nakon scrapinga:
```bash
cp google_maps_reviews.csv google_maps_reviews_backup_$(date +%Y%m%d).csv
```

## 📈 Očekivani rezultati

| Restoran | Očekivani broj recenzija | Vrijeme scrapinga |
|----------|--------------------------|-------------------|
| Nautika | 500+ | ~5-10 minuta |
| Arsenal | 300+ | ~3-5 minuta |
| Panorama | 400+ | ~4-8 minuta |
| Dubravka | 350+ | ~3-6 minuta |
| **UKUPNO** | **~1500+** | **~15-30 minuta** |

## 🔄 Usporedba sa TripAdvisor

| Feature | Google Maps | TripAdvisor |
|---------|-------------|-------------|
| Broj recenzija | Više | Manje (fokus na turiste) |
| Lokalni gosti | ✅ Puno | ❌ Malo |
| Strani turisti | ✅ Da | ✅✅ Najviše |
| Autentičnost | ✅ Verificirano | ⚠️ Može biti fake |
| Odgovor vlasnika | ✅ Vidljivo | ✅ Vidljivo |
| Fotografije | ✅✅ Puno | ✅ Umjereno |

## 📝 Sljedeći koraci

Nakon što izvučeš sve Google Maps recenzije:

1. **Analiza podataka** - koristi Python/Excel za analizu
2. **Sentiment analysis** - pozitivne vs negativne
3. **Keyword extraction** - što gosti hvale/kritiziraju
4. **Usporedba sa TripAdvisor** - razlike između platformi
5. **Response strategy** - odgovaraj na recenzije

## 🆘 Podrška

Ako nešto ne radi:

1. Provjeri `debug_*.html` fajlove
2. Povećaj `MAX_SCROLLS`
3. Isprobaj bez headless moda (`HEADLESS = False`)
4. Updateaj ChromeDriver: `brew upgrade chromedriver` (macOS)

## 📜 Licenca

Free to use. Koristi odgovorno i poštuj Google Terms of Service.

---

**Autor:** Claude Code
**Verzija:** 1.0
**Datum:** 2025-01-09
