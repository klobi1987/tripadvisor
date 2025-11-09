# 🍽️ Dubravka 1836 Google Reviews Scraper

Skripta koja automatski izvlači **SVE** Google recenzije za Dubravka 1836 restoran i sprema ih u `DubravkaGoogle.csv`.

## ✨ Što radi?

✅ Otvara Google reviews page za Dubravka 1836
✅ Automatski scrolla i učitava **SVE** recenzije
✅ Klika sve "More" buttone za puni tekst
✅ Sortira po datumu (najnovije prvo)
✅ Izvlači:
- Ime recenzenta
- Local Guide status
- Broj recenzija korisnika
- Rating (broj zvjezdica)
- Puni tekst recenzije
- Datum recenzije
- Odgovor vlasnika (ako postoji)
- Broj fotografija u recenziji

✅ Sprema u **DubravkaGoogle.csv** i **DubravkaGoogle.json**

## 🚀 Kako pokrenuti?

### Korak 1: Provjeri da li imaš Python

```bash
python3 --version
```

Trebaš Python 3.7 ili noviji.

### Korak 2: Instaliraj dependencies

```bash
pip install -r requirements.txt
```

### Korak 3: Instaliraj ChromeDriver

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install chromium-chromedriver
```

**macOS:**
```bash
brew install chromedriver
```

**Windows:**
1. Preuzmi: https://chromedriver.chromium.org/
2. Raspakuj u `C:\chromedriver\`
3. Dodaj u PATH

### Korak 4: Pokreni scraper

```bash
python3 scrape_dubravka_google.py
```

## 📺 Što ćeš vidjeti?

1. **Otvara se Chrome browser** (vidiš ga uživo)
2. **Učitava Google reviews** za Dubravka 1836
3. **Automatski scrolla** kroz sve recenzije
4. **Klika "More" buttone** da proširi tekstove
5. **Sprema podatke** u DubravkaGoogle.csv

**Trajanje:** ~5-15 minuta (ovisno o broju recenzija)

## 📊 Rezultat: DubravkaGoogle.csv

CSV fajl sa svim podacima:

| Kolona | Primjer | Opis |
|--------|---------|------|
| `restaurant` | "Dubravka 1836" | Ime restorana |
| `reviewer_name` | "Marko Horvat" | Ime recenzenta |
| `reviewer_local_guide` | True/False | Je li Local Guide |
| `reviewer_reviews_count` | 127 | Ukupno recenzija korisnika |
| `reviewer_photos_count` | 45 | Ukupno fotografija korisnika |
| `rating` | 5 | Broj zvjezdica (1-5) |
| `review_text` | "Amazing food..." | Puni tekst recenzije |
| `review_date` | "2 months ago" | Datum |
| `owner_response` | "Thank you..." | Odgovor vlasnika |
| `review_photos_count` | 3 | Broj fotki u ovoj recenziji |
| `scraped_at` | "2025-01-09T..." | Kada je izvučeno |
| `source` | "Google" | Izvor podataka |

## ⚙️ Konfiguracija (opcionalno)

Otvori `scrape_dubravka_google.py` i pronađi liniju ~815:

```python
# Configuration
HEADLESS = False  # True = ne vidiš browser, False = vidiš browser
MAX_SCROLLS = 300  # Povećaj ako imaš 500+ recenzija
```

### Headless mode (bez GUI):

Ako želiš da scraper radi u pozadini:

```python
HEADLESS = True
```

### Više recenzija:

Ako imaš jako puno recenzija:

```python
MAX_SCROLLS = 500  # Ili više
```

## 🔧 Troubleshooting

### Problem: "ChromeDriver not found"

**Rješenje (Linux):**
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver
```

**Rješenje (macOS):**
```bash
brew install chromedriver
```

**Rješenje (Windows):**
1. Download: https://chromedriver.chromium.org/
2. Staviti u PATH environment variable

### Problem: "Selenium not installed"

**Rješenje:**
```bash
pip install selenium
```

### Problem: "No reviews found"

**Uzroci:**
1. Google Maps promijenio strukturu → provjeri debug HTML fajlove
2. Premalo scrollova → povećaj `MAX_SCROLLS`
3. URL nije ispravan

**Rješenje:**
```python
MAX_SCROLLS = 500  # Povećaj
```

### Problem: "Session not created"

**Uzrok:** ChromeDriver verzija ne odgovara Chrome verziji

**Rješenje:**
```bash
# Provjeri Chrome verziju
google-chrome --version

# Updateaj ChromeDriver na odgovarajuću verziju
```

### Problem: Browser se odmah zatvori

**Rješenje:** Dodaj pauzu na kraju skripte:

```python
# Na kraju run() metode, prije cleanup()
input("Press ENTER to close browser...")
self.cleanup()
```

## 📁 Output fajlovi

Nakon uspješnog izvođenja dobit ćeš:

| Fajl | Svrha |
|------|-------|
| **DubravkaGoogle.csv** | ⭐ Glavni fajl - sve recenzije |
| **DubravkaGoogle.json** | Backup u JSON formatu |
| **debug_dubravka_initial.html** | Debug - početna stranica |
| **debug_dubravka_final.html** | Debug - finalna stranica sa svim recenzijama |

## 💡 Pro tips

### 1. Backup podataka odmah

```bash
cp DubravkaGoogle.csv backups/DubravkaGoogle_$(date +%Y%m%d).csv
```

### 2. Provjeri koliko recenzija je izvučeno

```bash
wc -l DubravkaGoogle.csv
# Output: 347 DubravkaGoogle.csv  (347 linija = 346 recenzija + 1 header)
```

### 3. Otvori u Excel/LibreOffice

```bash
libreoffice DubravkaGoogle.csv
```

### 4. Filtriraj samo 5-star recenzije

```bash
grep ",5," DubravkaGoogle.csv > DubravkaGoogle_5stars.csv
```

### 5. Pronađi najčešće riječi u recenzijama

```python
import pandas as pd
from collections import Counter

df = pd.read_csv('DubravkaGoogle.csv')
all_text = ' '.join(df['review_text'].dropna()).lower()
words = all_text.split()
common = Counter(words).most_common(50)
print(common)
```

## 📈 Očekivani rezultati

| Metrika | Očekivano |
|---------|-----------|
| Broj recenzija | 200-400+ |
| Vrijeme izvođenja | 5-15 minuta |
| Prosječan rating | 4.0-4.8 ⭐ |
| Recenzije sa tekstom | 80-90% |
| Owner responses | 30-60% |
| Local Guide recenzije | 20-40% |

## 🔄 Usporedba sa TripAdvisor

Nakon što izvučeš Google recenzije, možeš ih usporediti sa TripAdvisor podacima:

```python
import pandas as pd

# Load both
google = pd.read_csv('DubravkaGoogle.csv')
tripadvisor = pd.read_csv('Dubravka.csv')

print(f"Google: {len(google)} recenzija")
print(f"TripAdvisor: {len(tripadvisor)} recenzija")

# Compare ratings
print(f"\nGoogle avg: {google['rating'].mean():.2f} ⭐")
print(f"TripAdvisor avg: {tripadvisor['rating'].mean():.2f} ⭐")
```

## 📝 Sljedeći koraci

Nakon što izvučeš Dubravka recenzije:

1. **Analiza sentimenta** - pozitivne vs negativne
2. **Keyword extraction** - što gosti hvale/kritiziraju
3. **Odgovori na recenzije** - koji komentari nemaju owner response
4. **Trend analiza** - kako se rating mijenjao kroz vrijeme
5. **Usporedba sa konkurencijom** - kako Dubravka stoji vs drugi restorani

## 🌐 Dodatni restorani

Ako želiš izvući recenzije i za ostale restorane (Nautika, Arsenal, Panorama), koristi:

```bash
python3 google_universal_scraper.py
```

Dodaj Google Maps URL-ove za svaki restoran u RESTAURANTS dictionary.

## 🆘 Podrška

Ako nešto ne radi:

1. **Provjeri debug fajlove:**
   ```bash
   firefox debug_dubravka_final.html
   ```

2. **Pokreni bez headless moda** da vidiš što se događa:
   ```python
   HEADLESS = False
   ```

3. **Povećaj verbosity** u kodu - dodaj više `print()` statementova

4. **Provjer ChromeDriver verziju**:
   ```bash
   chromedriver --version
   ```

---

## 📜 Licence & Legal

⚠️ **Important:**
- Use responsibly
- Respect Google Terms of Service
- Don't overload Google servers
- Use for personal/business analysis only
- Built-in delays to be respectful

---

**Autor:** Claude Code
**Verzija:** 1.0
**Datum:** 2025-01-09

**Enjoy scraping!** 🎉
