# Sistrix Ranking Changes Analyzer

Ein interaktives, lokales Streamlit-Dashboard zur tiefgehenden Analyse von Sistrix-Keyword-Exporten. 
Dieses Tool geht weit über das reine Zählen von Rankings hinaus: Es bewertet Abstürze nach ihrem **echten Traffic-Verlust** (via CTR-Modell), berechnet den **monetären Impact**, clustert Keywords automatisch nach Themen und identifiziert **Low Hanging Fruits** für schnelle SEO-Wins.

---

## 🌟 Kern-Features

- **Robustes CSV-Parsing:** Frisst Sistrix-CSV-Exporte (Vergleiche) in allen gängigen Codierungen (UTF-8, Latin1, UTF-16) und Trennzeichen vollautomatisch.
- **🌍 Zweisprachiges UI:** Das gesamte Dashboard lässt sich mit einem Klick zwischen Deutsch und Englisch umschalten (inkl. Flaggen-Icons).
- **📊 Executive Summary & Marketing-Story:** Ein geteiltes Dashboard mit einer narrativen Zusammenfassung (Sie-Form) und kompakten, gestapelten KPI-Metriken auf der rechten Seite.
- **⚡ Quick-Jump Navigation:** Interaktive Buttons im Executive Summary leiten Nutzer mit sanftem Scrollen direkt zu den wichtigsten Datenbereichen (Top 3 Drops, Top 10 Drops, Low Hanging Fruits).
- **🎯 Automatische Search Intent Klassifizierung:** Clustert Suchanfragen für Deutsch und Englisch in `KNOW`, `DO (Transactional)`, `regional:CITY`, `regional:COUNTRY` und `undefined` zur präzisen Intent-Analyse.
- **🤖 KI-Freies NLP-Clustering:** Clustert tausende Verlierer-Keywords vollautomatisch und in Millisekunden in Themenbereiche (Head-Terms).
- **🎯 Intelligente Change-Metriken:** Taggt Keywords automatisch nach harten Ranking-Grenzen (`New`, `OoTop3`, `OoTop10`, `OoSERP2`, `OoTop100`, `IntoTop10`). Mikro-Schwankungen (< 1.0) werden sauber als `None` aussortiert.
- **Traffic-Verlust Schätzung:** Nutzt ein klassisches Klickraten-Modell (CTR), um den echten Traffic-Impact zu schätzen (Platz 1 = 30%, Platz 2 = 15%, etc.).
- **Monetärer Impact (Traffic Value):** Multipliziert verlorene Klicks mit dem jeweiligen Keyword-CPC, um das AdWords-Äquivalent in Euro darzustellen.
- **🎨 Premium Visual Loader:** Custom Lade-Overlay im MindBlow-Branding (Weinrot `#993333` Spinner mit weichem Hintergrund-Blur) für ein flüssiges Nutzererlebnis beim Tab-Wechsel.
- **📊 Interaktives KPI-Dashboard:** Zeigt direkt nach dem Upload den Netto-Traffic, die schlimmsten Top-3-Abstürze, Search-Intent-Verteilungen und die Performance deiner Themen-Cluster grafisch an.
- **⚙️ Git-basierte Versionierung:** Automatische Anzeige der Versionsnummer (Commit-Count) und des Git-Hashes im Footer.

---

## 📑 Aufbau der Analyse (Die 6 Tabs)

Sobald du deine Sistrix-Vergleichs-CSV hochgeladen hast, generiert die App 6 interaktive Analyse-Reiter:

1. **Verzeichnis-Analyse:** Zeigt visuell an, welche Website-Bereiche/Ordner am meisten Traffic verloren haben.
2. **Themen-Cluster:** Bündelt die Keyword-Verluste nach Begriffen. Erkennt sofort, ob ein bestimmtes Themenfeld (z.B. "Winterreifen") kollektiv abgestürzt ist. Du kannst gezielt Brand-Keywords herausfiltern.
3. **Ranking Drops:** Sortiert die Abstürze in priorisierte Kategorien (Top 3 Drops, Top 10 Drops, Seite 2 Drops, Komplette Verluste). Perfekt für Content-Rettungsaktionen. Inklusive Live-Textsuche.
4. **Low Hanging Fruits:** Identifiziert "Schwellen-Keywords", die knapp auf Seite 2 (Pos. 11-15) gerutscht sind. Mit leichten OnPage-Optimierungen holst du dir hier den massiven Traffic zurück.
5. **Gewinner:** Hebt neue Top-10-Rankings und Traffic-Gewinner hervor.
6. **Alle Daten:** Der ultimative Daten-Dump mit der neuen `Change`-Spalte und interaktiven Multiselect-Filtern (Cluster, Change-Typ, Verzeichnis). Ideal für den Export.

---

## ⚙️ Benötigtes Sistrix-Format

Das Tool benötigt einen regulären Sistrix-Vergleichsexport (CSV) mit mindestens folgenden Spaltennamen:
- `Keyword`
- `Position#1` (Altes Datum)
- `Position#2` (Neues Datum)
- `Search Volume`
- `URL`

*(Optional, aber sehr empfohlen für Deep Dives: `CPC` und `Competition`)*

---

## 🚀 Installation & Lokaler Start

Dieses Tool nutzt `streamlit` für das UI, `pandas` für die Datenverarbeitung und `plotly` für die Grafiken. Wir empfehlen die Nutzung des blitzschnellen Python-Managers `uv`.

**1. Repository klonen / Ordner öffnen**
Navigiere in deinem Terminal in den Projektordner.

**2. App starten (mit uv)**
Mit `uv` brauchst du keine manuellen virtuellen Umgebungen anlegen. Es installiert die Requirements on the fly und startet den Server in einer isolierten Umgebung:

```bash
uv run --python 3.12 --with-requirements requirements.txt streamlit run app.py
```

Das Terminal gibt dir nun eine lokale URL (meist `http://localhost:8501`). Öffne diese in deinem Browser.

---

## ☁️ Deployment auf der Streamlit Community Cloud

Das Projekt ist "Cloud Ready" und kann in wenigen Klicks kostenlos gehostet werden:
1. Pushe diesen Ordner (`app.py` und `requirements.txt`) in ein GitHub-Repository.
2. Melde dich auf [share.streamlit.io](https://share.streamlit.io) mit deinem GitHub-Account an.
3. Klicke auf **New app**, wähle das Repo und die `app.py` als Main File.
4. Klicke auf **Deploy**. Fertig!

---

## 📝 Lizenz & Credits

MIT License © 2026 Benjamin "SEOux Indianer" Wingerter 
Mitentwickelt von Antigravity (KI-Coding-Assistent von Google DeepMind)

Made with ❤️ in Munich & Bangkok: [seouxindianer.de](https://seouxindianer.de)
