import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from urllib.parse import urlparse
import io
import re
from collections import Counter
import base64
import time
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Sistrix Ranking Changes Analyzer",
    page_icon="assets/logo-head-clear.png",
    layout="wide"
)

# --- Load Brand Styles ---
try:
    with open("brand_style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Konnte brand_style.css nicht laden: {e}")

# --- i18n Language Setup ---
st.sidebar.image("assets/logo-horizontal.png", use_container_width=True)
st.sidebar.markdown("### Language / Sprache")
lang_choice = st.sidebar.radio("Select Language", options=["DE", "EN"], index=0, label_visibility="collapsed")
lang = "DE" if "DE" in lang_choice else "EN"

translations = {
    "EN": {
        "title": "Sistrix Ranking Changes Analyzer",
        "subtitle": "Upload your Sistrix comparison export and analyze keyword losses, traffic impact, and quick wins.",
        "sidebar_data": "1. Data & Settings",
        "upload_label": "Sistrix CSV Upload",
        "dates_header": "Dates for Charts",
        "date_old": "Date for Position#1 (Old)",
        "date_new": "Date for Position#2 (New)",
        "cluster_settings": "Clustering Settings",
        "brand_input": "Brand Keywords (comma-separated)",
        "brand_help": "Keywords containing these terms will be grouped into a 'Brand' cluster.",
        "cluster_count": "Number of Topic Clusters",
        "btn_analyze": "Analyze",
        "err_format": "Could not recognize the Sistrix format. Please check the file (columns 'Keyword' and 'Position#1' must exist exactly like this).",
        "err_read": "Error reading CSV: ",
        "err_req": "The following required columns are missing in the CSV: ",
        "succ_load": "File successfully loaded and analyzed!",
        "info_upload": "Please upload a Sistrix CSV file and click 'Analyze'.",
        
        "kpi_header": "Overview: Business Impact",
        "kpi_lost_total_sv": "Lost Search Volume (Total)",
        "kpi_gained_total_sv": "Gained Search Volume (Total)",
        "kpi_net_change_sv": "Net Search Volume Change",
        "kpi_avg_pos_change": "Avg. Position Change",
        "dir_chart_title_sv": "Which directories lost the most search volume?",
        "dir_chart_label_t_sv": "Lost Search Volume",
        "cl_chart_title_sv": "Which topic clusters lost the most search volume?",
        "cl_chart_label_t_sv": "Lost Search Volume",
        "kpi_lost_total": "Lost Traffic (Total)",
        "kpi_value_total": "Monetary Loss (AdWords Equivalent)",
        "kpi_gained_total": "Gained Traffic (Total)",
        "kpi_net_change": "Net Traffic Change",
        "kpi_top3_drops": "Top 3 Drops",
        "kpi_top10_drops": "Top 10 Drops",
        "kpi_total_loss": "Complete Losses",
        "kpi_total_loss_help": "Keywords that fell out of the Top 100 completely.",
        "kpi_lhf": "Low Hanging Fruits",
        "kpi_lhf_link": "See tab below",
        "kpi_lhf_help": "Actual search volume of keywords ranking on positions 11-15. High search volume here means great potential if pushed to page 1.",
        "kpi_cluster_title": "Topic Cluster Performance",
        "kpi_best_cluster": "Best Cluster",
        "kpi_worst_cluster": "Worst Cluster",
        "kpi_top3_title": "Top 3 Drops (Worst 5)",
        
        "tab_dir": "Directory Analysis",
        "tab_cluster": "Topic Clusters",
        "tab_drops": "Ranking Drops",
        "tab_lhf": "Low Hanging Fruits",
        "tab_winners": "Winners",
        "tab_all": "All Data",
        
        "dir_sub": "Lost Traffic & Value by Directory",
        "dir_empty": "No data available.",
        "dir_chart_title": "Which directories cost us the most traffic?",
        "dir_chart_label_d": "Directory",
        "dir_chart_label_t": "Lost Traffic (Estimated)",
        
        "cl_sub": "Traffic Loss by Topic Clusters",
        "cl_desc": "Automatic grouping of losing keywords by their most frequent head terms.",
        "cl_chart_title": "Which topic clusters lost the most traffic?",
        "cl_chart_label_c": "Topic Cluster",
        "cl_chart_label_t": "Lost Traffic (Estimated)",
        "cl_detail": "#### Detail Data per Cluster",
        "cl_select": "Select one or multiple clusters for detail insights:",
        "cl_sum": "Total affected search volume in selected clusters:",
        "cl_empty": "No drops available for clustering.",
        "cl_other": "Other",
        
        "rd_sub": "Ranking Drops Overview",
        "rd_filter": "Filter by keyword (optional):",
        "rd_t3_title": "#### 1. Top 3 Drops (Ranking losses starting in Top 3)",
        "rd_t3_empty": "No Top 3 Drops found.",
        "rd_t10_title": "#### 2. Top 10 Drops (Ranking losses starting in Top 10)",
        "rd_t10_empty": "No Top 10 Drops found.",
        "rd_p2_title": "#### 3. Page 2 Drops (Ranking losses starting on Page 2)",
        "rd_p2_empty": "No Page 2 Drops found.",
        "rd_100_title": "#### 4. Complete Losses (Fell out of Top 100)",
        "rd_100_empty": "No keywords fell out of Top 100.",
        "rd_sum_vol": "Affected Search Volume:",
        "rd_sum_traf": "(Estimated Traffic Loss:",
        
        "lhf_sub": "Low Hanging Fruits (Position 11 - 15)",
        "lhf_desc": "These keywords currently rank on the top half of page 2 (Position 11-15) and already generate the real search volume shown above. With tiny on-page optimizations, you can push these over the threshold to page 1 and turn those impressions into massive traffic.",
        "lhf_empty": "No keywords found in range 11-15.",
        
        "win_sub": "Winners (New in Top 10)",
        "win_empty": "No new rankings in Top 10.",
        "win_chart_title": "Winner Keywords by Search Volume",
        "win_chart_label_pos": "New Position",
        
        "ad_sub": "All Data (Complete Export)",
        "ad_filter_cluster": "Filter by Cluster",
        "ad_filter_change": "Filter by Change Type",
        "ad_filter_dir": "Filter by Directory",
        "ad_filter_kw": "Search Keyword",
        "ad_filter_intent": "Filter by Search Intent",
        "data_lang": "Data Language (for Search Intent)",
        "data_lang_options": ["German", "English", "Other"],
        "data_lang_help": "Select the language of your keyword data to correctly determine search intent (KNOW, DO, regional). If 'Other' is selected, search intent analysis is skipped.",
        "intent_not_analyzed_msg": "Search intent analysis was skipped because data language is set to 'Other'.",
        "intent_not_analyzed": "Not Analyzed",
        "kpi_intent_title": "Search Intent Distribution",
        "traffic": "Traffic",
        "footer": "MIT License &copy; 2026 Benjamin &quot;SEOux Indianer&quot; Wingerter | Created in Munich & Bangkok with ❤️ | <a href='https://seouxindianer.de' target='_blank' style='color: #2ea3f2; text-decoration: underline;'>seouxindianer.de</a> | Co-developed with Antigravity",
        "legal_header": "Legal & Privacy Policy",
        "imprint_body": """### Imprint

**Information pursuant to § 5 DDG:**
Benjamin Wingerter
SEOux Indianer
Email: mytools.sistrixrankingchanges@mindblowmedia.com
Website: seouxindianer.de

**Disclaimer:**
The contents of this app were created with the utmost care. However, we cannot guarantee the correctness, completeness, or topicality of the content.""",
        "privacy_body": """### Privacy Policy

**1. General Information**
This privacy policy informs you about the nature, scope, and purpose of the processing of personal data within this web application.

**2. Data Controller**
Benjamin Wingerter
Email: mytools.sistrixrankingchanges@mindblowmedia.com

**3. Hosting (Streamlit Cloud)**
This app is hosted on Streamlit Community Cloud, a service provided by Snowflake Inc. (106 East Babcock Street, Suite 3A, Bozeman, MT 59715, USA). To serve the app securely, Snowflake processes connection logs and IP addresses of visitors. This processing is based on our legitimate interest in a secure and efficient operation of the application (Art. 6 (1) (f) GDPR). For more details, please refer to the Snowflake Privacy Policy.

**4. Processing of Uploaded Files (CSV)**
When you upload a Sistrix export file:
- The file is processed **exclusively in the transient memory (RAM)** of the server to generate dashboards.
- The uploaded data is **never stored permanently on any storage drive or database**.
- As soon as you terminate your session (e.g., by closing the browser tab, reloading the page, or replacing the file), all processed data is completely erased.
- The legal basis for this processing is Art. 6 (1) (f) GDPR (our legitimate interest in providing you with this analysis tool).

**5. Your Rights**
You have the right to access, rectify, erase, or restrict the processing of your personal data, as well as the right to data portability and objection.""",
    },
    "DE": {
        "title": "Sistrix Ranking Changes Analyzer",
        "subtitle": "Lade deinen Sistrix-Vergleichsexport hoch und analysiere Keyword-Verluste, Traffic-Impact und Quick Wins.",
        "sidebar_data": "1. Daten & Einstellungen",
        "upload_label": "Sistrix CSV Upload",
        "dates_header": "Datumsangaben für die Diagramme",
        "date_old": "Datum für Position#1 (Alt)",
        "date_new": "Datum für Position#2 (Neu)",
        "cluster_settings": "Clustering Einstellungen",
        "brand_input": "Brand-Keywords (kommagetrennt)",
        "brand_help": "Keywords, die diese Begriffe enthalten, werden in einem eigenen 'Brand' Cluster gesammelt.",
        "cluster_count": "Anzahl der Themen-Cluster",
        "btn_analyze": "Analysieren",
        "err_format": "Konnte das Sistrix-Format nicht erkennen. Bitte prüfe die Datei (Spaltennamen 'Keyword' und 'Position#1' müssen exakt so existieren).",
        "err_read": "Fehler beim Lesen der CSV: ",
        "err_req": "Die folgenden benötigten Spalten fehlen in der CSV: ",
        "succ_load": "Datei erfolgreich geladen und analysiert!",
        "info_upload": "Bitte lade eine Sistrix CSV-Datei hoch und klicke auf 'Analysieren'.",
        
        "kpi_header": "Überblick: Business Impact",
        "kpi_lost_total_sv": "Verlorenes Suchvolumen (Gesamt)",
        "kpi_gained_total_sv": "Gewonnenes Suchvolumen (Gesamt)",
        "kpi_net_change_sv": "Netto Suchvolumen-Veränderung",
        "kpi_avg_pos_change": "Ø Positions-Veränderung",
        "dir_chart_title_sv": "Welche Verzeichnisse haben am meisten Suchvolumen verloren?",
        "dir_chart_label_t_sv": "Verlorenes Suchvolumen",
        "cl_chart_title_sv": "Welche Themen-Cluster haben am meisten Suchvolumen verloren?",
        "cl_chart_label_t_sv": "Verlorenes Suchvolumen",
        "kpi_lost_total": "Verlorener Traffic (Schätzung)",
        "kpi_value_total": "Monetärer Verlust (AdWords-Äquivalent)",
        "kpi_gained_total": "Gewonnener Traffic (Schätzung)",
        "kpi_net_change": "Netto Traffic-Veränderung",
        "kpi_top3_drops": "Top 3 Abstürze",
        "kpi_top10_drops": "Top 10 Abstürze",
        "kpi_total_loss": "Komplette Verluste",
        "kpi_total_loss_help": "Keywords, die komplett aus den Top 100 gefallen sind.",
        "kpi_lhf": "Low Hanging Fruits",
        "kpi_lhf_link": "Siehe Reiter unten",
        "kpi_lhf_help": "Das komplette Suchvolumen, das diese Keywords im aktuellen Zeitraum auf den Positionen 11-15 sammeln. Ein hohes Suchvolumen hier bedeutet hohes Potenzial für Seite 1.",
        "kpi_cluster_title": "Themen-Cluster Performance",
        "kpi_best_cluster": "Bestes Cluster",
        "kpi_worst_cluster": "Schlechtestes Cluster",
        "kpi_top3_title": "Top 3 Abstürze (Die 5 schlimmsten)",
        "traffic": "Traffic",
        
        "tab_dir": "Verzeichnis-Analyse",
        "tab_cluster": "Themen-Cluster",
        "tab_drops": "Ranking Drops",
        "tab_lhf": "Low Hanging Fruits",
        "tab_winners": "Gewinner",
        "tab_all": "Alle Daten",
        
        "dir_sub": "Verlorener Traffic & Wert nach Verzeichnis",
        "dir_empty": "Keine Daten vorhanden.",
        "dir_chart_title": "Welche Verzeichnisse kosten uns am meisten Traffic?",
        "dir_chart_label_d": "Verzeichnis",
        "dir_chart_label_t": "Verlorene Klicks (Schätzung)",
        
        "cl_sub": "Traffic-Verlust nach Themen-Clustern",
        "cl_desc": "Automatische Bündelung der Verlierer-Keywords nach den häufigsten Begriffen (Head-Terms).",
        "cl_chart_title": "Welche Themen-Cluster haben am meisten Traffic verloren?",
        "cl_chart_label_c": "Themen-Cluster",
        "cl_chart_label_t": "Verlorener Traffic (Schätzung)",
        "cl_detail": "#### Detail-Daten pro Cluster",
        "cl_select": "Wähle ein oder mehrere Cluster für Detail-Insights:",
        "cl_sum": "Gesamtes betroffenes Suchvolumen in den gewählten Clustern:",
        "cl_empty": "Keine Abstürze zum Clustern vorhanden.",
        "cl_other": "Sonstiges",
        
        "rd_sub": "Alle Abstürze in der Übersicht",
        "rd_filter": "Nach Keyword filtern (optional):",
        "rd_t3_title": "#### 1. Top 3 Abstürze (Ranking-Verluste aus den Top 3)",
        "rd_t3_empty": "Keine Top 3 Drops gefunden.",
        "rd_t10_title": "#### 2. Top 10 Abstürze (Ranking-Verluste aus den Top 10)",
        "rd_t10_empty": "Keine Top 10 Drops gefunden.",
        "rd_p2_title": "#### 3. Seite 2 Abstürze (Ranking-Verluste von Seite 2)",
        "rd_p2_empty": "Keine Seite 2 Drops gefunden.",
        "rd_100_title": "#### 4. Komplette Verluste (Aus Top 100 gefallen)",
        "rd_100_empty": "Keine Keywords aus den Top 100 gefallen.",
        "rd_sum_vol": "Angezeigtes Suchvolumen:",
        "rd_sum_traf": "(Geschätzter Traffic-Verlust:",
        
        "lhf_sub": "Low Hanging Fruits (Position 11 - 15)",
        "lhf_desc": "Diese sogenannten **Schwellen-Keywords** ranken aktuell auf der oberen Hälfte von Seite 2 (Position 11-15) und generieren dort bereits das angezeigte Suchvolumen. Das bedeutet: Das Suchvolumen ist da! Mit winzigen inhaltlichen Optimierungen kannst du diese Keywords über die Schwelle auf Seite 1 schieben und das Suchvolumen in massiven Traffic verwandeln.",
        "lhf_empty": "Keine Keywords im Bereich 11-15 gefunden.",
        
        "win_sub": "Gewinner (Neu in den Top 10)",
        "win_empty": "Keine neuen Rankings in den Top 10.",
        "win_chart_title": "Gewinner-Keywords nach Suchvolumen",
        "win_chart_label_pos": "Neue Position",
        
        "ad_sub": "Alle Daten (Gesamter Export)",
        "ad_filter_cluster": "Nach Cluster filtern",
        "ad_filter_change": "Nach Change-Typ filtern",
        "ad_filter_dir": "Nach Verzeichnis filtern",
        "ad_filter_kw": "Keyword suchen",
        "ad_filter_intent": "Nach Suchintent filtern",
        "data_lang": "Daten-Sprache (für Suchintent)",
        "data_lang_options": ["Deutsch", "English", "Andere"],
        "data_lang_help": "Wähle die Sprache Deiner Keyword-Daten aus, um den Suchintent (KNOW, DO, regional) korrekt zu bestimmen. Wenn 'Andere' gewählt wird, wird keine Suchintent-Analyse durchgeführt.",
        "intent_not_analyzed_msg": "Die Suchintent-Analyse wurde übersprungen, da die Daten-Sprache auf 'Andere' eingestellt ist.",
        "intent_not_analyzed": "Nicht analysiert",
        "kpi_intent_title": "Suchintents-Verteilung",
        "footer": "MIT License &copy; 2026 Benjamin &quot;SEOux Indianer&quot; Wingerter | Erstellt in München & Bangkok mit ❤️ | <a href='https://seouxindianer.de' target='_blank' style='color: #2ea3f2; text-decoration: underline;'>seouxindianer.de</a> | Mitentwickelt von Antigravity",
        "legal_header": "Rechtliches / Impressum",
        "imprint_body": """### Impressum

**Angaben gemäß § 5 DDG:**
Benjamin Wingerter
SEOux Indianer
E-Mail: mytools.sistrixrankingchanges@mindblowmedia.com
Website: seouxindianer.de

**Haftungsausschluss (Disclaimer):**
Die Inhalte dieser App wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen.""",
        "privacy_body": """### Datenschutzerklärung

**1. Allgemeine Hinweise**
Diese Datenschutzerklärung klärt Sie über die Art, den Umfang und Zweck der Verarbeitung von personenbezogenen Daten innerhalb dieser Webanwendung (App) auf.

**2. Verantwortlicher**
Benjamin Wingerter
E-Mail: mytools.sistrixrankingchanges@mindblowmedia.com

**3. Hosting (Streamlit Cloud)**
Diese App wird auf der Streamlit Community Cloud gehostet, einem Dienst von Snowflake Inc. (106 East Babcock Street, Suite 3A, Bozeman, MT 59715, USA). Zur Bereitstellung und zum sicheren Betrieb der App verarbeitet Snowflake Verbindungsdaten und IP-Adressen der Besucher. Die Übermittlung erfolgt auf Grundlage unserer berechtigten Interessen an einem sicheren und effizienten Betrieb des Dienstes (Art. 6 Abs. 1 lit. f DSGVO). Weitere Details finden Sie in der Datenschutzerklärung von Snowflake.

**4. Verarbeitung von hochgeladenen Dateien (CSV)**
Wenn Sie eine Sistrix Exportdatei hochladen:
- Die Datei wird **ausschließlich im Arbeitsspeicher (RAM)** des Servers verarbeitet, um die Auswertungen zu berechnen.
- Die hochgeladenen Daten werden **zu keinem Zeitpunkt dauerhaft auf Datenträgern oder in einer Datenbank gespeichert**.
- Sobald Sie Ihre Sitzung beenden (z. B. durch Schließen des Browsers, Neuladen der Seite oder Ändern der Upload-Datei), werden die verarbeiteten Daten vollständig gelöscht.
- Die Rechtsgrundlage für diese Verarbeitung ist Art. 6 Abs. 1 lit. f DSGVO (unser berechtigtes Interesse, Ihnen diese Analysefunktionalität anzubieten).

**5. Ihre Rechte**
Sie haben das Recht auf Auskunft, Berichtigung, Löschung und Einschränkung der Verarbeitung Ihrer personenbezogenen Daten sowie das Recht auf Datenübertragbarkeit und Widerspruch.""",
    }
}

t = translations[lang]

# Helper to format numbers based on selected language (DE: 1.234.567,89 / EN: 1,234,567.89)
def format_num(val, decimal_places=0):
    if pd.isnull(val):
        return ""
    formatted_str = f"{val:,.{decimal_places}f}"
    if lang == "DE":
        placeholder = "|||"
        temp = formatted_str.replace(",", placeholder)
        temp = temp.replace(".", ",")
        formatted_str = temp.replace(placeholder, ".")
    return formatted_str

# Helper to style Plotly figures according to Corporate Design
def style_plotly_fig(fig):
    title_text = ""
    if fig.layout.title is not None:
        if isinstance(fig.layout.title, str):
            title_text = fig.layout.title
        elif hasattr(fig.layout.title, 'text') and fig.layout.title.text is not None:
            title_text = fig.layout.title.text

    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font_family="Raleway",
        font_color="#232323",
        margin=dict(l=60, r=40, t=45, b=45),  # Safe default margins to avoid clipping
        title=dict(
            text=title_text,
            font=dict(family="Raleway", color="#232323", size=15)
        ),
        xaxis=dict(
            title=dict(text=""),  # Suppress default x-axis title to avoid "undefined" text
            gridcolor="#dfdfdf",
            zerolinecolor="#dfdfdf",
            linecolor="#dfdfdf",
            tickfont=dict(family="Open Sans", color="#535353")
        ),
        yaxis=dict(
            title=dict(text=""),  # Suppress default y-axis title to avoid "undefined" text
            gridcolor="#dfdfdf",
            zerolinecolor="#dfdfdf",
            linecolor="#dfdfdf",
            tickfont=dict(family="Open Sans", color="#535353")
        )
    )
    return fig

st.title(t["title"])
st.markdown(t["subtitle"])

# --- Custom Loading Overlay ---
loading_placeholder = st.empty()

if st.session_state.get("show_custom_loader"):
    logo_base64 = ""
    try:
        with open("assets/logo-head-clear.png", "rb") as image_file:
            logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    except Exception:
        pass
        
    custom_loader_html = f"""<div class="custom-loader-overlay">
    <div class="loader-logo-container">
        <img class="loader-logo" src="data:image/png;base64,{logo_base64}" />
        <svg class="loader-svg" viewBox="0 0 100 100">
            <circle class="loader-bg-circle" cx="50" cy="50" r="45" />
            <circle class="loader-fill-circle" cx="50" cy="50" r="45" />
        </svg>
    </div>
</div>
<style>
.custom-loader-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(35, 35, 35, 0.15);
    backdrop-filter: blur(2px);
    z-index: 999999;
    display: flex;
    justify-content: center;
    align-items: center;
    pointer-events: all;
}}
.loader-logo-container {{
    position: relative;
    width: 140px;
    height: 140px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #ffffff;
    border-radius: 50%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}}
.loader-logo {{
    width: 80px;
    height: 80px;
    object-fit: contain;
    z-index: 1;
}}
.loader-svg {{
    position: absolute;
    top: 0;
    left: 0;
    width: 140px;
    height: 140px;
    z-index: 2;
}}
.loader-bg-circle {{
    fill: none;
    stroke: rgba(153, 51, 51, 0.05);
    stroke-width: 6;
}}
.loader-fill-circle {{
    fill: none;
    stroke: rgba(153, 51, 51, 0.7);
    stroke-width: 6;
    stroke-linecap: round;
    stroke-dasharray: 283;
    stroke-dashoffset: 283;
    animation: fill-progress 1.5s ease-in-out infinite alternate, rotate-spinner 2s linear infinite;
    transform-origin: center;
}}
@keyframes fill-progress {{
    0% {{
        stroke-dashoffset: 283;
    }}
    100% {{
        stroke-dashoffset: 28;
    }}
}}
@keyframes rotate-spinner {{
    0% {{
        transform: rotate(0deg);
    }}
    100% {{
        transform: rotate(360deg);
    }}
}}
</style>"""
    loading_placeholder.markdown(custom_loader_html, unsafe_allow_html=True)
    time.sleep(1.2)

# Sidebar - Settings
st.sidebar.header(t["sidebar_data"])

uploaded_file = st.sidebar.file_uploader(t["upload_label"], type=["csv"])

st.sidebar.subheader(t["dates_header"])
date_old = st.sidebar.date_input(t["date_old"], value=pd.to_datetime('today') - pd.DateOffset(months=1))
date_new = st.sidebar.date_input(t["date_new"], value=pd.to_datetime('today'))

st.sidebar.subheader(t["cluster_settings"])
brand_input = st.sidebar.text_input(t["brand_input"], value="", help=t["brand_help"])
num_clusters = st.sidebar.slider(t["cluster_count"], min_value=5, max_value=50, value=20, step=5)
data_lang_choice = st.sidebar.selectbox(
    t["data_lang"], 
    options=t["data_lang_options"], 
    index=0,
    help=t["data_lang_help"]
)

metric_basis = "SV"

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

if uploaded_file is not None:
    if st.sidebar.button(t["btn_analyze"], type="primary"):
        st.session_state['analyzed'] = True

# Sidebar - Legal Disclosures
st.sidebar.markdown("---")
with st.sidebar.expander(t["legal_header"]):
    st.markdown(t["imprint_body"])
    st.markdown("---")
    st.markdown(t["privacy_body"])

# Helper function for CTR calculation
def estimate_ctr(pos):
    # Standard SEO CTR Model
    ctr_map = {1: 0.30, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05, 6: 0.04, 7: 0.03, 8: 0.02, 9: 0.015, 10: 0.01}
    return ctr_map.get(pos, 0.0)

if uploaded_file is not None and st.session_state['analyzed']:
    # Read the data robustly
    try:
        content = uploaded_file.getvalue()
        df = None
        
        for enc in ['utf-8', 'utf-16', 'latin1', 'utf-8-sig']:
            for sep in ['\t', ';', ',']:
                for skip in [0, 1, 2, 3, 4, 5]:
                    try:
                        temp_df = pd.read_csv(io.BytesIO(content), encoding=enc, sep=sep, skiprows=skip, on_bad_lines='skip')
                        temp_df.columns = [str(c).strip().strip('"').strip("'") for c in temp_df.columns]
                        
                        if 'Keyword' in temp_df.columns and 'Position#1' in temp_df.columns:
                            df = temp_df
                            break
                    except Exception:
                        continue
                if df is not None:
                    break
            if df is not None:
                break
                
        if df is None:
            raise Exception(t["err_format"])
             
    except Exception as e:
        st.error(f"{t['err_read']} {e}")
        st.stop()
        
    st.success(t["succ_load"])
    
    req_cols = ["Keyword", "Position#1", "Position#2", "Search Volume", "URL"]
    missing_cols = [col for col in req_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"{t['err_req']} {missing_cols}")
        st.write("Vorhandene Spalten:", df.columns.tolist())
        st.stop()
        
    # --- Data Cleaning ---
    if df['Search Volume'].dtype == 'object':
        df['Search Volume'] = df['Search Volume'].astype(str).str.replace('.', '', regex=False).str.replace(',', '', regex=False)
    df['Search Volume'] = pd.to_numeric(df['Search Volume'], errors='coerce').fillna(0)
    
    if 'CPC' in df.columns:
        if df['CPC'].dtype == 'object':
            df['CPC'] = df['CPC'].astype(str).str.replace(',', '.', regex=False)
        df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce').fillna(0.0)
    else:
        df['CPC'] = 0.0

    if 'Competition' in df.columns:
        if df['Competition'].dtype == 'object':
            df['Competition'] = df['Competition'].astype(str).str.replace(',', '.', regex=False)
        df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce').fillna(0.0)
    else:
        df['Competition'] = 0.0
    
    for col in ['Position#1', 'Position#2']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(101)
        df[col] = df[col].replace(0, 101)
        
    def get_first_directory(url):
        try:
            path = urlparse(str(url)).path
            parts = path.strip('/').split('/')
            if len(parts) > 0 and parts[0] != '':
                return f"/{parts[0]}/"
            return "/"
        except:
            return "Unbekannt"
            
    df['Directory'] = df['URL'].apply(get_first_directory)
    
    # --- Advanced Analytics Logic ---
    df['Traffic#1'] = df['Search Volume'] * df['Position#1'].apply(estimate_ctr)
    df['Traffic#2'] = df['Search Volume'] * df['Position#2'].apply(estimate_ctr)
    df['Traffic Loss'] = df['Traffic#1'] - df['Traffic#2']
    df['Traffic Gain'] = df['Traffic#2'] - df['Traffic#1']
    df['Lost Value €'] = df['Traffic Loss'].clip(lower=0) * df['CPC']
    df['Position Change'] = df['Position#1'] - df['Position#2']
    df['Traffic Change'] = df['Traffic#2'] - df['Traffic#1']
    
    # Dynamic Metric Calculations
    if metric_basis == "Clicks":
        df['Metric Loss'] = df['Traffic Loss'].clip(lower=0)
        df['Metric Gain'] = df['Traffic Gain'].clip(lower=0)
        df['Metric Change'] = df['Traffic Change']
        metric_unit = "Klicks" if lang == "DE" else "clicks"
    else:
        # Search Volume mode
        df['Metric Loss'] = 0.0
        df.loc[df['Position Change'] < 0, 'Metric Loss'] = df['Search Volume']
        df['Metric Gain'] = 0.0
        df.loc[df['Position Change'] > 0, 'Metric Gain'] = df['Search Volume']
        df['Metric Change'] = df['Metric Gain'] - df['Metric Loss']
        metric_unit = "SV"

    # Ranking-Veränderung Statistiken
    gained_keywords_count = int((df['Position Change'] > 0).sum())
    lost_keywords_count = int((df['Position Change'] < 0).sum())
    avg_gain_pos = df[df['Position Change'] > 0]['Position Change'].mean()
    if pd.isnull(avg_gain_pos): avg_gain_pos = 0.0
    avg_loss_pos = abs(df[df['Position Change'] < 0]['Position Change'].mean())
    if pd.isnull(avg_loss_pos): avg_loss_pos = 0.0
    avg_pos_change = df['Position Change'].mean()
    if pd.isnull(avg_pos_change): avg_pos_change = 0.0
    
    gained_keywords_sv = df[df['Position Change'] > 0]['Search Volume'].sum()
    lost_keywords_sv = df[df['Position Change'] < 0]['Search Volume'].sum()
    total_sv = df['Search Volume'].sum()
    
    def get_change_type(row):
        po = row['Position#1']
        pn = row['Position#2']
        if po == 101 and pn != 101: return "New"
        elif po <= 3 and pn > 3: return "OoTop3"
        elif po <= 10 and pn > 10: return "OoTop10"
        elif 10 < po <= 20 and pn > 20: return "OoSERP2"
        elif po <= 100 and pn > 100: return "OoTop100"
        elif po > 10 and pn <= 10: return "IntoTop10"
        elif abs(po - pn) < 1.0: return "None"
        else: return "Changed"
    df['Change'] = df.apply(get_change_type, axis=1)
    
    # --- Clustering Logic ---
    stopwords_de = set([
        "und", "oder", "kaufen", "test", "erfahrung", "erfahrungen", "günstig", "online", "shop", 
        "mit", "für", "von", "in", "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", 
        "eines", "auf", "im", "am", "zu", "ist", "sind", "wie", "was", "wo", "wer", "warum", "als", "an",
        "bei", "aus", "nach", "um", "bis", "über", "unter", "vor", "zwischen", "aber", "nur", "auch",
        "dass", "dann", "wenn", "so", "sich", "nicht", "noch", "mehr", "durch", "zum", "zur"
    ])
    stopwords_en = set([
        "and", "or", "buy", "test", "experience", "cheap", "online", "shop", "with", "for", "of", "in",
        "the", "a", "an", "on", "at", "to", "is", "are", "how", "what", "where", "who", "why", "as",
        "from", "after", "about", "under", "before", "between", "but", "only", "also", "that", "then",
        "if", "so", "not", "more", "by"
    ])
    stopwords = stopwords_en if lang == "EN" else stopwords_de
    brand_terms = [b.strip().lower() for b in brand_input.split(',')] if brand_input.strip() else []
    
    def get_cluster(kw):
        kw_lower = str(kw).lower()
        for b in brand_terms:
            if b and b in kw_lower:
                return "Brand"
        return None

    df['Cluster'] = df['Keyword'].apply(get_cluster)
    
    temp_losers = df[df['Traffic Loss'] > 0]
    non_brand_kws = temp_losers[temp_losers['Cluster'].isnull()]['Keyword'].dropna().tolist()
    
    word_counts = Counter()
    for kw in non_brand_kws:
        words = re.findall(r'\b\w+\b', str(kw).lower())
        for w in words:
            if w not in stopwords and len(w) > 2 and not w.isnumeric():
                word_counts[w] += 1
                
    top_head_terms = [word for word, count in word_counts.most_common(num_clusters)]
    
    def assign_head_term(kw):
        kw_lower = str(kw).lower()
        for term in top_head_terms:
            if re.search(rf'\b{re.escape(term)}\b', kw_lower):
                return term.capitalize()
        return "undefined"
        
    df.loc[df['Cluster'].isnull(), 'Cluster'] = df[df['Cluster'].isnull()]['Keyword'].apply(assign_head_term)
    
    def get_intent(kw):
        kw_lower = str(kw).lower()
        intents = []
        if data_lang_choice == t["data_lang_options"][0]:
            # User Intent: KNOW
            if re.search(r'((.*\s|^)w(er|em|en|essen|ie|ann|o|elche|as|obei|omit|oran|orin|ohin|obei|eshalb|arum|ieso|orauf|orum|ovor|ogegen|odurch|oher|eswegen|oraus)\s.*)|((.*\s|^)anleitung|anweisung|beschreibung|bestimmung|bin ich|definition|erklärung|forum|frage|gesetz|guide|(.*\s|^)hilfe|how to|muss|kann(\s.*|$)|(.*\s|^)darf|methode|quora|rechtlich|regeln|tipps|tutorial|brauche|vor was|walkthrough|diy|yahoo clever|gute frage)(\s.*|$)', kw_lower):
                intents.append("KNOW")
                
            # User Intent: DO (Transactional)
            if re.search(r'.*aktionen.*|.*am billigsten.*|.*anfordern.*|.*angebot.*|.*anmeldung.*|.*auf lager.*|.*bestellbar.*|.*bestellen.*|.*billig.*|.*coupon.*|.*discount.*|.*download.*|.*free.*|.*garantie.*|.*gebraucht.*|.*gewinnen.*|.*gewinnspiel.*|.*gratis.*|.*günstig.*|.*günstige.*|.*günstiges.*|.*günstigste.*|.*günstigste.*|.*gutschein.*|.*gutscheincode.*|.*im angebot.*|.*in stock.*|.*kaufen.*|.*kaufen.*|.*käuflich.*|.*kontakt.*|.*kostenlos.*|.*leihen.*|.*mieten.*|.*mit kreditkarte.*|.*mit paypal.*|.*ohne schufa.*|.*online kaufen.*|.*onlineshop.*|.*pdf.*|.*preis.*|.*preisausschreiben.*|.*preisvergleich.*|.*preiswert.*|.*rabatt.*|.*shop.*|.*special.*|.*template.*|.*überbestände.*|.*umsonst.*|.*verkauf.*|.*vorlage.*|.*vorrätig.*|.*werbung.*|.*wo kauf.*|.*zu verkaufen.*', kw_lower):
                intents.append("DO (Transactional)")

            # User Intent: regional:CITY
            if re.search(r'.*aach.*|.*aalen.*|.*abenberg.*|.*abensberg.*|.*achern.*|.*achim.*|.*adelsheim.*|.*adenau.*|.*adorf.*|.*ahaus.*|.*ahlen.*|.*ahrensburg.*|.*aichach.*|.*aichtal.*|.*aken.*|.*albstadt.*|.*alfeld.*|.*allendorf.*|.*allstedt.*|.*alpirsbach.*|.*alsdorf.*|.*alsfeld.*|.*alsleben.*|.*altdorf.*|.*altena.*|.*altenau.*|.*altenberg.*|.*altenburg.*|.*altenkirchen.*|.*altensteig.*|.*altentreptow.*|.*altlandsberg.*|.*altötting.*|.*alzenau.*|.*alzey.*|.*amberg.*|.*amöneburg.*|.*amorbach.*|.*andernach.*|.*angermünde.*|.*anklam.*|.*annaberg.*|.*annaberg-buchholz.*|.*annaburg.*|.*annweiler.*|.*ansbach.*|.*apolda.*|.*arendsee.*|.*arneburg.*|.*arnis.*|.*arnsberg.*|.*arnstadt.*|.*arnstein.*|.*artern.*|.*unstrut.*|.*arzberg.*|.*aschaffenburg.*|.*aschersleben.*|.*asperg.*|.*aßlar.*|.*attendorn.*|.*aub.*|.*aue.*|.*auerbach.*|.*augsburg.*|.*augustusburg.*|.*aulendorf.*|.*aurich.*|.*babenhausen.*|.*bacharach.*|.*backnang.*|.*bad aibling.*|.*bad arolsen.*|.*bad bentheim.*|.*bad bergzabern.*|.*bad berka.*|.*bad berleburg.*|.*bad berneck.*|.*bad bevensen.*|.*bad bibra.*|.*bad blankenburg.*|.*bad bramstedt.*|.*bad breisig.*|.*bad brückenau.*|.*bad buchau.*|.*bad camberg.*|.*bad colberg.*|.*bad colberg heldburg.*|.*colberg.*|.*heldburg.*|.*doberan.*|.*bad driburg.*|.*bad düben.*|.*bad dürkheim.*|.*bad dürrenberg.*|.*bad dürrheim.*|.*bad elster.*|.*bad ems.*|.*bad fallingbostel.*|.*bad frankenhausen.*|.*frankenhausen.*|.*kyffhäuser.*|.*bad freienwalde.*|.*bad friedrichshall.*|.*bad gandersheim.*|.*bad gottleuba.*|.*bad gottleuba-berggießhübel.*|.*bad griesbach.*|.*griesbach.*|.*bad grund.*|.*bad harzburg.*|.*bad herrenalb.*|.*bad hersfeld.*|.*bad homburg.*|.*bad homburg vor der höhe.*|.*bad honnef.*|.*bad hönningen.*|.*bad iburg.*|.*bad karlshafen.*|.*kissingen.*|.*bad könig.*|.*königshofen.*|.*bad kösen.*|.*köstritz.*|.*kötzting.*|.*bad kreuznach.*|.*bad krozingen.*|.*bad laasphe.*|.*bad langensalza.*|.*bad lauchstädt.*|.*bad lausick.*|.*bad lauterberg.*|.*bad lauterberg im harz.*|.*bad liebenstein.*|.*bad liebenwerda.*|.*bad liebenzell.*|.*bad lippspringe.*|.*bad lobenstein.*|.*bad marienberg.*|.*bad mergentheim.*|.*bad münder am deister.*|.*bad münster.*|.*bad münster am stein-ebernburg.*|.*bad münstereifel.*|.*bad muskau.*|.*bad nauheim.*|.*bad nenndorf.*|.*bad neuenahr.*|.*bad neuenahr-ahrweiler.*|.*bad neustadt.*|.*bad neustadt an der saale.*|.*bad oeynhausen.*|.*bad oldesloe.*|.*bad orb.*|.*bad pyrmont.*|.*bad rappenau.*|.*bad reichenhall.*|.*bad rodach.*|.*bad sachsa.*|.*bad säckingen.*|.*bad salzdetfurth.*|.*bad salzuflen.*|.*bad salzungen.*|.*bad saulgau.*|.*bad schandau.*|.*bad schmiedeberg.*|.*bad schussenried.*|.*bad schwalbach.*|.*bad schwartau.*|.*bad segeberg.*|.*bad sobernheim.*|.*bad soden.*|.*bad soden am taunus.*|.*bad soden-salmünster.*|.*bad sooden.*|.*bad sooden-allendorf.*|.*staffelstein.*|.*bad sulza.*|.*bad sülze.*|.*teinach.*|.*zavelstein.*|.*tennstedt.*|.*tölz.*|.*bad urach.*|.*vilbel.*|.*bad waldsee.*|.*bad wildbad.*|.*bad wildungen.*|.*bad wilsnack.*|.*bad wimpfen.*|.*bad windsheim.*|.*bad wörishofen.*|.*bad wünnenberg.*|.*bad wurzach.*|.*baden-baden.*|.*baesweiler.*|.*baiersdorf.*|.*balingen.*|.*ballenstedt.*|.*balve.*|.*bamberg.*|.*barby.*|.*bargteheide.*|.*barmstedt.*|.*bärnau.*|.*barntrup.*|.*barsinghausen.*|.*barth.*|.*baruth.*|.*baruth.*|.*bassum.*|.*battenberg.*|.*baumholder.*|.*baunach.*|.*baunatal.*|.*bautzen.*|.*bayreuth.*|.*bebra.*|.*beckum.*|.*bedburg.*|.*beelitz.*|.*beerfelden.*|.*beeskow.*|.*beilngries.*|.*beilstein.*|.*belgern.*|.*belzig.*|.*bendorf.*|.*benneckenstein.*|.*bensheim.*|.*berching.*|.*berga elster.*|.*bergen.*|.*bergheim.*|.*bergisch gladbach.*|.*bergkamen.*|.*bergneustadt.*|.*berka.*|.*berka werra.*|.*werra.*|.*berlin.*|.*bernau bei berlin.*|.*bernburg.*|.*bernkastel-kues.*|.*bernsdorf.*|.*bernstadt a. d. eigen.*|.*bersenbrück.*|.*besigheim.*|.*betzdorf.*|.*betzenstein.*|.*beverungen.*|.*bexbach.*|.*biberach an der riß.*|.*biedenkopf.*|.*bielefeld.*|.*biesenthal.*|.*bietigheim-bissingen.*|.*billerbeck.*|.*bingen am rhein.*|.*birkenfeld.*|.*bischofsheim an der rhön.*|.*bischofswerda.*|.*bismark.*|.*bitburg.*|.*bitterfeld.*|.*blankenburg.*|.*blankenhain.*|.*blaubeuren.*|.*bleckede.*|.*bleicherode.*|.*blieskastel.*|.*blomberg.*|.*blumberg.*|.*bobingen.*|.*böblingen.*|.*bocholt.*|.*bochum.*|.*bockenem.*|.*bodenwerder.*|.*bogen.*|.*böhlen.*|.*boizenburg.*|.*bonn.*|.*bonndorf im schwarzwald.*|.*bönnigheim.*|.*bopfingen.*|.*boppard.*|.*borgentreich.*|.*borgholzhausen.*|.*borken.*|.*borken.*|.*borkum.*|.*borna.*|.*bornheim.*|.*bottrop.*|.*boxberg.*|.*brackenheim.*|.*brake.*|.*brakel.*|.*bramsche.*|.*brand-erbisdorf.*|.*brandenburg an der havel.*|.*brandis.*|.*braubach.*|.*braunfels.*|.*braunlage.*|.*bräunlingen.*|.*braunsbedra.*|.*braunschweig.*|.*breckerfeld.*|.*bredstedt.*|.*brehna.*|.*breisach am rhein.*|.*bremen.*|.*bremerhaven.*|.*bremervörde.*|.*bretten.*|.*breuberg.*|.*brilon.*|.*brotterode.*|.*bruchköbel.*|.*bruchsal.*|.*brück.*|.*brüel.*|.*brühl.*|.*brunsbüttel.*|.*brüssow.*|.*buchen.*|.*buchholz.*|.*buchholz in der nordheide.*|.*buchloe.*|.*bückeburg.*|.*buckow.*|.*büdelsdorf.*|.*büdingen.*|.*bühl.*|.*bünde.*|.*büren.*|.*burg.*|.*burg stargard.*|.*burgau.*|.*burgbernheim.*|.*burgdorf.*|.*bürgel.*|.*burghausen.*|.*burgkunstadt.*|.*burglengenfeld.*|.*burgstädt.*|.*burgwedel.*|.*burladingen.*|.*burscheid.*|.*bürstadt.*|.*buttelstedt.*|.*buttstädt.*|.*butzbach.*|.*bützow.*|.*buxtehude.*|.*calau.*|.*calbe.*|.*calw.*|.*camburg.*|.*castrop-rauxel.*|.*celle.*|.*cham.*|.*chemnitz.*|.*clausthal-zellerfeld.*|.*clingen.*|.*cloppenburg.*|.*coburg.*|.*cochem.*|.*coesfeld.*|.*colditz.*|.*coswig.*|.*coswig.*|.*cottbus.*|.*crailsheim.*|.*creglingen.*|.*creußen.*|.*creuzburg.*|.*crimmitschau.*|.*crivitz.*|.*cuxhaven.*|.*dachau.*|.*dahlen.*|.*dahme.*|.*dahn.*|.*damme.*|.*dannenberg.*|.*dargun.*|.*darmstadt.*|.*dassel.*|.*dassow.*|.*datteln.*|.*daun.*|.*deggendorf.*|.*deidesheim.*|.*delbrück.*|.*delitzsch.*|.*delmenhorst.*|.*demmin.*|.*derenburg.*|.*dessau.*|.*detmold.*|.*dettelbach.*|.*dieburg.*|.*diemelstadt.*|.*diepholz.*|.*dierdorf.*|.*dietenheim.*|.*dietfurt an der altmühl.*|.*dietzenbach.*|.*diez.*|.*dillenburg.*|.*donau.*|.*dillingen.*|.*dingelstädt.*|.*dingolfing.*|.*dinkelsbühl.*|.*dinklage.*|.*dinslaken.*|.*dippoldiswalde.*|.*dissen am teutoburger wald.*|.*ditzingen.*|.*döbeln.*|.*doberlug-kirchhain.*|.*döbern.*|.*dohna.*|.*dömitz.*|.*dommitzsch.*|.*donaueschingen.*|.*donauwörth.*|.*donzdorf.*|.*dorfen.*|.*dormagen.*|.*dornburg.*|.*dornhan.*|.*dornstetten.*|.*dorsten.*|.*dortmund.*|.*dransfeld.*|.*drebkau.*|.*dreieich.*|.*drensteinfurt.*|.*dresden.*|.*drolshagen.*|.*duderstadt.*|.*duisburg.*|.*dülmen.*|.*düren.*|.*düsseldorf.*|.*ebeleben.*|.*eberbach.*|.*ebermannstadt.*|.*ebern.*|.*ebersbach.*|.*ebersbach an der fils.*|.*ebersberg.*|.*eberswalde.*|.*eckartsberga.*|.*eckernförde.*|.*edenkoben.*|.*egeln.*|.*eggenfelden.*|.*eggesin.*|.*ehingen.*|.*ehrenfriedersdorf.*|.*eibelstadt.*|.*eibenstock.*|.*eichstätt.*|.*eilenburg.*|.*einbeck.*|.*eisenach.*|.*eisenberg.*|.*eisenberg.*|.*eisenhüttenstadt.*|.*eisfeld.*|.*eisleben.*|.*eislingen.*|.*elbingerode.*|.*ellingen.*|.*ellrich.*|.*ellwangen.*|.*elmshorn.*|.*elsfleth.*|.*elsterberg.*|.*elsterwerda.*|.*elstra.*|.*elterlein.*|.*eltmann.*|.*eltville am rhein.*|.*elzach.*|.*elze.*|.*emden.*|.*emmendingen.*|.*emmerich am rhein.*|.*emsdetten.*|.*endingen am kaiserstuhl.*|.*engen.*|.*enger.*|.*ennepetal.*|.*ennigerloh.*|.*eppelheim.*|.*eppingen.*|.*eppstein.*|.*erbach.*|.*erbach.*|.*erbendorf.*|.*erding.*|.*erftstadt.*|.*erfurt.*|.*erkelenz.*|.*erkner.*|.*erkrath.*|.*erlangen.*|.*erlenbach am main.*|.*erwitte.*|.*eschborn.*|.*eschenbach in der oberpfalz.*|.*eschershausen.*|.*eschwege.*|.*eschweiler.*|.*espelkamp.*|.*essen.*|.*esslingen.*|.*ettenheim.*|.*ettlingen.*|.*euskirchen.*|.*eutin.*|.*falkenberg.*|.*falkensee.*|.*falkenstein.*|.*fehmarn.*|.*fellbach.*|.*felsberg.*|.*feuchtwangen.*|.*filderstadt.*|.*finsterwalde.*|.*fladungen.*|.*flensburg.*|.*flöha.*|.*flörsheim.*|.*forchheim.*|.*forchtenberg.*|.*frankenau.*|.*frankenberg.*|.*frankenberg.*|.*frankenthal.*|.*frankfurt.*|.*frankfurt am main.*|.*franzburg.*|.*franzburg.*|.*frechen.*|.*freiberg.*|.*freiberg am neckar.*|.*freiburg im breisgau.*|.*freilassing.*|.*freinsheim.*|.*freising.*|.*freital.*|.*freren.*|.*freudenberg.*|.*freudenberg.*|.*freudenstadt.*|.*freyburg.*|.*freystadt.*|.*freyung.*|.*fridingen an der donau.*|.*friedberg.*|.*friedberg.*|.*friedland.*|.*friedland.*|.*friedrichroda.*|.*friedrichsdorf.*|.*friedrichshafen.*|.*friedrichstadt.*|.*friedrichsthal.*|.*friesack.*|.*friesoythe.*|.*fritzlar.*|.*frohburg.*|.*fröndenberg.*|.*fulda.*|.*fürstenau.*|.*fürstenberg.*|.*fürstenfeldbruck.*|.*fürstenwalde.*|.*fürth.*|.*furth im wald.*|.*furtwangen im schwarzwald.*|.*füssen.*|.*gadebusch.*|.*gaggenau.*|.*gaildorf.*|.*gammertingen.*|.*garbsen.*|.*garching bei münchen.*|.*gardelegen.*|.*garding.*|.*gartz.*|.*garz.*|.*algesheim.*|.*gebesee.*|.*gedern.*|.*geesthacht.*|.*gefell.*|.*gefrees.*|.*gehrden.*|.*geilenkirchen.*|.*geisa.*|.*geiselhöring.*|.*geisenfeld.*|.*geisenheim.*|.*geising.*|.*geisingen.*|.*geislingen.*|.*geislingen an der steige.*|.*geithain.*|.*geldern.*|.*gelnhausen.*|.*gelsenkirchen.*|.*gemünden.*|.*gemünden am main.*|.*gengenbach.*|.*genthin.*|.*georgsmarienhütte.*|.*gera.*|.*gerabronn.*|.*gerbstedt.*|.*geretsried.*|.*geringswalde.*|.*gerlingen.*|.*germering.*|.*germersheim.*|.*gernrode.*|.*gernsbach.*|.*gernsheim.*|.*gerolstein.*|.*gerolzhofen.*|.*gersfeld.*|.*gersthofen.*|.*gescher.*|.*geseke.*|.*gevelsberg.*|.*geyer.*|.*giengen.*|.*gießen.*|.*gifhorn.*|.*gladbeck.*|.*gladenbach.*|.*glashütte.*|.*glauchau.*|.*glinde.*|.*glücksburg.*|.*glückstadt.*|.*gnoien.*|.*goch.*|.*goldberg.*|.*goldkronach.*|.*golßen.*|.*gommern.*|.*göppingen.*|.*görlitz.*|.*goslar.*|.*gößnitz.*|.*gotha.*|.*göttingen.*|.*grabow.*|.*grafenau.*|.*gräfenberg.*|.*gräfenhainichen.*|.*gräfenthal.*|.*grafenwöhr.*|.*grafing.*|.*gransee.*|.*grebenau.*|.*grebenstein.*|.*greding.*|.*greifswald.*|.*greiz.*|.*greußen.*|.*greven.*|.*grevenbroich.*|.*grevesmühlen.*|.*griesheim.*|.*grimma.*|.*grimmen.*|.*gröbzig.*|.*gröditz.*|.*groitzsch.*|.*gronau.*|.*gronau.*|.*gröningen.*|.*groß bieberau.*|.*groß gerau.*|.*groß-umstadt.*|.*großalmerode.*|.*großbottwar.*|.*großbreitenbach.*|.*großenehrich.*|.*großenhain.*|.*großräschen.*|.*großröhrsdorf.*|.*großschirma.*|.*grünberg.*|.*grünhain-beierfeld.*|.*grünsfeld.*|.*grünstadt.*|.*guben.*|.*gudensberg.*|.*güglingen.*|.*gummersbach.*|.*gundelfingen an der donau.*|.*gundelsheim.*|.*güntersberge.*|.*günzburg.*|.*gunzenhausen.*|.*güsten.*|.*güstrow.*|.*gütersloh.*|.*gützkow.*|.*haan.*|.*hachenburg.*|.*hadamar.*|.*hadmersleben.*|.*hagen.*|.*hagenbach.*|.*hagenow.*|.*haiger.*|.*haigerloch.*|.*hainichen.*|.*haiterbach.*|.*halberstadt.*|.*haldensleben.*|.*halle.*|.*halle.*|.*hallenberg.*|.*hallstadt.*|.*haltern am see.*|.*halver.*|.*hamburg.*|.*hameln.*|.*hamm.*|.*hammelburg.*|.*hamminkeln.*|.*hanau.*|.*hann. münden.*|.*hannover.*|.*harburg.*|.*hardegsen.*|.*haren.*|.*harsewinkel.*|.*hartenstein.*|.*hartha.*|.*harzgerode.*|.*haselünne.*|.*haslach im kinzigtal.*|.*hasselfelde.*|.*haßfurt.*|.*hattersheim am main.*|.*hattingen.*|.*hatzfeld.*|.*hausach.*|.*hauzenberg.*|.*havelberg.*|.*havelsee.*|.*hayingen.*|.*hechingen.*|.*hecklingen.*|.*heideck.*|.*heidelberg.*|.*heidenau.*|.*heidenheim an der brenz.*|.*heilbad heiligenstadt.*|.*heilbronn.*|.*heiligenhafen.*|.*heiligenhaus.*|.*heilsbronn.*|.*heimbach.*|.*heimsheim.*|.*heinsberg.*|.*heitersheim.*|.*heldrungen.*|.*helmbrechts.*|.*helmstedt.*|.*hemau.*|.*hemer.*|.*hemmingen.*|.*hemmoor.*|.*hemsbach.*|.*hennef.*|.*hennigsdorf.*|.*heppenheim.*|.*herbolzheim.*|.*herborn.*|.*herbrechtingen.*|.*herbstein.*|.*herdecke.*|.*herdorf.*|.*herford.*|.*heringen.*|.*heringen.*|.*hermeskeil.*|.*hermsdorf.*|.*herne.*|.*herrenberg.*|.*herrieden.*|.*herrnhut.*|.*hersbruck.*|.*herten.*|.*herzberg.*|.*herzberg am harz.*|.*herzogenaurach.*|.*herzogenrath.*|.*hessisch lichtenau.*|.*hessisch oldendorf.*|.*hettingen.*|.*hettstedt.*|.*heubach.*|.*heusenstamm.*|.*hilchenbach.*|.*hildburghausen.*|.*hilden.*|.*hildesheim.*|.*hillesheim.*|.*hilpoltstein.*|.*hirschau.*|.*hirschberg.*|.*hirschhorn.*|.*hitzacker.*|.*hochheim am main.*|.*höchstadt an der aisch.*|.*höchstädt an der donau.*|.*hockenheim.*|.*hofgeismar.*|.*hofheim.*|.*hohen neuendorf.*|.*hohenberg.*|.*hohenleuben.*|.*hohenmölsen.*|.*hohenstein-ernstthal.*|.*hohnstein.*|.*höhr-grenzhausen.*|.*hollfeld.*|.*holzgerlingen.*|.*holzminden.*|.*homberg.*|.*homberg.*|.*homburg.*|.*horb am neckar.*|.*meinberg.*|.*hornbach.*|.*hornberg.*|.*hornburg.*|.*hörstel.*|.*horstmar.*|.*höxter.*|.*hoya.*|.*hoyerswerda.*|.*hoym.*|.*hückelhoven.*|.*hückeswagen.*|.*hüfingen.*|.*hünfeld.*|.*hungen.*|.*hürth.*|.*husum.*|.*ibbenbüren.*|.*ichenhausen.*|.*idar-oberstein.*|.*idstein.*|.*illertissen.*|.*ilmenau.*|.*ilsenburg.*|.*ilshofen.*|.*immenhausen.*|.*immenstadt im allgäu.*|.*ingelfingen.*|.*ingelheim am rhein.*|.*ingolstadt.*|.*iphofen.*|.*iserlohn.*|.*isny im allgäu.*|.*isselburg.*|.*itzehoe.*|.*jarmen.*|.*jena.*|.*jerichow.*|.*jessen.*|.*jeßnitz.*|.*jever.*|.*joachimsthal.*|.*johanngeorgenstadt.*|.*jöhstadt.*|.*jülich.*|.*jüterbog.*|.*kaarst.*|.*kahla.*|.*kaisersesch.*|.*kaiserslautern.*|.*kalbe.*|.*kalkar.*|.*kaltenkirchen.*|.*kaltennordheim.*|.*kamen.*|.*kamenz.*|.*kamp-lintfort.*|.*kandel.*|.*kandern.*|.*kappeln.*|.*karben.*|.*karlsruhe.*|.*karlstadt.*|.*kassel.*|.*kastellaun.*|.*katzenelnbogen.*|.*kaub.*|.*kaufbeuren.*|.*kehl.*|.*kelbra.*|.*kelheim.*|.*kelkheim.*|.*kellinghusen.*|.*kelsterbach.*|.*kemberg.*|.*kemnath.*|.*kempen.*|.*kempten.*|.*kenzingen.*|.*kerpen.*|.*ketzin.*|.*kevelaer.*|.*kiel.*|.*kierspe.*|.*kindelbrück.*|.*kirchberg.*|.*kirchberg.*|.*kirchberg an der jagst.*|.*kirchen.*|.*kirchenlamitz.*|.*kirchhain.*|.*kirchheim unter teck.*|.*kirchheimbolanden.*|.*kirn.*|.*kirtorf.*|.*kitzingen.*|.*kitzscher.*|.*kleve.*|.*klingenberg.*|.*klingenthal.*|.*klötze.*|.*klütz.*|.*knittlingen.*|.*koblenz.*|.*kohren-sahlis.*|.*kolbermoor.*|.*kölleda.*|.*köln.*|.*königs wusterhausen.*|.*königsberg in bayern.*|.*königsbrück.*|.*königsbrunn.*|.*königsee.*|.*königslutter.*|.*königstein.*|.*königstein im taunus.*|.*königswinter.*|.*könnern.*|.*konstanz.*|.*konz.*|.*korbach.*|.*korntal-münchingen.*|.*kornwestheim.*|.*korschenbroich.*|.*köthen.*|.*kraichtal.*|.*krakow am see.*|.*kranichfeld.*|.*krautheim.*|.*krefeld.*|.*kremmen.*|.*krempe.*|.*kreuztal.*|.*kronach.*|.*kronberg im taunus.*|.*kröpelin.*|.*kroppenstedt.*|.*krumbach.*|.*kühlungsborn.*|.*kulmbach.*|.*külsheim.*|.*künzelsau.*|.*kupferberg.*|.*kuppenheim.*|.*kusel.*|.*kyllburg.*|.*kyritz.*|.*laage.*|.*laatzen.*|.*ladenburg.*|.*lahnstein.*|.*lahr.*|.*schwarzwald.*|.*laichingen.*|.*lambrecht.*|.*lampertheim.*|.*landau an der isar.*|.*landau in der pfalz.*|.*landsberg.*|.*landsberg am lech.*|.*landshut.*|.*landstuhl.*|.*langelsheim.*|^langen.*|.*langenau.*|.*langenburg.*|.*langenfeld.*|.*langenhagen.*|.*langenselbold.*|.*langenzenn.*|.*langewiesen.*|.*lassan.*|.*laubach.*|.*laucha an der unstrut.*|.*lauchhammer.*|.*lauchheim.*|.*lauda-königshofen.*|.*lauenburg.*|.*lauf an der pegnitz.*|.*laufen.*|.*laufenburg.*|.*lauffen am neckar.*|.*lauingen.*|.*laupheim.*|.*lauscha.*|.*lauta.*|.*lauter.*|.*lebach.*|.*lebus.*|.*leer.*|.*lehesten.*|.*lehrte.*|.*leichlingen.*|.*leimen.*|.*leinefelde-worbis.*|.*leinfelden-echterdingen.*|.*leipheim.*|.*leipzig.*|.*leisnig.*|.*lemgo.*|.*lengefeld.*|.*lengenfeld.*|.*lengerich.*|.*stadt.*|.*lenzen.*|.*leonberg.*|.*leun.*|.*leuna.*|.*leutenberg.*|.*leutershausen.*|.*leutkirch im allgäu.*|.*leverkusen.*|.*lichtenau.*|.*lichtenberg.*|.*lichtenfels.*|.*lichtenstein.*|.*liebenau.*|.*liebenwalde.*|.*lieberose.*|.*limbach-oberfrohna.*|.*limburg an der lahn.*|.*lindau.*|.*lindau.*|.*linden.*|.*lindenberg.*|.*lindenfels.*|.*lindow.*|.*linnich.*|.*linz am rhein.*|.*löbau.*|.*löbejün.*|.*loburg.*|.*löffingen.*|.*lohmar.*|.*lohne.*|.*löhne.*|.*lohr am main.*|.*loitz.*|.*lollar.*|.*lommatzsch.*|.*löningen.*|.*lorch.*|.*lorch.*|.*lörrach.*|.*lorsch.*|.*lößnitz.*|.*löwenstein.*|.*lübbecke.*|.*lübben.*|.*lübbenau.*|.*spreewald.*|.*lübeck.*|.*lübtheen.*|.*lübz.*|.*lüchow.*|.*lucka.*|.*luckau.*|.*luckenwalde.*|.*lüdenscheid.*|.*lüdinghausen.*|.*ludwigsburg.*|.*ludwigsfelde.*|.*ludwigshafen am rhein.*|.*ludwigslust.*|.*lugau.*|.*lügde.*|.*lüneburg.*|.*lünen.*|.*lunzenau.*|.*lütjenburg.*|.*lützen.*|.*lychen.*|.*magdala.*|.*magdeburg.*|.*mahlberg.*|.*mainbernheim.*|.*mainburg.*|.*maintal.*|.*mainz.*|.*malchin.*|.*malchow.*|.*manderscheid.*|.*mannheim.*|.*mansfeld.*|.*marbach am neckar.*|.*marburg.*|.*marienberg.*|.*marienmünster.*|.*markdorf.*|.*markgröningen.*|.*märkisch buchholz.*|.*markkleeberg.*|.*markneukirchen.*|.*markranstädt.*|.*marktbreit.*|.*marktheidenfeld.*|.*marktleuthen.*|.*marktoberdorf.*|.*marktredwitz.*|.*marktsteft.*|.*marlow.*|.*marne$|^marne.*|.*marsberg.*|.*maulbronn.*|.*maxhütte-haidhof.*|.*mayen.*|.*mechernich.*|.*meckenheim.*|.*medebach.*|.*meerane.*|.*meerbusch.*|.*meersburg.*|.*meinerzhagen.*|.*meiningen.*|.*meisenheim.*|.*meißen.*|.*meldorf.*|.*melle.*|.*melsungen.*|.*memmingen.*|.*menden.*|.*mendig.*|.*mengen.*|.*meppen.*|.*merkendorf.*|.*merseburg.*|.*merzig.*|.*meschede.*|.*meßkirch.*|.*meßstetten.*|.*mettmann.*|.*metzingen.*|.*meuselwitz.*|.*meyenburg.*|.*miesbach.*|.*miltenberg.*|.*mindelheim.*|.*minden.*|.*mirow.*|.*mittenwalde.*|.*mitterteich.*|.*mittweida.*|.*möckern.*|.*möckmühl.*|.*moers.*|.*mölln.*|.*mönchengladbach.*|.*monheim.*|.*monheim am rhein.*|.*monschau.*|.*montabaur.*|.*moosburg an der isar.*|.*mörfelden-walldorf.*|.*moringen.*|.*mosbach.*|.*mössingen.*|.*mücheln.*|.*mügeln.*|.*mühlacker.*|.*mühlberg.*|.*mühldorf.*|.*mühlhausen.*|.*mühlheim.*|.*mühltroff.*|.*mülheim.*|.*müllheim.*|.*müllrose.*|.*münchberg.*|.*müncheberg.*|.*münchen.*|.*münchenbernsdorf.*|.*munderkingen.*|.*münsingen.*|.*munster.*|.*münster.*|.*münstermaifeld.*|.*münzenberg.*|.*murrhardt.*|.*mutzschen.*|.*mylau.*|.*nabburg.*|.*nagold.*|.*naila.*|.*nassau.*|.*nastätten.*|.*nauen.*|.*naumburg.*|.*naumburg.*|.*naunhof.*|.*nebra.*|.*neckarbischofsheim.*|.*neckargemünd.*|.*neckarsteinach.*|.*neckarsulm.*|.*nerchau.*|.*neresheim.*|.*netphen.*|.*nettetal.*|.*netzschkau.*|.*neu-isenburg.*|.*neu ulm.*|.*neubrandenburg.*|.*neubukow.*|.*neubulach.*|.*neuburg.*|.*neudenau.*|.*neuenbürg.*|.*neuenburg am rhein.*|.*neuenhaus.*|.*neuenrade.*|.*neuenstein.*|.*neuerburg.*|.*neuffen.*|.*neugersdorf.*|.*neuhaus am rennweg.*|.*neukalen.*|.*neukirchen.*|.*neukirchen-vluyn.*|.*neukloster.*|.*neumark.*|.*neumünster.*|.*neunburg.*|.*neunkirchen.*|.*neuötting.*|.*neuruppin.*|.*neusalza-spremberg.*|.*neusäß.*|.*neuss.*|.*neustrelitz.*|.*neutraubling.*|.*neuwied.*|.*nidda.*|.*niddatal.*|.*nidderau.*|.*nideggen.*|.*niebüll.*|.*niedenstein.*|.*niederkassel.*|.*niedernhall.*|.*niederstetten.*|.*niederstotzingen.*|.*nieheim.*|.*niemegk.*|.*nienburg.*|.*nienburg.*|.*niesky.*|.*nittenau.*|.*norden.*|.*nordenham.*|.*norderney.*|.*norderstedt.*|.*nordhausen.*|.*nordhorn.*|.*nördlingen.*|.*northeim.*|.*nortorf.*|.*nossen.*|.*nürnberg.*|.*nürtingen.*|.*ober-ramstadt.*|.*oberasbach.*|.*oberhausen.*|.*oberhof.*|.*oberkirch.*|.*oberkochen.*|.*oberlungwitz.*|.*obermoschel.*|.*obernburg am main.*|.*oberndorf am neckar.*|.*obernkirchen.*|.*oberriexingen.*|.*obertshausen.*|.*oberursel.*|.*oberviechtach.*|.*oberweißbach.*|.*oberwesel.*|.*oberwiesenthal.*|.*ochsenfurt.*|.*ochsenhausen.*|.*ochtrup.*|.*oderberg.*|.*oebisfelde.*|.*oederan.*|.*oelde.*|.*oelsnitz.*|.*erzgebirge.*|.*erkenschwick.*|.*oerlinghausen.*|.*oestrich-winkel.*|.*oettingen in bayern.*|.*offenbach am main.*|.*offenburg.*|.*ohrdruf.*|.*öhringen.*|.*olbernhau.*|.*oldenburg.*|.*oldenburg in holstein.*|.*olfen.*|.*olpe.*|.*olsberg.*|.*oppenau.*|.*oppenheim.*|.*oranienbaum.*|.*oranienburg.*|.*orlamünde.*|.*ornbau.*|.*ortenberg.*|.*ortrand.*|.*oschatz.*|.*oschersleben.*|.*osnabrück.*|.*osterburg.*|.*osterburken.*|.*osterfeld.*|.*osterhofen.*|.*osterholz-scharmbeck.*|.*osterode am harz.*|.*osterwieck.*|.*ostfildern.*|.*ostheim vor der rhön.*|.*osthofen.*|.*östringen.*|.*ostritz.*|.*otterberg.*|.*otterndorf.*|.*ottweiler.*|.*overath.*|.*owen.*|.*paderborn.*|.*papenburg.*|.*pappenheim.*|.*parchim.*|.*parsberg.*|.*pasewalk.*|.*passau.*|.*pattensen.*|.*pausa.*|.*vogtland.*|.*pegau.*|.*pegnitz.*|.*peine.*|.*peitz.*|.*penig.*|.*penkun.*|.*penzberg.*|.*penzlin.*|.*perleberg.*|.*petershagen.*|.*pfaffenhofen an der ilm.*|.*pfarrkirchen.*|.*pforzheim.*|.*pfreimd.*|.*pfullendorf.*|.*pfullingen.*|.*philippsburg.*|.*pinneberg.*|.*pirmasens.*|.*pirna.*|.*plattling.*|.*plau am see.*|.*plaue.*|.*plauen.*|.*plettenberg.*|.*pleystein.*|.*plochingen.*|.*plön.*|.*pocking.*|.*pohlheim.*|.*polch.*|.*porta westfalica.*|.*pößneck.*|.*potsdam.*|.*pottenstein.*|.*preetz.*|.*premnitz.*|.*prenzlau.*|.*pressath.*|.*prettin.*|.*pretzsch.*|.*preußisch oldendorf.*|.*pritzwalk.*|.*prüm.*|.*pulheim.*|.*pulsnitz.*|.*putbus.*|.*putlitz.*|.*püttlingen.*|.*quakenbrück.*|.*quedlinburg.*|.*querfurt.*|.*quickborn.*|.*rabenau.*|.*radeberg.*|.*radebeul.*|.*radeburg.*|.*radegast.*|.*radevormwald.*|.*radolfzell am bodensee.*|.*raguhn.*|.*rahden.*|.*rain.*|.*ramstein-miesenbach.*|.*ranis.*|.*ransbach.*|.*baumbach.*|.*rastatt.*|.*rastenberg.*|.*rathenow.*|.*ratingen.*|.*ratzeburg.*|.*rauenberg.*|.*raunheim.*|.*rauschenberg.*|.*ravensburg.*|.*ravenstein.*|.*recklinghausen.*|.*rees.*|.*regen.*|.*regensburg.*|.*regis breitingen.*|.*rehau.*|.*rehburg-loccum.*|.*rehna.*|.*reichelsheim.*|.*reichenbach.*|.*reinbek.*|.*reinfeld.*|.*reinheim.*|.*remagen.*|.*remda-teichel.*|.*remscheid.*|.*remseck am neckar.*|.*renchen.*|.*rendsburg.*|.*rennerod.*|.*renningen.*|.*rerik.*|.*rethem.*|.*reutlingen.*|.*rheda-wiedenbrück.*|.*rhede.*|.*rheinau.*|.*rheinbach.*|.*rheinberg.*|.*rheine.*|.*rheinfelden.*|.*rheinsberg.*|.*rheinstetten.*|.*rhens.*|.*rhinow.*|.*ribnitz-damgarten.*|.*richtenberg.*|.*riedenburg.*|.*riedlingen.*|.*rieneck.*|.*riesa.*|.*rietberg.*|.*rinteln.*|.*röbel.*|.*müritz.*|.*rochlitz.*|.*rockenhausen.*|.*rodalben.*|.*rodenberg.*|.*rödental.*|.*rödermark.*|.*rodewisch.*|.*rodgau.*|.*roding.*|.*römhild.*|.*romrod.*|.*ronneburg.*|.*ronnenberg.*|.*rosbach.*|.*rosenfeld.*|.*rosenheim.*|.*rosenthal.*|.*rösrath.*|.*roßlau.*|.*roßleben.*|.*roßwein.*|.*rostock.*|.*rotenburg.*|.*rotenburg an der flux.*|.*roth.*|.*rötha.*|.*röthenbach.*|.*rothenburg.*|.*rothenfels.*|.*rottenburg.*|.*rottenburg am neckar.*|.*röttingen.*|.*rottweil.*|.*rötz.*|.*rüdesheim.*|.*ruhla.*|.*ruhland.*|.*runkel.*|.*rüsselsheim.*|.*rüthen.*|.*saalburg.*|.*saalburg ebersdorf.*|.*saalfeld.*|.*saale.*|.*saarbrücken.*|.*saarburg.*|.*saarlouis.*|.*sachsenhagen.*|.*sachsenheim.*|.*salzgitter.*|.*salzkotten.*|.*salzwedel.*|.*sandau.*|.*sandersleben.*|.*sangerhausen.*|.*sankt andreasberg.*|.*sankt augustin.*|.*sankt goar.*|.*sankt goarshausen.*|.*sarstedt.*|.*sassenberg.*|.*sassnitz.*|.*sayda.*|.*schafstädt.*|.*schalkau.*|.*schauenstein.*|.*scheer.*|.*scheibenberg.*|.*scheinfeld.*|.*schelklingen.*|.*schenefeld.*|.*scheßlitz.*|.*schieder-schwalenberg.*|.*schildau.*|.*schillingsfürst.*|.*schiltach.*|.*schirgiswalde.*|.*schkeuditz.*|.*schkölen.*|.*schleiden.*|.*schleiz.*|.*schleswig.*|.*schlettau.*|.*schleusingen.*|.*schlieben.*|.*schlitz.*|.*schloß holte-stukenbrock.*|.*schlotheim.*|.*schlüchtern.*|.*schlüsselfeld.*|.*schmalkalden.*|.*schmallenberg.*|.*schmölln.*|.*schnackenburg.*|.*schnaittenbach.*|.*schneeberg.*|.*schneverdingen.*|.*schömberg.*|.*schönau.*|.*schönau im schwarzwald.*|.*schönberg.*|.*schönebeck.*|.*schöneck.*|.*schönewalde.*|.*schongau.*|.*schöningen.*|.*schönsee.*|.*schönwald.*|.*schopfheim.*|.*schöppenstedt.*|.*schorndorf.*|.*schortens.*|.*schotten.*|.*schramberg.*|.*schraplau.*|.*schriesheim.*|.*schrobenhausen.*|.*schrozberg.*|.*schüttorf.*|.*schwaan.*|.*schwabach.*|.*schwäbisch gmünd.*|.*schwäbisch hall.*|.*schwabmünchen.*|.*schwaigern.*|.*schwalbach am taunus.*|.*schwandorf.*|.*schwanebeck.*|.*schwarzenbach.*|.*schwarzenbek.*|.*schwarzenberg.*|.*schwarzenborn.*|.*schwarzheide.*|.*schwedt.*|.*schweich.*|.*schweinfurt.*|.*schwelm.*|.*schwerin.*|.*schwerte.*|.*schwetzingen.*|.*sebnitz.*|.*seehausen.*|.*seehausen.*|.*seelow.*|.*seelze.*|.*seesen.*|.*sehnde.*|.*seifhennersdorf.*|.*selb.*|.*selbitz.*|.*selm.*|.*selters.*|.*senden.*|.*sendenhorst.*|.*senftenberg.*|.*seßlach.*|.*siegburg.*|.*siegen.*|.*sigmaringen.*|.*simbach am inn.*|.*simmern.*|.*hunsrück.*|.*sindelfingen.*|.*singen.*|.*sinsheim.*|.*sinzig.*|.*soest.*|.*solingen.*|.*solms.*|.*soltau.*|.*sömmerda.*|.*sondershausen.*|.*sonneberg.*|.*sonnewalde.*|.*sonthofen.*|.*sontra.*|.*spaichingen.*|.*spalt.*|.*spangenberg.*|.*spenge.*|.*speyer.*|.*spremberg.*|.*sprockhövel.*|.*st. blasien.*|.*st. georgen.*|.*st. ingbert.*|.*st. wendel.*|.*stade.*|.*starnberg.*|.*staßfurt.*|.*staufen im breisgau.*|.*staufenberg.*|.*stavenhagen.*|.*steinach.*|.*steinau.*|.*steinbach.*|.*steinfurt.*|.*steinheim.*|.*stendal.*|.*sternberg.*|.*stockach.*|.*stolberg.*|.*stollberg.*|.*stolpen.*|.*storkow.*|.*stößen.*|.*straelen.*|.*stralsund.*|.*strasburg.*|.*straubing.*|.*strausberg.*|.*strehla.*|.*stromberg.*|.*stühlingen.*|.*stutensee.*|.*stuttgart.*|.*suhl.*|.*sulingen.*|.*sulz am neckar.*|.*sulzbach-rosenberg.*|.*sulzbach.*|.*sulzburg.*|.*sundern (sauerland).*|.*süßen.*|.*syke.*|.*tambach.*|.*dietharz.*|.*tangerhütte.*|.*tangermünde.*|.*tann.*|.*tanna.*|.*tauberbischofsheim.*|.*taucha.*|.*taunusstein.*|.*tecklenburg.*|.*tegernsee.*|.*telgte.*|.*teltow.*|.*templin.*|.*tengen.*|.*tessin.*|.*teterow.*|.*tettnang.*|.*teublitz.*|.*teuchern.*|.*teupitz.*|.*teuschnitz.*|.*thale.*|.*thalheim.*|.*thannhausen.*|.*tharandt.*|.*themar.*|.*thum.*|.*tirschenreuth.*|.*titisee.*|.*tittmoning.*|.*todtnau.*|.*töging.*|.*tönisvorst.*|.*tönning.*|.*torgau.*|.*torgelow.*|.*tornesch.*|.*traben-trarbach.*|.*traunreut.*|.*traunstein.*|.*trebbin.*|.*trebsen.*|.*treffurt.*|.*trendelburg.*|.*treuchtlingen.*|.*treuen.*|.*treuenbrietzen.*|.*triberg im schwarzwald.*|.*tribsees.*|.*trier.*|.*triptis.*|.*trochtelfingen.*|.*troisdorf.*|.*trossingen.*|.*trostberg.*|.*tübingen.*|.*tuttlingen.*|.*twistringen.*|.*übach-palenberg.*|.*überlingen.*|.*uebigau-wahrenbrück.*|.*ueckermünde.*|.*uelzen.*|.*uetersen.*|.*uffenheim.*|.*uhingen.*|.*ulm.*|.*ulrichstein.*|.*unna.*|.*unstrut.*|.*unterföhring.*|.*unterschleißheim.*|.*usedom.*|.*usingen.*|.*uslar.*|.*vacha.*|.*vaihingen an der enz.*|.*vallendar.*|.*varel.*|.*vechta.*|.*velbert.*|.*velburg.*|.*velden.*|.*vellberg.*|.*vellmar.*|.*velten.*|.*verden.*|.*versmold.*|.*vetschau.*|.*viechtach.*|.*vienenburg.*|.*viernheim.*|.*viersen.*|.*villingen-schwenningen.*|.*vilsbiburg.*|.*vilseck.*|.*vilshofen an der donau.*|.*visselhövede.*|.*vlotho.*|.*voerde.*|.*vogtsburg.*|.*kaiserstuhl.*|.*vohburg.*|.*vohenstrauß.*|.*vöhrenbach.*|.*vöhringen.*|.*volkach.*|.*völklingen.*|.*volkmarsen.*|.*vreden.*|.*wachenheim an der weinstraße.*|.*wächtersbach.*|^wadern.*|.* wadern.*|.*waghäusel.*|.*wahlstedt.*|.*waiblingen.*|.*waischenfeld.*|.*waldbröl.*|.*waldeck.*|.*waldenbuch.*|.*waldenburg.*|.*waldenburg.*|.*waldershof.*|.*waldheim.*|.*waldkappel.*|.*waldkirch.*|.*waldkirchen.*|.*waldkraiburg.*|.*waldmünchen.*|.*waldsassen.*|.*waldshut-tiengen.*|.*walldorf.*|.*walldürn.*|.*wallenfels.*|.*walsrode.*|.*waltershausen.*|.*waltrop.*|.*wanfried.*|.*wangen im allgäu.*|.*wanzleben.*|.*warburg.*|.*waren.*|.*warendorf.*|.*warin.*|.*warstein.*|.*wassenberg.*|.*wasserburg am inn.*|.*wassertrüdingen.*|.*wasungen.*|.*wedel.*|.*weener.*|.*wegberg.*|.*wegeleben.*|.*weida.*|.*weiden in der oberpfalz.*|.*weikersheim.*|.*weil am rhein.*|.*weilburg.*|.*weilheim.*|.*weimar.*|.*weinheim.*|.*weinsberg.*|.*weismain.*|.*weißenberg.*|.*weißenburg.*|.*weißenfels.*|.*weißenhorn.*|.*weißensee.*|.*weißenthurm.*|.*weißwasser.*|.*weiterstadt.*|.*welzheim.*|.*welzow.*|.*wemding.*|.*wendlingen.*|.*werben.*|.*werdau.*|.*werder.*|.*werdohl.*|.*werl.*|.*wermelskirchen.*|.*wernau.*|.*werne.*|.*werneuchen.*|.*wernigerode.*|.*werra.*|.*wertheim.*|.*werther.*|.*wertingen.*|.*wesel.*|.*wesenberg.*|.*wesselburen.*|.*wesseling.*|.*westerburg.*|.*westerland.*|.*westerstede.*|.*wetter.*|.*wetter.*|.*wettin.*|.*wetzlar.*|.*widdern.*|.*wiehe.*|.*wiehl.*|.*wiesbaden.*|.*wiesensteig.*|.*wiesloch.*|.*wiesmoor.*|.*wildberg.*|.*wildemann.*|.*wildenfels.*|.*wildeshausen.*|.*wilhelmshaven.*|.*wilkau-haßlau.*|.*willebadessen.*|.*willich.*|.*wilsdruff.*|.*wilster.*|.*wilthen.*|.*windischeschenbach.*|.*windsbach.*|.*winnenden.*|.*winsen.*|.*winterberg.*|.*wipperfürth.*|.*wirges.*|.*wismar.*|.*wissen.*|.*witten.*|.*wittenberg.*|.*wittenberge.*|.*wittenburg.*|.*wittichenau.*|.*wittingen.*|.*wittlich.*|.*wittmund.*|.*wittstock.*|.*dosse.*|.*witzenhausen.*|.*woldegk.*|.*wolfach.*|.*wolfen.*|.*wolfenbüttel.*|.*wolfhagen.*|.*wolframs-eschenbach.*|.*wolfratshausen.*|.*wolfsburg.*|.*wolfstein.*|.*wolgast.*|.*wolkenstein.*|.*wolmirstedt.*|.*wörlitz.*|.*worms.*|.*wörth.*|.*wriezen.*|.*wülfrath.*|.*wunsiedel.*|.*wunstorf.*|.*wuppertal.*|.*würselen.*|.*wurzbach.*|.*würzburg.*|.*wurzen.*|.*wustrow.*|.*wyk auf föhr.*|.*xanten.*|.*zahna.*|.*zarrentin am schaalsee.*|.*zehdenick.*|.*zeil am main.*|.*zeitz.*|.*zell am.*|.*zell im.*|.*mehlis.*|.*zerbst.*|.*zeulenroda.*|.*zeven.*|.*ziegenrück.*|.*zierenberg.*|.*ziesar.*|.*zirndorf.*|.*zittau.*|.*zöblitz.*|.*zörbig.*|.*zossen.*|.*zschopau.*|.*zülpich.*|.*zweibrücken.*|.*zwenkau.*|.*zwickau.*|.*zwiesel.*|.*zwingenberg.*|.*zwönitz.*', kw_lower):
                intents.append("regional:CITY")

            # User Intent: regional:COUNTRY
            if re.search(r'.*belgien.*|.*bulgarien.*|.*dänemark.*|.*deutschland.*|.*estland.*|.*finnland.*|.*frankreich.*|.*griechenland.*|.*irland.*|.*italien.*|.*kroatien.*|.*lettland.*|.*litauen.*|.*luxemburg.*|.*malta.*|.*niederlande.*|.*österreich.*|.*polen.*|.*portugal.*|.*rumänien.*', kw_lower):
                intents.append("regional:COUNTRY")
                
        elif data_lang_choice == t["data_lang_options"][1]:
            # User Intent: KNOW
            if re.search(r'\b(who|what|where|when|why|how|which|whose|whom|guide|tutorial|tips|definition|explain|explanation|how\s+to|faq|forum|info|information|meaning|instruction|manual|example|examples|case\s+study|learn|training|course|help|support|diy|walkthrough)\b', kw_lower):
                intents.append("KNOW")
                
            # User Intent: DO (Transactional)
            if re.search(r'\b(buy|order|cheap|coupon|discount|download|free|shop|price|pricing|sale|purchase|store|promo|deal|deals|rent|hire|cheapest|voucher|booking|book)\b', kw_lower):
                intents.append("DO (Transactional)")

            # User Intent: regional:CITY
            if re.search(r'\b(near\s+me|local|nearby|map|directions|address|hours|opening\s+hours|london|new\s+york|nyc|los\s+angeles|chicago|houston|phoenix|philadelphia|dallas|san\s+diego|austin|san\s+francisco|seattle|denver|boston|miami|atlanta|las\s+vegas|toronto|vancouver|sydney|melbourne|brisbane|perth|auckland)\b', kw_lower):
                intents.append("regional:CITY")

            # User Intent: regional:COUNTRY
            if re.search(r'\b(us|usa|united\s+states|uk|united\s+kingdom|england|great\s+britain|canada|australia|nz|new\s+zealand|ireland|scotland|wales|south\s+africa)\b', kw_lower):
                intents.append("regional:COUNTRY")
                
        return ", ".join(intents) if intents else "undefined"

    if data_lang_choice == t["data_lang_options"][2]:
        df['Search Intent'] = 'not analyzed'
    else:
        df['Search Intent'] = df['Keyword'].apply(get_intent)
    
    st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)
    
    # Segments
    if metric_basis == "Clicks":
        losers = df[df['Traffic Loss'] > 0].copy()
        winners = df[df['Traffic Gain'] > 0].copy()
        top3_drops = df[(df['Position#1'] <= 3) & (df['Position#2'] > df['Position#1']) & (df['Traffic Loss'] > 0)]
        top10_drops = df[(df['Position#1'] <= 10) & (df['Position#2'] > df['Position#1']) & (df['Traffic Loss'] > 0)]
        page2_drops = df[(df['Position#1'] > 10) & (df['Position#1'] <= 20) & (df['Position#2'] > df['Position#1']) & (df['Traffic Loss'] > 0)]
        total_loss = df[(df['Position#1'] <= 100) & (df['Position#2'] > 100) & (df['Traffic Loss'] > 0)]
    else:
        # SV mode
        losers = df[df['Position Change'] < 0].copy()
        winners = df[df['Position Change'] > 0].copy()
        top3_drops = df[(df['Position#1'] <= 3) & (df['Position Change'] < 0)]
        top10_drops = df[(df['Position#1'] <= 10) & (df['Position Change'] < 0)]
        page2_drops = df[(df['Position#1'] > 10) & (df['Position#1'] <= 20) & (df['Position Change'] < 0)]
        total_loss = df[(df['Position#1'] <= 100) & (df['Position#2'] > 100)]
        
    low_hanging = df[(df['Position#2'] >= 11) & (df['Position#2'] <= 15)]
    
    # --- KPIs ---
    st.header(t["kpi_header"])
    
    # 1. Search Volume Metrics (Primary for text and rankings)
    total_sv_old = df['Search Volume'].sum()
    total_sv_loss = losers['Search Volume'].sum()
    total_sv_gained = winners['Search Volume'].sum()
    net_sv = total_sv_gained - total_sv_loss
    pct_sv_change = (net_sv / total_sv_old * 100) if total_sv_old > 0 else 0.0
    pct_sign = " %" if lang == "DE" else "%"
    
    # SV Formatted strings
    net_sv_sign = "+" if net_sv > 0 else ""
    net_sv_val_str = f"{net_sv_sign}{format_num(int(net_sv))} SV"
    pct_sv_val_str = f"{net_sv_sign}{format_num(pct_sv_change, 1)}{pct_sign}"
    
    loss_sv_pct_str = f"-{format_num(total_sv_loss / total_sv_old * 100 if total_sv_old > 0 else 0.0, 1)}{pct_sign}"
    gain_sv_pct_str = f"+{format_num(total_sv_gained / total_sv_old * 100 if total_sv_old > 0 else 0.0, 1)}{pct_sign}"
    
    loss_sv_val_str = f"-{format_num(int(total_sv_loss))} SV"
    gain_sv_val_str = f"+{format_num(int(total_sv_gained))} SV"
    
    # 2. Click-Based Metrics (Estimated Traffic)
    total_clicks_old = df['Traffic#1'].sum()
    total_clicks_loss = df['Traffic Loss'].clip(lower=0).sum()
    total_clicks_gain = df['Traffic Gain'].clip(lower=0).sum()
    net_clicks = total_clicks_gain - total_clicks_loss
    pct_clicks_change = (net_clicks / total_clicks_old * 100) if total_clicks_old > 0 else 0.0
    
    # Clicks Formatted strings
    clicks_unit = "Klicks" if lang == "DE" else "clicks"
    net_clicks_sign = "+" if net_clicks > 0 else ""
    net_clicks_val_str = f"{net_clicks_sign}{format_num(int(net_clicks))} {clicks_unit}"
    pct_clicks_val_str = f"{net_clicks_sign}{format_num(pct_clicks_change, 1)}{pct_sign}"
    
    loss_clicks_pct_str = f"-{format_num(total_clicks_loss / total_clicks_old * 100 if total_clicks_old > 0 else 0.0, 1)}{pct_sign}"
    gain_clicks_pct_str = f"+{format_num(total_clicks_gain / total_clicks_old * 100 if total_clicks_old > 0 else 0.0, 1)}{pct_sign}"
    
    loss_clicks_val_str = f"-{format_num(int(total_clicks_loss))} {clicks_unit}"
    gain_clicks_val_str = f"+{format_num(int(total_clicks_gain))} {clicks_unit}"
    
    # 3. Monetary Loss Metrics (AdWords Equivalent Value)
    total_value_old = (df['Traffic#1'] * df['CPC']).sum()
    total_value_loss = df['Lost Value €'].sum()  # Already clipped at 0 in dataframe
    pct_value_change = (total_value_loss / total_value_old * 100) if total_value_old > 0 else 0.0
    
    value_val_str = f"-{format_num(total_value_loss, 2)} €" if lang == "DE" else f"-€{format_num(total_value_loss, 2)}"
    value_pct_str = f"-{format_num(pct_value_change, 1)}{pct_sign}"
    
    # 4. Segment Drops (using SV)
    top3_count = len(top3_drops)
    top3_loss_val = top3_drops['Search Volume'].sum()
    top3_pct = (top3_loss_val / total_sv_old * 100) if total_sv_old > 0 else 0.0
    top3_loss_str = f"-{format_num(int(top3_loss_val))} SV (-{format_num(top3_pct, 1)}{pct_sign})"
    top3_loss_only = f"{format_num(int(top3_loss_val))} SV"
    
    top10_count = len(top10_drops)
    top10_loss_val = top10_drops['Search Volume'].sum()
    top10_pct = (top10_loss_val / total_sv_old * 100) if total_sv_old > 0 else 0.0
    top10_loss_str = f"-{format_num(int(top10_loss_val))} SV (-{format_num(top10_pct, 1)}{pct_sign})"
    top10_loss_only = f"{format_num(int(top10_loss_val))} SV"
    
    total_loss_count = len(total_loss)
    total_loss_loss_val = total_loss['Search Volume'].sum()
    total_loss_pct = (total_loss_loss_val / total_sv_old * 100) if total_sv_old > 0 else 0.0
    total_loss_loss_str = f"-{format_num(int(total_loss_loss_val))} SV (-{format_num(total_loss_pct, 1)}{pct_sign})"
    total_loss_loss_only = f"{format_num(int(total_loss_loss_val))} SV"
    
    lhf_count = len(low_hanging)
    lhf_search_vol = int(low_hanging['Search Volume'].sum())
    lhf_sv = format_num(lhf_search_vol)
    lhf_pct = (lhf_search_vol / total_sv_old * 100) if total_sv_old > 0 else 0.0
    lhf_delta_str = f"+{lhf_sv} SV (+{format_num(lhf_pct, 1)}{pct_sign})"
    
    avg_pos_change_sign = "+" if avg_pos_change > 0 else ""
    avg_pos_change_val_str = f"{avg_pos_change_sign}{format_num(avg_pos_change, 2)}"
    avg_pos_change_delta_str = f"+{gained_keywords_count} / -{lost_keywords_count} KWs"

    if lang == "DE":
        story_text = f"""<p style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1rem;'>
Im Vergleich vom <strong>{date_old.strftime('%d.%m.%Y')}</strong> zum <strong>{date_new.strftime('%d.%m.%Y')}</strong> verzeichnete Ihre Website folgende Ranking-Entwicklungen:
</p>

<h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Ranking-Veränderungen (Positions-Daten):</h4>
<ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
<li style='margin-bottom: 0.5rem;'>
<strong>Positions-Gewinne:</strong> <span style='font-weight: bold;'>{format_num(gained_keywords_count)} Keywords</span> haben sich im Ranking verbessert (im Durchschnitt um <span style='color: #90c274; font-weight: bold;'>+{format_num(avg_gain_pos, 1)} Positionen</span>, Gesamt-Suchvolumen: <span style='font-weight: bold;'>{format_num(gained_keywords_sv)} SV</span>).
</li>
<li style='margin-bottom: 0.5rem;'>
<strong>Positions-Verluste:</strong> <span style='font-weight: bold;'>{format_num(lost_keywords_count)} Keywords</span> haben sich im Ranking verschlechtert (im Durchschnitt um <span style='color: #d28063; font-weight: bold;'>-{format_num(avg_loss_pos, 1)} Positionen</span>, Gesamt-Suchvolumen: <span style='font-weight: bold;'>{format_num(lost_keywords_sv)} SV</span>).
</li>
<li style='margin-bottom: 0.5rem;'>
<strong>Gesamt-Tendenz:</strong> Die durchschnittliche Positions-Veränderung über alle Keywords beträgt <span style='font-weight: bold; color: {"#90c274" if avg_pos_change > 0 else "#d28063"};'>{"+" if avg_pos_change > 0 else ""}{format_num(avg_pos_change, 2)} Positionen</span> (Gesamt-Suchvolumen aller Keywords: <span style='font-weight: bold;'>{format_num(total_sv)} SV</span>).
</li>
</ul>

<h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Haupttreiber der Ranking-Abstürze:</h4>
<ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
<li style='margin-bottom: 0.5rem;'>
<strong>Abstürze aus den Top 3:</strong> <span style='font-weight: bold;'>{format_num(top3_count)} Keywords</span> verloren Top-Positionen (Verlust von <span style='color: #d28063; font-weight: bold;'>{top3_loss_only}</span>).
</li>
<li style='margin-bottom: 0.5rem;'>
<strong>Abstürze aus den Top 10:</strong> Weitere <span style='font-weight: bold;'>{format_num(top10_count)} Keywords</span> fielen von Seite 1 (Verlust von <span style='color: #d28063; font-weight: bold;'>{top10_loss_only}</span>).
</li>
<li style='margin-bottom: 0.5rem;'>
<strong>Vollständige Ranking-Verluste:</strong> Insgesamt sind <span style='font-weight: bold;'>{format_num(total_loss_count)} Keywords</span> komplett aus den Top 100 herausgefallen (Verlust von <span style='color: #d28063; font-weight: bold;'>{total_loss_loss_only}</span>).
</li>
</ul>

<h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Quick-Wins / Handlungsempfehlungen:</h4>
<ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
<li>
Ich empfehle Ihnen die On-Page-Optimierung für die <strong style='color: #90c274;'>{format_num(lhf_count)} Schwellen-Keywords (Low Hanging Fruits)</strong> auf den Positionen 11-15. Diese Keywords weisen bereits ein beträchtliches <strong>Suchvolumen von {lhf_sv} SV</strong> auf der zweiten Ergebnisseite auf. Mit gezielten inhaltlichen Anpassungen können Sie diese schnell auf Seite 1 heben.
</li>
</ul>"""
        story_title = "Executive Summary & Marketing-Story"
    else:
        story_text = f"""<p style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.6; font-size: 0.95rem; margin-bottom: 1rem;'>
Comparing <strong>{date_old.strftime('%d.%m.%Y')}</strong> to <strong>{date_new.strftime('%d.%m.%Y')}</strong>, your website recorded the following ranking developments:
</p>

<h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Ranking Changes (Position Data):</h4>
<ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
<li style='margin-bottom: 0.5rem;'>
<strong>Position Gains:</strong> <span style='font-weight: bold;'>{format_num(gained_keywords_count)} keywords</span> improved in rankings (by <span style='color: #90c274; font-weight: bold;'>+{format_num(avg_gain_pos, 1)} positions</span> on average, total search volume: <span style='font-weight: bold;'>{format_num(gained_keywords_sv)} SV</span>).
</li>
<li style='margin-bottom: 0.5rem;'>
<strong>Position Losses:</strong> <span style='font-weight: bold;'>{format_num(lost_keywords_count)} keywords</span> deteriorated in rankings (by <span style='color: #d28063; font-weight: bold;'>-{format_num(avg_loss_pos, 1)} positions</span> on average, total search volume: <span style='font-weight: bold;'>{format_num(lost_keywords_sv)} SV</span>).
</li>
<li style='margin-bottom: 0.5rem;'>
<strong>Overall Trend:</strong> The average position change across all keywords is <span style='font-weight: bold; color: {"#90c274" if avg_pos_change > 0 else "#d28063"};'>{"+" if avg_pos_change > 0 else ""}{format_num(avg_pos_change, 2)} positions</span> (total search volume of all keywords: <span style='font-weight: bold;'>{format_num(total_sv)} SV</span>).
</li>
</ul>

<h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Main Drivers of Ranking Drops:</h4>
<ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
<li style='margin-bottom: 0.5rem;'>
<strong>Drops from Top 3:</strong> <span style='font-weight: bold;'>{format_num(top3_count)} keywords</span> lost top positions (loss of <span style='color: #d28063; font-weight: bold;'>{top3_loss_only}</span>).
</li>
<li style='margin-bottom: 0.5rem;'>
<strong>Drops from Top 10:</strong> An additional <span style='font-weight: bold;'>{format_num(top10_count)} keywords</span> fell off page 1 (loss of <span style='color: #d28063; font-weight: bold;'>{top10_loss_only}</span>).
</li>
<li style='margin-bottom: 0.5rem;'>
<strong>Complete Ranking Losses:</strong> In total, <span style='font-weight: bold;'>{format_num(total_loss_count)} keywords</span> dropped out of the Top 100 entirely (loss of <span style='color: #d28063; font-weight: bold;'>{total_loss_loss_only}</span>).
</li>
</ul>

<h4 style='font-family: "Raleway", sans-serif; font-weight: 700; color: #232323; margin-top: 1rem; margin-bottom: 0.5rem;'>Quick-Wins / Actionable Recommendations:</h4>
<ul style='font-family: "Open Sans", sans-serif; color: #444444; line-height: 1.5; font-size: 0.95rem; padding-left: 1.2rem; margin-top: 0;'>
<li>
I recommend focusing on the <strong style='color: #90c274;'>{format_num(lhf_count)} Threshold Keywords (Low Hanging Fruits)</strong> currently ranking on positions 11-15. These already represent a significant <strong>search volume of {lhf_sv} SV</strong> on page 2. With targeted on-page adjustments, you can easily push them to page 1 to gain traffic.
</li>
</ul>"""
        story_title = "Executive Summary & Marketing Story"

    kpi_col1, kpi_col2 = st.columns([5, 3])
    
    with kpi_col1:
        with st.container(border=True, key="exec_summary_container"):
            st.markdown(
                f"""<h3 style='margin-top: 0; margin-bottom: 1rem; font-family: "Raleway", sans-serif; font-weight: 800; color: #232323;'>
{story_title}
</h3>
{story_text}""", 
                unsafe_allow_html=True
            )
            
            # Callbacks to switch tabs programmatically with scrolling
            def select_lhf_tab():
                st.session_state["main_tabs"] = t["tab_lhf"]
                st.query_params["tab"] = "lhf"
                st.session_state["scroll_target"] = "low-hanging-fruits"
                st.session_state["show_custom_loader"] = True

            def select_top3_tab():
                st.session_state["main_tabs"] = t["tab_drops"]
                st.query_params["tab"] = "top3"
                st.session_state["scroll_target"] = "top3-drops"
                st.session_state["show_custom_loader"] = True

            def select_top10_tab():
                st.session_state["main_tabs"] = t["tab_drops"]
                st.query_params["tab"] = "top10"
                st.session_state["scroll_target"] = "top10-drops"
                st.session_state["show_custom_loader"] = True

            # Render action buttons in a row inside the container
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                label_t3 = "Top 3 Drops" if lang == "EN" else "Top 3 Abstürze"
                st.button(label_t3, key="goto_top3_btn", on_click=select_top3_tab, type="secondary", use_container_width=True)
            with b_col2:
                label_t10 = "Top 10 Drops" if lang == "EN" else "Top 10 Abstürze"
                st.button(label_t10, key="goto_top10_btn", on_click=select_top10_tab, type="secondary", use_container_width=True)
            with b_col3:
                label_lhf = "Low Hanging Fruits"
                st.button(label_lhf, key="goto_lhf_btn", on_click=select_lhf_tab, type="secondary", use_container_width=True)

    with kpi_col2:
        # Row 1: Net Change SV & Net Change Traffic
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.metric(t["kpi_net_change_sv"], net_sv_val_str, delta=pct_sv_val_str)
        with row1_col2:
            st.metric(t["kpi_net_change"], net_clicks_val_str, delta=pct_clicks_val_str)
            
        # Row 2: Lost SV & Gained SV
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.metric(t["kpi_lost_total_sv"], loss_sv_val_str, delta=loss_sv_pct_str, delta_color="normal")
        with row2_col2:
            st.metric(t["kpi_gained_total_sv"], gain_sv_val_str, delta=gain_sv_pct_str, delta_color="normal")
            
        # Row 3: Top 3 Drops & Top 10 Drops
        row3_col1, row3_col2 = st.columns(2)
        with row3_col1:
            st.metric(t["kpi_top3_drops"], format_num(top3_count), delta=top3_loss_str, delta_color="normal")
        with row3_col2:
            st.metric(t["kpi_top10_drops"], format_num(top10_count), delta=top10_loss_str, delta_color="normal")
            
        # Row 4: Complete Losses & Monetary Loss
        row4_col1, row4_col2 = st.columns(2)
        with row4_col1:
            st.metric(t["kpi_total_loss"], format_num(total_loss_count), delta=total_loss_loss_str, delta_color="normal", help=t.get("kpi_total_loss_help", ""))
        with row4_col2:
            st.metric(t["kpi_value_total"], value_val_str, delta=value_pct_str, delta_color="normal")
            
        # Row 5: Avg Position Change & Low Hanging Fruits
        row5_col1, row5_col2 = st.columns(2)
        with row5_col1:
            st.metric(t["kpi_avg_pos_change"], avg_pos_change_val_str, delta=avg_pos_change_delta_str, delta_color="off")
        with row5_col2:
            st.metric(t["kpi_lhf"], format_num(lhf_count), delta=lhf_delta_str, delta_color="off", help=t["kpi_lhf_help"])
        
    st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)
    
    viz_col1, viz_col2 = st.columns(2)
    with viz_col1:
        st.markdown("#### " + t["kpi_cluster_title"])
        cluster_net = df.groupby('Cluster')['Metric Change'].sum().reset_index()
        cluster_net = cluster_net[cluster_net['Cluster'] != "undefined"]
        
        if not cluster_net.empty:
            best_cluster = cluster_net.loc[cluster_net['Metric Change'].idxmax()]
            worst_cluster = cluster_net.loc[cluster_net['Metric Change'].idxmin()]
            
            best_pct = (best_cluster['Metric Change'] / total_metric_old * 100) if total_metric_old > 0 else 0.0
            worst_pct = (worst_cluster['Metric Change'] / total_metric_old * 100) if total_metric_old > 0 else 0.0
            
            best_sign = "+" if best_cluster['Metric Change'] > 0 else ""
            worst_sign = "+" if worst_cluster['Metric Change'] > 0 else ""
            best_pct_sign = "+" if best_pct > 0 else ""
            worst_pct_sign = "+" if worst_pct > 0 else ""
            
            best_delta = f"{best_sign}{format_num(int(best_cluster['Metric Change']))} {metric_unit} ({best_pct_sign}{format_num(best_pct, 1)}{pct_sign})"
            worst_delta = f"{worst_sign}{format_num(int(worst_cluster['Metric Change']))} {metric_unit} ({worst_pct_sign}{format_num(worst_pct, 1)}{pct_sign})"
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(t["kpi_best_cluster"], best_cluster['Cluster'], delta=best_delta)
            with c2:
                st.metric(t["kpi_worst_cluster"], worst_cluster['Cluster'], delta=worst_delta)
                
            top_bottom = pd.concat([cluster_net.nlargest(3, 'Metric Change'), cluster_net.nsmallest(3, 'Metric Change')]).drop_duplicates()
            top_bottom = top_bottom.sort_values('Metric Change')
            fig_net = px.bar(
                top_bottom, x='Metric Change', y='Cluster', orientation='h',
                color='Metric Change', color_continuous_scale=[[0.0, '#d28063'], [0.5, '#ffed00'], [1.0, '#90c274']],
                height=200
            )
            style_plotly_fig(fig_net)
            fig_net.update_layout(margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_net, use_container_width=True)

    with viz_col2:
        st.markdown("#### " + t["kpi_top3_title"])
        if not top3_drops.empty:
            worst_top3 = top3_drops.nlargest(5, 'Metric Loss').sort_values('Metric Loss', ascending=True)
            fig_t3 = px.bar(
                worst_top3, x='Metric Loss', y='Keyword', orientation='h',
                color_discrete_sequence=['#d28063'], height=270
            )
            style_plotly_fig(fig_t3)
            fig_t3.update_layout(margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_t3, use_container_width=True)
        else:
            st.info(t["rd_t3_empty"])
            
    st.write("")
    if data_lang_choice == t["data_lang_options"][2]:
        st.info(t["intent_not_analyzed_msg"])
    else:
        viz_col3, viz_col4 = st.columns(2)
        with viz_col3:
            st.markdown("#### " + t["kpi_intent_title"])
            # Split multiple intents per keyword
            intent_df = df.assign(Intent=df['Search Intent'].str.split(', ')).explode('Intent')
            intent_counts = intent_df['Intent'].value_counts().reset_index()
            intent_counts.columns = ['Search Intent', 'Count']
            
            color_map = {
                "DO (Transactional)": "#90c274",
                "KNOW": "#2ea3f2",
                "regional:CITY": "#ffed00",
                "regional:COUNTRY": "#f29e2e",
                "undefined": "#dfdfdf"
            }
            
            fig_pie = px.pie(
                intent_counts, values='Count', names='Search Intent',
                color='Search Intent', color_discrete_map=color_map,
                hole=0.4,
                height=280
            )
            style_plotly_fig(fig_pie)
            fig_pie.update_layout(margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with viz_col4:
            st.markdown("#### Details" if lang == "EN" else "#### Details")
            intent_pct = intent_df['Intent'].value_counts(normalize=True).reset_index()
            intent_pct.columns = ['Search Intent', 'Percentage']
            intent_pct['Percentage'] = intent_pct['Percentage'] * 100
            
            intent_summary = pd.merge(intent_counts, intent_pct, on='Search Intent')
            col_intent = 'Search Intent' if lang == 'EN' else 'Suchintent'
            col_count = 'Keywords (Count)' if lang == 'EN' else 'Keywords (Anzahl)'
            col_share = 'Share (%)' if lang == 'EN' else 'Anteil (%)'
            intent_summary.columns = [col_intent, col_count, col_share]
            
            formatted_intent_summary = intent_summary.copy()
            formatted_intent_summary[col_count] = formatted_intent_summary[col_count].apply(lambda x: format_num(x))
            pct_sign = " %" if lang == "DE" else "%"
            formatted_intent_summary[col_share] = formatted_intent_summary[col_share].apply(lambda x: f"{format_num(x, 1)}{pct_sign}")
            
            st.write("")
            st.dataframe(formatted_intent_summary, use_container_width=True, hide_index=True)
            
    st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)

    def display_styled_dataframe(df_to_show, sort_col, ascending=False):
        loss_cols = [c for c in ['Traffic Loss', 'Lost Value €'] if c in df_to_show.columns]
        gain_cols = [c for c in ['Traffic Gain'] if c in df_to_show.columns]
        
        styler = df_to_show.sort_values(sort_col, ascending=ascending).style
        format_dict = {}
        
        if loss_cols:
            styler = styler.map(lambda x: 'color: #d28063; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=loss_cols)
            for c in loss_cols:
                if c == 'Lost Value €':
                    if lang == "EN":
                        format_dict[c] = lambda x: f"▼ -€{format_num(x, 2)}" if pd.notnull(x) and x > 0 else ("€0.00" if pd.notnull(x) else "")
                    else:
                        format_dict[c] = lambda x: f"▼ -{format_num(x, 2)} €" if pd.notnull(x) and x > 0 else ("0,00 €" if pd.notnull(x) else "")
                else:
                    format_dict[c] = lambda x: f"▼ -{format_num(x)}" if pd.notnull(x) and x > 0 else ("0" if pd.notnull(x) else "")
                
        if gain_cols:
            styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=gain_cols)
            for c in gain_cols:
                format_dict[c] = lambda x: f"▲ +{format_num(x)}" if pd.notnull(x) and x > 0 else ("0" if pd.notnull(x) else "")
                
        for c in ['Search Volume', 'Traffic#1', 'Traffic#2']:
            if c in df_to_show.columns:
                format_dict[c] = lambda x: format_num(x) if pd.notnull(x) else ""
                
        for c in ['Position#1', 'Position#2']:
            if c in df_to_show.columns:
                format_dict[c] = lambda x: "-" if pd.notnull(x) and x == 101 else (format_num(x, 2) if pd.notnull(x) else "")
        
        if 'Position Change' in df_to_show.columns:
            styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else ('color: #d28063; font-weight: bold;' if pd.notnull(x) and x < 0 else ''), subset=['Position Change'])
            format_dict['Position Change'] = lambda x: f"▲ +{format_num(abs(x), 2)}" if pd.notnull(x) and x > 0 else (f"▼ -{format_num(abs(x), 2)}" if pd.notnull(x) and x < 0 else format_num(0.0, 2))
            
        if 'Traffic Change' in df_to_show.columns:
            styler = styler.map(lambda x: 'color: #90c274; font-weight: bold;' if pd.notnull(x) and x > 0 else ('color: #d28063; font-weight: bold;' if pd.notnull(x) and x < 0 else ''), subset=['Traffic Change'])
            format_dict['Traffic Change'] = lambda x: f"▲ +{format_num(x)}" if pd.notnull(x) and x > 0 else (f"▼ -{format_num(abs(x))}" if pd.notnull(x) and x < 0 else "0")
                
        styler = styler.format(format_dict)
        st.dataframe(styler, use_container_width=True)

    # Callback when user switches tab manually to keep query params in sync
    def on_tab_change():
        active_tab = st.session_state.get("main_tabs")
        if active_tab == t["tab_lhf"]:
            st.query_params["tab"] = "lhf"
        elif active_tab == t["tab_drops"]:
            st.query_params["tab"] = "drops"
        else:
            if "tab" in st.query_params:
                del st.query_params["tab"]

    # Handle deep-linking on initial load / rerun
    if "tab" in st.query_params and "main_tabs" not in st.session_state:
        param_val = st.query_params["tab"]
        if param_val == "lhf":
            st.session_state["main_tabs"] = t["tab_lhf"]
            st.session_state["scroll_target"] = "low-hanging-fruits"
        elif param_val == "top3":
            st.session_state["main_tabs"] = t["tab_drops"]
            st.session_state["scroll_target"] = "top3-drops"
        elif param_val == "top10":
            st.session_state["main_tabs"] = t["tab_drops"]
            st.session_state["scroll_target"] = "top10-drops"
        elif param_val == "drops":
            st.session_state["main_tabs"] = t["tab_drops"]

    st.header("Details" if lang == "DE" else "Details")
    
    tab_d, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t["tab_dir"],
        t["tab_cluster"],
        t["tab_drops"],
        t["tab_lhf"],
        t["tab_winners"],
        t["tab_all"]
    ], key="main_tabs", on_change=on_tab_change)
    
    with tab_d:
        st.subheader(t["dir_sub"])
        if not top10_drops.empty:
            dir_vol = top10_drops.groupby('Directory').agg(
                Metric_Loss=('Metric Loss', 'sum'),
                Value_Loss=('Lost Value €', 'sum')
            ).reset_index()
            dir_vol = dir_vol[dir_vol['Metric_Loss'] > 0].sort_values('Metric_Loss', ascending=False).head(15)
            
            fig = px.bar(dir_vol, x='Directory', y='Metric_Loss', 
                         title=t["dir_chart_title_sv"] if metric_basis == "SV" else t["dir_chart_title"],
                         labels={'Directory': t["dir_chart_label_d"], 'Metric_Loss': t["dir_chart_label_t_sv"] if metric_basis == "SV" else t["dir_chart_label_t"]},
                         hover_data=['Value_Loss'] if metric_basis == "Clicks" else [],
                         color='Metric_Loss', color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#d28063']])
            style_plotly_fig(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t["dir_empty"])

    with tab1:
        st.subheader(t["cl_sub"])
        st.markdown(t["cl_desc"])
        
        if not losers.empty:
            cluster_vol = losers.groupby('Cluster').agg(
                Metric_Loss=('Metric Loss', 'sum'),
                Value_Loss=('Lost Value €', 'sum'),
                Keyword_Count=('Keyword', 'count')
            ).reset_index()
            cluster_vol = cluster_vol[cluster_vol['Metric_Loss'] > 0].sort_values('Metric_Loss', ascending=False)
            
            fig_cluster = px.bar(cluster_vol, x='Cluster', y='Metric_Loss', 
                         title=t["cl_chart_title_sv"] if metric_basis == "SV" else t["cl_chart_title"],
                         labels={'Cluster': t["cl_chart_label_c"], 'Metric_Loss': t["cl_chart_label_t_sv"] if metric_basis == "SV" else t["cl_chart_label_t"]},
                         hover_data=['Value_Loss', 'Keyword_Count'] if metric_basis == "Clicks" else ['Keyword_Count'],
                         color='Metric_Loss', color_continuous_scale=[[0.0, '#dfdfdf'], [1.0, '#d28063']])
            style_plotly_fig(fig_cluster)
            st.plotly_chart(fig_cluster, use_container_width=True)
            
            st.markdown(t["cl_detail"])
            opts = [c for c in cluster_vol['Cluster'].tolist() if c != "undefined"] + ["undefined"]
            selected_clusters = st.multiselect(t["cl_select"], options=opts)
            if selected_clusters:
                cluster_df = losers[losers['Cluster'].isin(selected_clusters)]
                st.write(f"{t['cl_sum']} **{format_num(int(cluster_df['Search Volume'].sum()))}**")
                display_styled_dataframe(cluster_df[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume' if metric_basis == "SV" else 'Traffic Loss')
        else:
            st.info(t["cl_empty"])

    with tab2:
        st.subheader(t["rd_sub"])
        kw_filter = st.text_input(t["rd_filter"]).strip().lower()
        
        f_top3 = top3_drops[top3_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top3_drops
        f_top10 = top10_drops[top10_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top10_drops
        f_page2 = page2_drops[page2_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else page2_drops
        f_total = total_loss[total_loss['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else total_loss
        
        st.markdown("<div id='top3-drops'></div>", unsafe_allow_html=True)
        st.markdown(t["rd_t3_title"])
        if not f_top3.empty:
            top3_sub_str = f"{t['rd_sum_vol']} **{format_num(int(f_top3['Search Volume'].sum()))}**"
            if metric_basis == "Clicks":
                top3_sub_str += f" {t['rd_sum_traf']} {format_num(int(f_top3['Traffic Loss'].sum()))})"
            st.write(top3_sub_str)
            display_styled_dataframe(f_top3[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume' if metric_basis == "SV" else 'Traffic Loss')
        else:
            st.info(t["rd_t3_empty"])
            
        st.markdown("<div id='top10-drops'></div>", unsafe_allow_html=True)
        st.markdown(t["rd_t10_title"])
        if not f_top10.empty:
            top10_sub_str = f"{t['rd_sum_vol']} **{format_num(int(f_top10['Search Volume'].sum()))}**"
            if metric_basis == "Clicks":
                top10_sub_str += f" {t['rd_sum_traf']} {format_num(int(f_top10['Traffic Loss'].sum()))})"
            st.write(top10_sub_str)
            display_styled_dataframe(f_top10[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume' if metric_basis == "SV" else 'Traffic Loss')
        else:
            st.info(t["rd_t10_empty"])
            
        st.markdown(t["rd_p2_title"])
        if not f_page2.empty:
            page2_sub_str = f"{t['rd_sum_vol']} **{format_num(int(f_page2['Search Volume'].sum()))}**"
            if metric_basis == "Clicks":
                page2_sub_str += f" {t['rd_sum_traf']} {format_num(int(f_page2['Traffic Loss'].sum()))})"
            st.write(page2_sub_str)
            display_styled_dataframe(f_page2[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume' if metric_basis == "SV" else 'Traffic Loss')
        else:
            st.info(t["rd_p2_empty"])
            
        st.markdown(t["rd_100_title"])
        if not f_total.empty:
            total_sub_str = f"{t['rd_sum_vol']} **{format_num(int(f_total['Search Volume'].sum()))}**"
            if metric_basis == "Clicks":
                total_sub_str += f" {t['rd_sum_traf']} {format_num(int(f_total['Traffic Loss'].sum()))})"
            st.write(total_sub_str)
            display_styled_dataframe(f_total[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Search Volume' if metric_basis == "SV" else 'Traffic Loss')
        else:
            st.info(t["rd_100_empty"])

    with tab3:
        st.subheader(t["lhf_sub"], anchor="low-hanging-fruits")
        st.markdown(t["lhf_desc"])
        if not low_hanging.empty:
            display_styled_dataframe(low_hanging[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory']], sort_col='Search Volume', ascending=False)
        else:
            st.info(t["lhf_empty"])
            
    with tab4:
        st.subheader(t["win_sub"])
        if not winners.empty:
            display_styled_dataframe(winners[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Gain', 'Directory']], sort_col='Search Volume' if metric_basis == "SV" else 'Traffic Gain')
            
            fig_win = px.scatter(
                winners, x="Search Volume", y="Position#2", 
                size="Search Volume" if metric_basis == "SV" else "Traffic Gain", color="Directory",
                hover_name="Keyword", title=t["win_chart_title"],
                labels={'Position#2': t["win_chart_label_pos"]},
                color_discrete_sequence=['#2ea3f2', '#90c274', '#e2a312', '#993333', '#797979']
            )
            fig_win.update_yaxes(autorange="reversed")
            style_plotly_fig(fig_win)
            st.plotly_chart(fig_win, use_container_width=True)
        else:
            st.info(t["win_empty"])

    with tab5:
        st.subheader(t["ad_sub"])
        
        f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
        
        all_clusters = sorted([c for c in df['Cluster'].dropna().unique() if c != 'undefined']) + ['undefined']
        with f_col1:
            sel_clusters = st.multiselect(t["ad_filter_cluster"], options=all_clusters)
            
        with f_col2:
            is_disabled = (data_lang_choice == t["data_lang_options"][2])
            all_intents = set()
            for val in df['Search Intent'].dropna().unique():
                for piece in val.split(', '):
                    all_intents.add(piece)
            all_intents = sorted(list(all_intents))
            sel_intents = st.multiselect(t["ad_filter_intent"], options=all_intents, disabled=is_disabled)
            
        all_changes = sorted(df['Change'].unique().tolist())
        with f_col3:
            sel_changes = st.multiselect(t["ad_filter_change"], options=all_changes)
            
        all_dirs = sorted(df['Directory'].unique().tolist())
        with f_col4:
            sel_dirs = st.multiselect(t["ad_filter_dir"], options=all_dirs)
            
        with f_col5:
            search_kw = st.text_input(t["ad_filter_kw"]).strip().lower()
            
        filtered_df = df.copy()
        if sel_clusters:
            filtered_df = filtered_df[filtered_df['Cluster'].isin(sel_clusters)]
        if sel_intents:
            filtered_df = filtered_df[filtered_df['Search Intent'].apply(lambda x: any(c in x for c in sel_intents))]
        if sel_changes:
            filtered_df = filtered_df[filtered_df['Change'].isin(sel_changes)]
        if sel_dirs:
            filtered_df = filtered_df[filtered_df['Directory'].isin(sel_dirs)]
        if search_kw:
            filtered_df = filtered_df[filtered_df['Keyword'].astype(str).str.lower().str.contains(search_kw, na=False)]
            
        all_cols = ['Cluster', 'Search Intent', 'Directory', 'Keyword', 'Change', 'Position Change', 'Traffic Change', 'Lost Value €', 'Position#1', 'Position#2', 'Search Volume', 'Traffic#1', 'Traffic#2', 'URL']
        all_cols = [c for c in all_cols if c in filtered_df.columns]
        
        display_styled_dataframe(filtered_df[all_cols], sort_col='Position Change' if metric_basis == "SV" else 'Traffic Change', ascending=True)

else:
    st.info(t.get("info_upload", "Bitte lade eine Sistrix CSV-Datei hoch und klicke auf 'Analysieren'."))

# Footer
st.markdown("<hr class='hr--grey'>", unsafe_allow_html=True)

version = "v1.0.0"
try:
    import subprocess
    commit_count = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    if commit_count and commit_hash:
        version = f"v1.0.{commit_count} ({commit_hash})"
except Exception:
    pass

footer_text = f"{t['footer']} | <span style='opacity: 0.8;'>Version {version}</span>"
st.markdown(
    f"<div style='text-align: center; color: #797979; font-size: 0.9em;'>{footer_text}</div>", 
    unsafe_allow_html=True
)

# Clear custom loader state at the end of the run
if st.session_state.get("show_custom_loader"):
    st.session_state["show_custom_loader"] = False
    loading_placeholder.empty()

# Execute smooth scroll down to selected target if flag is set
if st.session_state.get("scroll_target"):
    target_id = st.session_state["scroll_target"]
    components.html(
        f"""<script>
        setTimeout(function() {{
            var el = window.parent.document.getElementById("{target_id}");
            if (el) {{
                el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        }}, 300);
        </script>""",
        height=0
    )
    st.session_state["scroll_target"] = None
