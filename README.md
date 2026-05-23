# Sistrix SEO Drop Analyzer Pro 📉🚀

Ein interaktives Streamlit-Dashboard zur tiefgehenden Analyse von Sistrix-Keyword-Exporten. 
Dieses Tool geht über das reine Zählen von Rankings hinaus: Es bewertet Abstürze nach ihrem **echten Traffic-Verlust** (via CTR-Modell), berechnet den **monetären Impact** und identifiziert **Low Hanging Fruits** für schnelle SEO-Wins.

## ✨ Features

- **Robustes CSV-Parsing:** Frisst Sistrix-CSV-Exporte (Vergleiche) in allen gängigen Codierungen (UTF-8, Latin1, UTF-16) und Trennzeichen automatisch.
- **Traffic-Verlust Schätzung:** Nutzt ein klassisches Klickraten-Modell (CTR), um den echten Klickverlust zu schätzen (Platz 1 = 30%, Platz 2 = 15%, etc.).
- **Monetärer Impact (Traffic Value):** Multipliziert verlorene Klicks mit dem jeweiligen Keyword-CPC (Cost per Click), um das AdWords-Äquivalent in Euro darzustellen.
- **Strategische Dashboards:**
  - 📂 **Verzeichnis-Analyse:** Zeigt an, welche Website-Bereiche am meisten Traffic verloren haben.
  - 🍎 **Low Hanging Fruits:** Identifiziert Keywords, die knapp auf Seite 2 (Pos. 11-15) gerutscht sind und leicht zurückerobert werden können.
  - 🏆 **Gewinner:** Hebt neue Seite-1-Rankings hervor.
  - 📊 **Keyword-Veränderungen:** Übersichtliche Datentabellen aller Drops (Top 10, Seite 2, Komplette Index-Verluste) als Export-Grundlage.

## 🛠️ Installation

Das Projekt basiert auf Python 3.12+ und nutzt Streamlit.

1. Repository klonen:
```bash
git clone https://github.com/dein-username/sistrix-seo-analyzer.git
cd sistrix-seo-analyzer
```

2. Virtuelle Umgebung erstellen und Abhängigkeiten installieren:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## 🚀 Nutzung

1. Starte den lokalen Streamlit-Server:
```bash
streamlit run app.py
```
2. Öffne den angezeigten Link (standardmäßig `http://localhost:8501`) im Browser.
3. Lege in der linken Seitenleiste das alte und neue Datum deines Sistrix-Exports fest.
4. Lade deine `.csv` Datei hoch und klicke auf **Analysieren**.

## 📝 Benötigtes Sistrix-Format
Das Tool benötigt einen regulären Sistrix-Vergleichsexport (CSV) mit mindestens folgenden Spaltennamen:
- `Keyword`
- `Position#1` (Altes Datum)
- `Position#2` (Neues Datum)
- `Search Volume`
- `URL`
*(Optional, aber empfohlen für Deep Dives: `CPC` und `Competition`)*
