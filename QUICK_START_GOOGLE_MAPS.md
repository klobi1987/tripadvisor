# 🚀 Quick Start - Google Maps Scraper

Brzi vodič za pokretanje Google Maps scrapera za izvlačenje svih recenzija.

## ⚡ 5 minuta do prvih recenzija

### 1️⃣ Instaliraj dependencije (jednom)

```bash
# Instaliraj Python biblioteke
pip install -r requirements.txt

# Instaliraj ChromeDriver (Linux)
sudo apt-get install chromium-chromedriver

# Ili (macOS)
brew install chromedriver
```

### 2️⃣ Pronađi Google Maps URL-ove

**Opcija A - Automatski (PREPORUČENO):**
```bash
python3 find_google_maps_urls.py
```

Skripta će:
1. Otvoriti browser
2. Automatski pretraživati svaki restoran
3. Izvući URL-ove
4. Ispisati kod koji kopiraš u `google_maps_scraper.py`

**Opcija B - Ručno:**
1. Idi na Google Maps → https://maps.google.com
2. Pretraži "Restaurant Nautika Dubrovnik"
3. Klikni na restoran
4. Kopiraj URL iz browser address bara
5. Ponovi za Arsenal, Panorama, Dubravka

### 3️⃣ Dodaj URL-ove u scraper

Otvori `google_maps_scraper.py` i pronađi liniju ~14:

```python
RESTAURANTS = {
    "Arsenal": {
        "name": "Arsenal Restaurant",
        "url": "https://www.google.com/maps/place/...",  # 👈 PASTE URL HERE
        "location": "Dubrovnik"
    },
    "Panorama": {
        "name": "Restaurant Panorama",
        "url": "https://www.google.com/maps/place/...",  # 👈 PASTE URL HERE
        "location": "Dubrovnik"
    },
    "Dubravka": {
        "name": "Dubravka 1836 Restaurant & Cafe",
        "url": "https://www.google.com/maps/place/...",  # 👈 PASTE URL HERE
        "location": "Dubrovnik"
    },
    "Nautika": {
        "name": "Restaurant Nautika",
        "url": "https://www.google.com/maps/place/...",  # 👈 PASTE URL HERE
        "location": "Dubrovnik"
    }
}
```

### 4️⃣ Pokreni scraper

```bash
python3 google_maps_scraper.py
```

**Što će se dogoditi:**
```
✅ Chrome driver initialized successfully
🔄 Loading: https://www.google.com/maps/...
✅ Page loaded successfully
✅ Clicked reviews tab
✅ Sorted by newest
📜 Scrolling reviews panel (max 200 scrolls)...
✅ Reached end of reviews after 87 scrolls
✅ Expanded 143 'Read more' buttons
💾 Saved page source to debug_google_maps_Restaurant_Nautika.html
✅ Found 237 review elements
  ✓ Extracted 50 reviews...
  ✓ Extracted 100 reviews...
  ✓ Extracted 150 reviews...
📊 Total reviews extracted: 237

⏸️  Waiting 10 seconds before next restaurant...
```

### 5️⃣ Provjeri rezultate

```bash
# Vidi koliko recenzija je izvučeno
wc -l google_maps_reviews.csv

# Otvori CSV u Excel/LibreOffice
libreoffice google_maps_reviews.csv

# Ili vidi u terminalu (prvih 10 linija)
head -n 10 google_maps_reviews.csv
```

## 📊 Očekivani Output

**Fajlovi:**
- `google_maps_reviews.csv` - Sve recenzije (glavni fajl)
- `google_maps_reviews.json` - JSON format (za programere)
- `debug_google_maps_*.html` - Debug fajlovi (za troubleshooting)

**CSV stupci:**
```
restaurant, reviewer_name, reviewer_local_guide, reviewer_total_reviews,
rating, review_text, review_date, owner_response, owner_response_date,
photos_count, scraped_at, source
```

**Statistika:**
```
📊 SUMMARY
============================================================
Total reviews scraped: 1,247
  • Restaurant Nautika: 312 reviews
  • Arsenal Restaurant: 289 reviews
  • Restaurant Panorama: 398 reviews
  • Dubravka 1836 Restaurant & Cafe: 248 reviews

📈 Average Ratings:
  • Restaurant Nautika: 4.52 ⭐
  • Arsenal Restaurant: 4.38 ⭐
  • Restaurant Panorama: 4.61 ⭐
  • Dubravka 1836 Restaurant & Cafe: 4.44 ⭐
```

## ⚙️ Konfiguracija

### Promjena broja scrollova

U `google_maps_scraper.py`, linija ~489:

```python
MAX_SCROLLS = 200  # Povećaj na 300-500 za više recenzija
```

### Headless mode (bez GUI)

```python
HEADLESS = True  # Browser se ne vidi, radi u pozadini
```

### Pojedinačan restoran (za test)

Komentiraj ostale restorane:

```python
RESTAURANTS = {
    "Nautika": {
        "name": "Restaurant Nautika",
        "url": "https://...",
        "location": "Dubrovnik"
    },
    # "Arsenal": { ... },  # ← Komentirano
    # "Panorama": { ... },
    # "Dubravka": { ... },
}
```

## 🔧 Troubleshooting

| Problem | Rješenje |
|---------|----------|
| `Selenium not installed` | `pip install selenium` |
| `ChromeDriver not found` | `sudo apt-get install chromium-chromedriver` |
| `No reviews found` | Povećaj `MAX_SCROLLS = 300` |
| Browser se odmah zatvori | Dodaj `input()` prije `cleanup()` |
| SSL error | Dodaj `--ignore-certificate-errors` u Chrome options |

## 💡 Pro Tips

### 1. Test prvo na jednom restoranu
Koristi samo Nautiku za prvi test run.

### 2. Backup podataka
```bash
cp google_maps_reviews.csv backups/google_maps_$(date +%Y%m%d).csv
```

### 3. Spojiti sa TripAdvisor podacima
```python
import pandas as pd

google = pd.read_csv('google_maps_reviews.csv')
tripadvisor = pd.read_csv('Nautika.csv')  # ili drugi TA CSV

# Analiza razlika
print(f"Google: {len(google)} recenzija")
print(f"TripAdvisor: {len(tripadvisor)} recenzija")
```

### 4. Sentiment analiza
Koristi postojeće CSV fajlove za sentiment:
- `analysis_sentiment_breakdown.csv`
- `analysis_positive_praise.csv`
- `analysis_negative_complaints.csv`

## 📈 Sljedeći koraci

Nakon izvlačenja Google Maps recenzija:

1. **Usporedi sa TripAdvisor** - koji su najčešći komentari?
2. **Analiziraj odgovore vlasnika** - koliko brzo odgovaraju?
3. **Provjeri Local Guides** - što hvale influenceri?
4. **Keyword analysis** - najčešće riječi u pozitivnim/negativnim recenzijama
5. **Foto analiza** - koje stvari gosti najčešće slikaju?

## 🎯 Use Cases

### Case 1: Pronađi što gosti kritiziraju
```bash
grep -i "bad\|poor\|terrible\|awful" google_maps_reviews.csv | head -20
```

### Case 2: Najbolje recenzije (5 zvjezdica)
```python
import pandas as pd
df = pd.read_csv('google_maps_reviews.csv')
best = df[df['rating'] == 5].head(20)
print(best[['reviewer_name', 'review_text']])
```

### Case 3: Odgovori na nove recenzije
```python
df = pd.read_csv('google_maps_reviews.csv')
no_response = df[df['owner_response'].isna()]
print(f"Recenzije bez odgovora: {len(no_response)}")
```

## 🆘 Pomoć

**Provjeri debug fajlove:**
```bash
ls -lh debug_google_maps_*.html
```

**Otvori u browseru:**
```bash
firefox debug_google_maps_Restaurant_Nautika.html
```

**Povećaj verbosity:**
U kodu dodaj više `print()` statementova za debugging.

---

**Enjoy scraping!** 🎉

Sretno s analizom recenzija! Ako nešto ne radi, provjeri `README_GOOGLE_MAPS.md` za detaljnije upute.
