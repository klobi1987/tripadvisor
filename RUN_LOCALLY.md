# ⚠️ VAŽNO: Scraper se mora pokrenuti LOKALNO

## Zašto ne radi na serveru?

Chrome browser **ne može raditi u sandbox/server okruženjima** zbog:
- Nedostatka GUI/display sistema
- Security restrictions (no-sandbox problemi)
- Memory limitations (/dev/shm)
- Chrome crashes u Docker/sandbox kontejnerima

**Rješenje:** Pokreni scraper na **svom računalu** (Windows, Mac, ili Linux desktop).

---

## 🚀 Kako pokrenuti lokalno (3 jednostavna koraka):

### 1️⃣ Pull kod sa GitHuba

```bash
git pull origin claude/csv-data-handling-011CUwtb3sw3p4mQmQQQ3FG9
```

### 2️⃣ Instaliraj dependencies

**Python biblioteke:**
```bash
pip install -r requirements.txt
```

**ChromeDriver:**

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt-get install chromium-chromedriver
  ```

- **macOS:**
  ```bash
  brew install chromedriver
  ```

- **Windows:**
  1. Download: https://chromedriver.chromium.org/
  2. Extract to `C:\chromedriver\`
  3. Add to PATH environment variable

### 3️⃣ Pokreni scraper

```bash
cd /putanja/do/tripadvisor/
python3 scrape_dubravka_google.py
```

---

## 📺 Što ćeš vidjeti:

```
╔══════════════════════════════════════════════════════════════════╗
║         DUBRAVKA 1836 - GOOGLE REVIEWS SCRAPER                   ║
╚══════════════════════════════════════════════════════════════════╝

✅ Chrome driver initialized
🔄 Opening Dubravka 1836 reviews...
✅ Page loaded
🍪 Checking for Google consent/privacy popups...
✅ Clicked consent button  ← AUTOMATSKI KLIKNE "PRIHVAĆAM"
🔍 Looking for reviews section...
✅ Found reviews section
📅 Sorting by newest...
✅ Sorted by newest
📜 Scrolling to load all reviews (max 300 scrolls)...
   Scrolled 20x...
   Scrolled 40x...
   ...
✅ Reached end after 89 scrolls
📖 Expanding review texts...
✅ Expanded 187 reviews
🔍 Extracting reviews...
   ✓ Extracted 50 reviews...
   ✓ Extracted 100 reviews...
   ✓ Extracted 150 reviews...
   ✓ Extracted 200 reviews...
✅ Successfully extracted 237 reviews

💾 ✅ Saved 237 reviews to DubravkaGoogle.csv
💾 Saved backup to DubravkaGoogle.json

======================================================================
📊 EXTRACTION SUMMARY
======================================================================
Total reviews: 237

⭐ Rating breakdown:
   5 stars: 142 reviews
   4 stars: 67 reviews
   3 stars: 18 reviews
   2 stars: 7 reviews
   1 stars: 3 reviews

📈 Average rating: 4.51 ⭐
📝 Reviews with text: 219
💬 Reviews with owner response: 98
🎖️  Reviews from Local Guides: 67

✅ SCRAPING COMPLETED SUCCESSFULLY!

📁 Output file: DubravkaGoogle.csv
```

**Vrijeme:** 5-15 minuta

---

## 📊 Rezultat: DubravkaGoogle.csv

CSV fajl sa svim kolonama:

```csv
restaurant,reviewer_name,reviewer_local_guide,reviewer_reviews_count,reviewer_photos_count,rating,review_text,review_date,owner_response,review_photos_count,scraped_at,source
Dubravka 1836,Marko Horvat,True,127,45,5,"Odlična hrana i pogled!",2 months ago,"Hvala vam!",3,2025-01-09T...,Google
```

---

## ⚙️ Opcije (u scrape_dubravka_google.py):

```python
# Linija ~733
HEADLESS = False  # True = ne vidiš browser, False = vidiš browser
MAX_SCROLLS = 300  # Povećaj za više recenzija
```

**Za brže izvođenje (ne vidiš browser):**
```python
HEADLESS = True
```

**Za više recenzija (500+):**
```python
MAX_SCROLLS = 500
```

---

## 🔧 Troubleshooting

### "ChromeDriver not found"
```bash
# Linux
sudo apt-get install chromium-chromedriver

# macOS
brew install chromedriver

# Windows
Download: https://chromedriver.chromium.org/
```

### "Selenium not installed"
```bash
pip install selenium
```

### "Tab crashed"
**Uzrok:** Sandbox okruženje (server/Docker)
**Rješenje:** **Mora pokrenuti lokalno** na svom računalu

### "No reviews found"
- Povećaj `MAX_SCROLLS = 500`
- Provjeri `debug_dubravka_final.html`

---

## 📁 Output fajlovi

Nakon uspješnog izvođenja:

| Fajl | Svrha |
|------|-------|
| **DubravkaGoogle.csv** | ⭐ Glavni - sve recenzije |
| **DubravkaGoogle.json** | Backup (JSON format) |
| **debug_dubravka_initial.html** | Debug - početna stranica |
| **debug_dubravka_final.html** | Debug - finalna stranica |

---

## 💡 Pro Tips

### 1. Test prvo sa malo scrollova
```python
MAX_SCROLLS = 50  # Test run
```

### 2. Backup odmah
```bash
cp DubravkaGoogle.csv backups/DubravkaGoogle_$(date +%Y%m%d).csv
```

### 3. Provjeri koliko recenzija
```bash
wc -l DubravkaGoogle.csv
```

### 4. Otvori u Excel
```bash
libreoffice DubravkaGoogle.csv  # Linux
open DubravkaGoogle.csv  # macOS
start DubravkaGoogle.csv  # Windows
```

---

## 🎯 Očekivani rezultati

| Metrika | Očekivano |
|---------|-----------|
| Broj recenzija | 200-400+ |
| Vrijeme | 5-15 minuta |
| Prosječan rating | 4.0-4.8 ⭐ |
| Sa tekstom | 80-90% |
| Sa owner response | 30-60% |
| Local Guides | 20-40% |

---

## ✅ Checklist prije pokretanja

- [ ] Git pull kod
- [ ] Instaliran Python 3.7+
- [ ] Instaliran `pip install -r requirements.txt`
- [ ] Instaliran ChromeDriver
- [ ] **NA LOKALNOM RAČUNALU** (ne server!)
- [ ] Terminal otvoren u tripadvisor direktoriju

Kada sve ✅, pokreni:
```bash
python3 scrape_dubravka_google.py
```

---

**Enjoy scraping!** 🎉

Više detalja: `DUBRAVKA_GOOGLE_SCRAPER_README.md`
