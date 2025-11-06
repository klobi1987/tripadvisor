# 🔧 Dianping Scraping Guide

Kompletni vodič za izvlačenje recenzija sa Dianping.com platforme za vaše restorane u Dubrovniku.

## 📋 Sadržaj

1. [Pregled problema](#pregled-problema)
2. [Dostupna rješenja](#dostupna-rješenja)
3. [Preporučeni pristup](#preporučeni-pristup)
4. [Detaljne upute](#detaljne-upute)
5. [Rezultati](#rezultati)

---

## ⚠️ Pregled Problema

**Dianping.com (大众点评)** je kineska platforma za recenzije restorana, ekvivalent TripAdvisor-u za kinesko tržište.

### Glavni izazovi:

1. **Zahtijeva prijavu** - Stranice sa recenzijama nisu dostupne bez kineskog računa
2. **Geo-blokada** - Često je potreban kineski IP ili VPN
3. **Kineski broj mobitela** - Za registraciju potreban kineski broj telefona
4. **JavaScript rendering** - Sadržaj se učitava dinamički
5. **Anti-bot zaštita** - CAPTCHA i detekcija automatizacije

### Vaši restorani na Dianping:

| Restoran | Broj recenzija | Cijena po osobi | ID |
|----------|---------------|-----------------|-----|
| **Gradska kavana Arsenal** | 189 | ¥305 (~€40) | `qB4r617...` |
| **Restaurant Panorama** | 224 | ¥253 (~€33) | `qB4r4d7...` |
| **Dubravka 1836 Restaurant & Cafe** | 153 | ¥234 (~€30) | `qB4r617...` |
| **Restaurant Nautika** | ? | ? | Još tražimo |

---

## 🛠️ Dostupna Rješenja

Kreirano je **3 različita alata** za različite scenarije:

### 1. `dianping_scraper.py` - Osnovni Scraper
**Najbolje za:** Brza provjera dostupnosti, testiranje
**Prednosti:**
- Jednostavan, bez dodatnih zavisnosti
- Brz za pokretanje
- Radi sa request-based pristupom

**Nedostaci:**
- ❌ Ne može zaobići login zahtjev
- ❌ Ne izvlači JavaScript sadržaj
- Ograničen uspjeh zbog anti-bot zaštite

**Kako pokrenuti:**
```bash
python3 dianping_scraper.py
```

---

### 2. `dianping_selenium_scraper.py` - Napredni Selenium Scraper
**Najbolje za:** Automatizacija sa pravim browser-om
**Prednosti:**
- ✅ Simulira pravi browser
- ✅ Izvršava JavaScript
- ✅ Omogućava ručnu prijavu
- ✅ Sprema cookies za buduću upotrebu
- ✅ Može koristiti proxy

**Zahtjevi:**
```bash
pip install selenium
# Također treba ChromeDriver: https://chromedriver.chromium.org/
```

**Kako pokrenuti:**
```bash
python3 dianping_selenium_scraper.py
```

**Proces:**
1. Scraper će otvoriti Chrome browser
2. Automatski će otići na Dianping stranicu
3. **Pauziraće i čekat će da se RUČNO prijavite**
4. Nakon prijave, pritisnite ENTER
5. Scraper će nastaviti automatski i izvući sve recenzije
6. Cookies će biti spremljeni za buduću upotrebu

---

### 3. `dianping_manual_extractor.py` - Ručni HTML Ekstraktor
**Najbolje za:** Garantiran uspjeh, bez automatizacije
**Prednosti:**
- ✅ 100% uspješan
- ✅ Nema problema sa blokiranjem
- ✅ Ne treba poseban software
- ✅ Možete vidjeti točno što izvlačite

**Proces:**

#### Korak 1: Spremite HTML stranice
1. Otvorite Chrome/Firefox browser
2. Prijavite se na Dianping.com (ili zamolite kineskog kolegu)
3. Otvorite stranicu svakog restorana:
   - https://www.dianping.com/shop/qB4r61... (Arsenal)
   - https://www.dianping.com/shop/qB4r4d7... (Panorama)
   - https://www.dianping.com/shop/qB4r617... (Dubravka)
4. **Skrolajte dolje** da se učitaju sve recenzije
5. Desni klik → **Save As** → **Webpage, Complete**
6. Spremite kao:
   - `arsenal.html`
   - `panorama.html`
   - `dubravka.html`
   - `nautika.html`

#### Korak 2: Pokrenite ekstraktor
```bash
python3 dianping_manual_extractor.py
```

Ekstraktor će:
- Automatski pronaći sve `.html` fajlove u direktoriju
- Analizirati HTML strukturu
- Izvući sve recenzije
- Spremiti u JSON i CSV format

---

## 🎯 Preporučeni Pristup

### Opcija A: Ako imate kineski Dianping račun
**Koristite:** `dianping_selenium_scraper.py`

**Koraci:**
1. Instalirajte Selenium i ChromeDriver
2. Pokrenite scraper
3. Prijavite se kada zatražite
4. Pričekajte da scraper završi
5. Rezultati će biti spremljeni automatski

### Opcija B: Ako NEMATE kineski Dianping račun
**Koristite:** `dianping_manual_extractor.py`

**Koraci:**
1. Angažirajte kinesku digitalnu agenciju ili kontaktirajte kineskog prijatelja
2. Zamolite ih da pristupe stranicama vaših restorana
3. Neka spremite stranice kao HTML
4. Pošaljite vam HTML fajlove
5. Pokrenite ekstraktor na tim fajlovima

### Opcija C: Profesionalni servis
Angažirajte kinesku digitalnu marketing agenciju koja specijalizira:
- Upravljanje Dianping profilima
- Izvlačenje i analiza recenzija
- Prevođenje komentara
- Odgovaranje na recenzije na kineskom

**Preporučene agencije:**
- Dragon Social (dragontrail.com)
- Jing Social
- Hot Pot Digital

---

## 📖 Detaljne Upute - Ručna Ekstrakcija

Ovo je **najsigurniji** način da dobijete recenzije.

### 1. Pristup Dianping-u

**Ako ste u Kini ili imate VPN:**
- Jednostavno se prijavite na dianping.com
- Koristite WeChat login ili kineski broj

**Ako ste van Kine:**
- Koristite VPN sa kineskim serverom (ExpressVPN, NordVPN)
- Ili zamolite kineskog kolegu/prijatelja

### 2. Navigacija do restorana

Direktni linkovi:

```
Arsenal:
https://www.dianping.com/shop/qB4r61711ac153e9c2b00ae22cce1e053615fcf47764c6e8720ce0d6677aab3126c49d2a41ed92aaaff8282c246900vxu5

Panorama:
https://www.dianping.com/shop/qB4r4d7c30a347b1eeb81bfe76fa5a021e14fcf47764c6e8720ce0d6677aab3126c49d2a41ed92aaaff8282c246900vxu5

Dubravka:
https://www.dianping.com/shop/qB4r617f7ed90fe7cbe317eb70d11d0e386efcf47764c6e8720ce0d6677aab3126c49d2a41ed92aaaff8282c246900vxu5
```

### 3. Spremanje stranica

**Chrome:**
1. Ctrl+S (ili Cmd+S na Mac)
2. Odaberite "Webpage, Complete"
3. Imenovati fajl (npr. `arsenal.html`)
4. Kliknite Save

**Firefox:**
1. Ctrl+S
2. Odaberite "Web Page, complete"
3. Imenovati fajl
4. Spremiti

**VAŽNO:**
- Prije spremanja, skrolajte do kraja stranice da se učitaju SVE recenzije
- Dianping često učitava recenzije postepeno, pa čekajte da se sve učita

### 4. Pokretanje ekstraktora

```bash
# Provjerite da li su svi HTML fajlovi u direktoriju
ls *.html

# Pokrenite ekstraktor
python3 dianping_manual_extractor.py
```

### 5. Analiza HTML strukture (opciono)

Ako ekstraktor ne pronađe recenzije automatski:

```bash
# Analizirajte strukturu stranice
python3 dianping_manual_extractor.py --analyze
```

Ovo će vam pokazati:
- Sve CSS klase koje sadrže "review", "comment", etc.
- IDs koji mogu biti korisni
- Embedded JSON podatke

---

## 📊 Rezultati

Nakon uspješnog scrapinga, dobićete:

### JSON format (`dianping_reviews.json`):
```json
[
  {
    "restaurant": "Gradska kavana Arsenal Restaurant",
    "reviewer": "张三",
    "rating": 4.5,
    "review_text": "非常好的餐厅，食物美味，服务周到...",
    "date": "2024-01-15",
    "photos": ["https://..."],
    "scraped_at": "2024-01-20T10:30:00"
  },
  ...
]
```

### CSV format (`dianping_reviews.csv`):
| restaurant | reviewer | rating | review_text | date |
|-----------|----------|--------|-------------|------|
| Arsenal | 张三 | 4.5 | 非常好的餐厅... | 2024-01-15 |
| Panorama | 李四 | 5.0 | 景色优美... | 2024-01-10 |

---

## 🔧 Troubleshooting

### Problem: "Login required"
**Rješenje:**
- Koristite Selenium scraper i prijavite se ručno
- Ili koristite Manual Extractor pristup

### Problem: "No reviews found"
**Rješenje:**
1. Provjerite HTML strukturu: `--analyze` opcija
2. Stranica možda koristi različite CSS klase
3. Recenzije mogu biti u JavaScript objektu
4. Koristite debug HTML fajlove koje scraper sprema

### Problem: CAPTCHA
**Rješenje:**
- Selenium scraper će čekati da riješite CAPTCHA
- Smanjite brzinu scrapinga (dodajte pauze)
- Koristite proxy za rotaciju IP-a

### Problem: ChromeDriver error
**Rješenje:**
```bash
# Linux
sudo apt-get install chromium-chromedriver

# Mac
brew install chromedriver

# Windows
# Download from: https://chromedriver.chromium.org/
```

---

## 🌐 Proxy Setup (Opciono)

Ako želite koristiti proxy za zaobilaženje geo-blokade:

### U `dianping_scraper.py`:
```python
USE_PROXY = True
PROXY_URL = "http://your-proxy:port"
```

### Besplatni proxy servisi:
- Proxyium: https://proxyium.com/
- Hide.me: https://hide.me/en/proxy
- KProxy: https://www.kproxy.com/

### Plaćeni proxy servisi (preporučeno):
- Bright Data (luminati.io)
- Oxylabs
- Smartproxy

---

## 📈 Analiza Podataka

Nakon izvlačenja recenzija, možete:

1. **Prevesti komentare:**
   - Google Translate API
   - DeepL
   - Manual translation service

2. **Sentiment analiza:**
   - Provjeriti pozitivne/negativne riječi
   - Identificirati najčešće pohvale/pritužbe
   - Analizirati trendove kroz vrijeme

3. **Competitive analysis:**
   - Usporediti sa konkurencijom
   - Pronaći competitive advantages
   - Identificirati područja za poboljšanje

4. **Report za gazdinu prezentaciju:**
   ```python
   # Kreirati summary statistics
   python3 -c "
   import json
   with open('dianping_reviews.json') as f:
       data = json.load(f)

   print(f'Ukupno recenzija: {len(data)}')
   ratings = [r['rating'] for r in data if r['rating']]
   print(f'Prosječna ocjena: {sum(ratings)/len(ratings):.2f}')
   "
   ```

---

## 🎓 Dodatni Resursi

### Dokumentacija:
- Dianping API (ako dostupna): https://open.dianping.com/
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/
- Selenium: https://selenium-python.readthedocs.io/

### Tutorials:
- Web Scraping with Python: https://realpython.com/python-web-scraping-practical-introduction/
- Selenium WebDriver: https://www.selenium.dev/documentation/

### Kineski marketing resursi:
- Dragon Trail: https://www.dragontrail.com/
- Jing Daily: https://jingdaily.com/

---

## 📞 Podrška

Ako naiđete na probleme:

1. Provjerite da li su svi paketi instalirani:
   ```bash
   pip install requests beautifulsoup4 selenium lxml
   ```

2. Pokrenite test:
   ```bash
   python3 -c "import requests, bs4, selenium; print('All packages OK!')"
   ```

3. Provjerite debug HTML fajlove koje scraper kreira

4. Pitajte za pomoć u GitHub Issues

---

## ✅ Checklist

- [ ] Odlučio sam koji pristup koristiti
- [ ] Instalirao sam potrebne pakete
- [ ] Testirao sam pristup Dianping-u
- [ ] Spremio sam HTML stranice (ako koristim Manual Extractor)
- [ ] Pokrenuo sam scraper
- [ ] Provjerio sam rezultate u JSON/CSV fajlovima
- [ ] Preveo sam komentare (opciono)
- [ ] Kreirao sam analitički report

---

## 🎉 Zaključak

Sa ovim alatima, možete izvući sve recenzije sa Dianping-a za vaše restorane.

**Preporučeni workflow:**

1. **Prvi pokušaj:** Testirajte `dianping_scraper.py` da vidite šta je dostupno
2. **Ako ne radi:** Koristite `dianping_selenium_scraper.py` sa ručnom prijavom
3. **Ako ni to ne radi:** Koristite `dianping_manual_extractor.py` pristup
4. **Dugoročno rješenje:** Angažirajte kinesku agenciju za redovno praćenje

Sretno sa scrapingom! 🚀
