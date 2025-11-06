# Dianping Restaurant Review Scraper

🇨🇳 Kompletni sistem za izvlačenje recenzija sa Dianping.com (大众点评) za restorane u Dubrovniku.

## 🚀 Quick Start

```bash
# Osnovni scraper (testiranje)
python3 dianping_scraper.py

# Napredni scraper sa browser automatizacijom (preporučeno)
pip install selenium
python3 dianping_selenium_scraper.py

# Ručna ekstrakcija iz HTML fajlova (100% uspješno)
python3 dianping_manual_extractor.py
```

## 📁 Fajlovi

| Fajl | Opis |
|------|------|
| `dianping_scraper.py` | Osnovni HTTP scraper |
| `dianping_selenium_scraper.py` | Napredni scraper sa Selenium-om |
| `dianping_manual_extractor.py` | Ekstraktor za ručno spremljene HTML stranice |
| `DIANPING_SCRAPING_GUIDE.md` | Detaljne upute za korištenje |
| `DIANPING_RESULTS.md` | Rezultati i business insights |

## 🍽️ Restorani

✅ **Pronađeno na Dianping:**
- Gradska kavana Arsenal (189 recenzija, ¥305/osoba)
- Restaurant Panorama (224 recenzije, ¥253/osoba) 🥇
- Dubravka 1836 Restaurant & Cafe (153 recenzije, ¥234/osoba)

❌ **Nije pronađeno:**
- Restaurant Nautika (treba kreirati profil)

**Ukupno dostupnih recenzija:** 566

## 📖 Dokumentacija

Za detaljne upute, vidi:
- **[DIANPING_SCRAPING_GUIDE.md](DIANPING_SCRAPING_GUIDE.md)** - Kompletni tutorial
- **[DIANPING_RESULTS.md](DIANPING_RESULTS.md)** - Analiza rezultata

## 🔧 Installation

```bash
# Osnovni paketi
pip install requests beautifulsoup4 lxml

# Za Selenium scraper
pip install selenium
# + instalirajte ChromeDriver: https://chromedriver.chromium.org/
```

## 💡 Preporučeni Workflow

**Ako imate Dianping račun:**
1. Koristite `dianping_selenium_scraper.py`
2. Prijavite se ručno kada zatraženo
3. Automatski će izvući sve recenzije

**Ako nemate Dianping račun:**
1. Angažirajte nekoga sa računom da spremi HTML stranice
2. Koristite `dianping_manual_extractor.py`
3. 100% uspješnost garantirana

## 📊 Output Format

**JSON:**
```json
{
  "restaurant": "Restaurant Panorama",
  "reviewer": "张三",
  "rating": 4.5,
  "review_text": "非常好的餐厅...",
  "date": "2024-01-15"
}
```

**CSV:**
| restaurant | reviewer | rating | review_text | date |
|-----------|----------|--------|-------------|------|
| Panorama | 张三 | 4.5 | 非常好的餐厅... | 2024-01-15 |

## 🎯 Business Insights

- **Panorama** je najpopularniji među kineskim gostima (224 recenzije)
- Price point €30-€33 je optimalan za kineski segment
- Nautika treba kreirati Dianping profil - missed opportunity!

## 📞 Support

Za probleme sa instalacijom ili korištenjem, provjerite:
1. `DIANPING_SCRAPING_GUIDE.md` - Troubleshooting sekcija
2. Debug HTML fajlovi koji se automatski generiraju
3. GitHub Issues

## ⚖️ Legal Notice

Ovaj tool je kreiran za:
- Market research
- Customer feedback analizu
- Business intelligence

Poštujte:
- Dianping Terms of Service
- Rate limiting (pauze između zahtjeva)
- Privacy policies

---

**Status:** ✅ Spremno za korištenje
**Verzija:** 1.0
**Datum:** 2024-01-20
