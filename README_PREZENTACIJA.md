# 📊 Vodič za Prezentacijske Materijale

## 🎯 Kreiran za: Genspark prezentaciju - Dojmovi gostiju po državama

---

## 📁 Novostvoreni Fajlovi za Prezentaciju

### 1. **analiza_dojmova_po_drzavama.md** ⭐ GLAVNI DOKUMENT
**Šta sadrži:**
- Detaljnu analizu TOP 15 država
- Profil gostiju za svaku državu (UK, USA, AUS, IRE, CAN, CRO, FRA, GER...)
- Ključne dojmove, stil komunikacije, preferencije hrane
- Sentiment analizu po državama
- Preporuke za marketing po državama
- Golden Insights i akcioni plan

**Kako koristiti:**
- Copy/paste sekcije direktno u Genspark
- Koristi emoji i formatiranje za vizuelni identitet
- Svakom državom ima svoju zastavu emoji

---

### 2. **country_insights_summary.csv** ⭐ BRZI PREGLED
**Šta sadrži:**
- Top 15 država u jednoj tabeli
- Key insights za svaku državu
- Marketing message za svaku
- Top prioriteti i preferiranje hrane

**Kako koristiti:**
- Idealan za dashboard vizualizacije
- Može se pretvoriti u tabelu u Gensparku
- Brzi reference za specifičnu državu

**Ključne kolone:**
- `country`, `total_reviews`, `pct_of_total`
- `sentiment_positive_pct`, `sentiment_negative_pct`
- `top_priority_1/2/3`, `top_food_1/2`
- `key_insight`, `marketing_message`

---

### 3. **country_preferences_matrix.csv** ⭐ POREĐENJE
**Šta sadrži:**
- Side-by-side poređenje UK, USA, AUS, IRE, CAN, CRO, FRA, GER
- 17 metrika po državama
- Key findings kolona

**Kako koristiti:**
- Perfektan za heat map vizualizacije
- Horizontal bar charts za poređenje
- Highlight razlike između država

**Ključne metrike:**
- Total Reviews, Avg Rating, Positive/Negative %
- View/Food/Service prioriteti
- Wait/Price complaints
- Steak vs Fish vs Seafood preference
- Wine mentions, Recommend count

---

### 4. **country_restaurant_ratings.csv** ⭐ RESTAURANT MATCH
**Šta sadrži:**
- Kako svaka država ocjenjuje svaki restoran
- Rating + Sentiment za sve 4 restorana
- Favorite restaurant po državi sa obrazloženjem

**Kako koristiti:**
- Identifikuj koji restoran za koju državu
- Target marketing strategije
- Match-making insights

**Primjeri:**
- Australija VOLI Arsenal (sentiment 0.835!)
- Kanada obožava Nautiku (sentiment 0.847)
- Hrvatska daje najviše ocene Panorami (4.92)

---

### 5. **cultural_segments.csv** ⭐ SEGMENTACIJA
**Šta sadrži:**
- 8 kulturoloških segmenata gostiju
- Grupacija država po sličnim karakteristikama
- Marketing approach za svaki segment

**8 Segmenata:**
1. **View Seekers** - UK, Croatia, Ireland
2. **Experience Hunters** - USA, Canada
3. **Quality Perfectionists** - Germany, Switzerland, France
4. **Balance Seekers** - Australia, Netherlands, Singapore
5. **People Connectors** - Ireland, Croatia locals
6. **Premium Loyalists** - Nautika lovers
7. **Value Conscious** - Finland, Spain
8. **Foodie Explorers** - USA, Australia, Singapore

**Kako koristiti:**
- Kreiraj personalized marketing campaigns
- Segment-based messaging
- Resource allocation po profitabilnosti

---

### 6. **wow_statistics.csv** ⭐ ATTENTION GRABBERS
**Šta sadrži:**
- 20 najimpresivnijih statistika
- "Wow factor" brojke za prezentaciju
- Kontekst i kako koristiti svaku statistiku

**Top WOW statistike:**
- 🇩🇪 Germany: 81.2% positive, 0% negative!
- 🇭🇷 Croatia: 0.6% negative (najniži!)
- 🇬🇧 UK: 2,563 "view" mentions (opsesija!)
- 🇦🇺 Arsenal+Australia: 0.835 sentiment (savršen match!)
- 🍷 UK Wine: 652 mentions (ljubitelji vina!)
- 🥩 UK Steak: 237 mentions (4x više od USA!)

**Kako koristiti:**
- Opening slide hooks
- Transition points u prezentaciji
- Social media quotes
- Infographic bullets

---

### 7. **presentation_key_slides.csv** ⭐ SLIDE GUIDE
**Šta sadrži:**
- 20 predloženih slajdova za prezentaciju
- Key message za svaki slajd
- Supporting data
- Visual suggestions (koje grafike koristiti)
- Color codes za svaki slajd

**Struktura prezentacije:**
- Slajdovi 1-3: Global overview
- Slajdovi 4-9: Top države detaljno
- Slajdovi 10-14: Restaurant & preference insights
- Slajdovi 15-17: Segmentacija i strategija
- Slajdovi 18-20: Akcije i next steps

**Kako koristiti:**
-Follow the flow 1-20 za kompletnu priču
- Svaki slajd ima vizuelni prijedlog
- Color codes za konzistentan dizajn

---

## 🎨 Kako Koristiti u Gensparku

### Opcija 1: Import CSV Files
1. Upload CSV fajlove u Genspark
2. Kreiraj charts/graphs automatski
3. Dodaj vizualizacije na slajdove

### Opcija 2: Copy/Paste from Markdown
1. Otvori `analiza_dojmova_po_drzavama.md`
2. Copy sekcije po državama
3. Paste u Genspark text fields
4. Formatiranje će se održati (emoji, bold, bullets)

### Opcija 3: Manual Design sa Data
1. Koristi `presentation_key_slides.csv` kao blueprint
2. Slijedi slide_title i key_message
3. Dodaj supporting_data iz drugih CSV-eva
4. Implementiraj visual_suggestions

---

## 📈 Preporučeni Chart/Graph Tipovi

### Za country_insights_summary.csv:
- **Bar chart**: Total reviews by country
- **Pie chart**: Percentage of total reviews
- **Sentiment heatmap**: Positive % by country (color-coded)

### Za country_preferences_matrix.csv:
- **Comparison table**: Side-by-side metrics
- **Horizontal bar charts**: Wait complaints, Food preferences
- **Stacked bar**: Positive vs Negative sentiment

### Za country_restaurant_ratings.csv:
- **Matrix heatmap**: Countries x Restaurants (sentiment color)
- **Grouped bar chart**: Ratings by restaurant per country
- **Scatter plot**: Rating vs Sentiment

### Za cultural_segments.csv:
- **Circular/pie diagram**: 8 segments with sizes
- **Bubble chart**: Segment size vs satisfaction
- **Network diagram**: Countries connected to segments

### Za wow_statistics.csv:
- **Infographic cards**: Individual stat highlights
- **Number callouts**: Big numbers with context
- **Icon-based**: Each stat with relevant icon

---

## 🚀 Quick Start Guide

### Za brzu prezentaciju (15 min):
1. **Slide 1**: Otvori `wow_statistics.csv` - Pick top 5 stats
2. **Slide 2-4**: Copy UK, USA, Australia sekcije iz `analiza_dojmova_po_drzavama.md`
3. **Slide 5**: Prikaži `cultural_segments.csv` kao 8-segment wheel
4. **Slide 6**: Zaključak iz "Actionable Insights"

### Za detaljnu prezentaciju (45 min):
1. Follow `presentation_key_slides.csv` strukturu (20 slajdova)
2. Combine sa detaljnim data iz drugih CSV-eva
3. Dodaj vizualizacije za svaki key point

### Za izvještaj/dokument:
1. Koristi `analiza_dojmova_po_drzavama.md` kao main body
2. Dodaj tabele iz CSV-eva kao appendix
3. Include wow_statistics kao executive summary

---

## 💡 Pro Tips za Genspark

### Vizualni Identitet:
- **Koristi zastave** - Emoji zastave za svaku državu
- **Color coding** - Follow color_code iz presentation_key_slides.csv
- **Icons** - Food icons, view icons, star ratings

### Data Storytelling:
1. Start sa WOW stat (hook)
2. Show global overview (context)
3. Deep dive po državama (details)
4. Cultural segments (patterns)
5. Actionable insights (conclusion)

### Emphasis Points:
- 🇩🇪 **Germany**: 81.2% positive - highlight u zelenom
- 🇭🇷 **Croatia**: 0.6% negative - highlight kao success
- 🇬🇧 **UK**: 29.6% volume - highlight kao main market
- 🇺🇸 **USA**: "Experience" factor - highlight differentiation

---

## 📊 Data Cross-Reference

Ako tražiš specifične podatke:

**Sentiment data**:
- `country_insights_summary.csv` (summary)
- `country_restaurant_ratings.csv` (by restaurant)
- `analiza_dojmova_po_drzavama.md` (detailed explanation)

**Food preferences**:
- `country_preferences_matrix.csv` (Steak/Fish/Seafood rows)
- `analiza_dojmova_po_drzavama.md` (Preferencije hrane sekcija)

**Complaints**:
- `country_preferences_matrix.csv` (Wait/Price rows)
- `analiza_dojmova_po_drzavama.md` (Pritužbe sekcija)

**Marketing messages**:
- `country_insights_summary.csv` (marketing_message kolona)
- `cultural_segments.csv` (marketing_approach kolona)
- `analiza_dojmova_po_drzavama.md` (Preporuke sekcija)

---

## ✨ Najvažniji Insights za Prezentaciju

### 1. **Kulturološke razlike su OGROMNE**
- UK: "lovely" iskustvo
- USA: "experience"
- Ireland: "friendly staff"
- France: "quality dishes"

### 2. **View je univerzalni faktor**
- Ali različite važnosti: UK (2,563) vs USA (674)

### 3. **Premium segment postoji**
- Canada, Germany, Sweden daju najviše ocene Nautici
- Sentiment 0.847-1.000

### 4. **Hrvatski gosti najzadovoljniji**
- 78.2% pozitivno, 0.6% negativno
- Lokalni ponos!

### 5. **8 različitih segmenata**
- Ne ciljaj sve isto - personaliziraj!

---

## 📧 Summary

Imaš **7 fajlova** sa kompletnom analizom dojmova gostiju po državama:

1. ✅ Detaljan markdown dokument (MD)
2. ✅ Quick reference CSV
3. ✅ Comparison matrix CSV
4. ✅ Restaurant ratings CSV
5. ✅ Cultural segments CSV
6. ✅ WOW statistics CSV
7. ✅ Presentation slides guide CSV

**Sve spremno za Genspark!** 🚀

---

*Kreirano: Novembar 2025*
*Dataset: 11,901 recenzija, 48+ država, 2014-2025*
