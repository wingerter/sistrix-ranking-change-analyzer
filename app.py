import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from urllib.parse import urlparse
import io
import re
from collections import Counter

st.set_page_config(page_title="Sistrix Ranking Changes Analyzer", layout="wide")

# --- i18n Translations ---
lang_choice = st.sidebar.radio("Language / Sprache", ["🇩🇪 DE", "🇬🇧 EN"], index=0)
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
        "kpi_lost_total": "Lost Traffic (Total)",
        "kpi_value_total": "Monetary Loss (Total)",
        "kpi_gained_total": "Gained Traffic (Total)",
        "kpi_net_change": "Net Traffic Change",
        "kpi_top3_drops": "Top 3 Drops",
        "kpi_top10_drops": "Top 10 Drops",
        "kpi_lhf": "Low Hanging Fruits",
        "kpi_lhf_link": "👉 See tab below",
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
        "rd_filter": "🔍 Filter by keyword (optional):",
        "rd_t3_title": "#### 1. Top 3 Drops (Fell out of Top 3)",
        "rd_t3_empty": "No Top 3 Drops found.",
        "rd_t10_title": "#### 2. Top 10 Drops (Fell out of Top 10)",
        "rd_t10_empty": "No Top 10 Drops found.",
        "rd_p2_title": "#### 3. Page 2 Drops (Dropped from Page 2 further back)",
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
        
        "traffic": "Traffic"
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
        "kpi_lost_total": "Verlorener Traffic (Schätzung)",
        "kpi_value_total": "Monetärer Verlust (AdWords Äquiv.)",
        "kpi_gained_total": "Gewonnener Traffic (Schätzung)",
        "kpi_net_change": "Netto Traffic-Veränderung",
        "kpi_top3_drops": "Top 3 Abstürze",
        "kpi_top10_drops": "Top 10 Abstürze",
        "kpi_lhf": "Low Hanging Fruits",
        "kpi_lhf_link": "👉 Siehe Reiter unten",
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
        "rd_filter": "🔍 Nach Keyword filtern (optional):",
        "rd_t3_title": "#### 1. Top 3 Drops (Aus Top 3 gerutscht)",
        "rd_t3_empty": "Keine Top 3 Drops gefunden.",
        "rd_t10_title": "#### 2. Top 10 Drops (Aus Top 10 gerutscht)",
        "rd_t10_empty": "Keine Top 10 Drops gefunden.",
        "rd_p2_title": "#### 3. Seite 2 Drops (Von Seite 2 weiter nach hinten)",
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
    }
}

t = translations[lang]

st.title(t["title"])
st.markdown(t["subtitle"])

# Sidebar - Settings
st.sidebar.header(t["sidebar_data"])

uploaded_file = st.sidebar.file_uploader(t["upload_label"], type=["csv"])

st.sidebar.subheader(t["dates_header"])
date_old = st.sidebar.date_input(t["date_old"], value=pd.to_datetime('today') - pd.DateOffset(months=1))
date_new = st.sidebar.date_input(t["date_new"], value=pd.to_datetime('today'))

st.sidebar.subheader(t["cluster_settings"])
brand_input = st.sidebar.text_input(t["brand_input"], value="", help=t["brand_help"])
num_clusters = st.sidebar.slider(t["cluster_count"], min_value=5, max_value=50, value=20, step=5)

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

if uploaded_file is not None:
    if st.sidebar.button(t["btn_analyze"], type="primary"):
        st.session_state['analyzed'] = True

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
    
    st.write("---")
    
    # Segments
    losers = df[df['Traffic Loss'] > 0].copy()
    top3_drops = df[(df['Position#1'] <= 3) & (df['Position#2'] > 3) & (df['Traffic Loss'] > 0)]
    top10_drops = df[(df['Position#1'] <= 10) & (df['Position#2'] > 10) & (df['Traffic Loss'] > 0)]
    page2_drops = df[(df['Position#1'] > 10) & (df['Position#1'] <= 20) & (df['Position#2'] > 20) & (df['Traffic Loss'] > 0)]
    total_loss = df[(df['Position#1'] <= 100) & (df['Position#2'] > 100) & (df['Traffic Loss'] > 0)]
    low_hanging = df[(df['Position#2'] >= 11) & (df['Position#2'] <= 15)]
    winners = df[df['Traffic Gain'] > 0].copy()
    
    # --- KPIs ---
    st.header(t["kpi_header"])
    
    total_traffic_loss = int(losers['Traffic Loss'].sum())
    total_value_loss = losers['Lost Value €'].sum()
    total_traffic_gained = int(winners['Traffic Gain'].sum())
    net_traffic = total_traffic_gained - total_traffic_loss
    lhf_search_vol = int(low_hanging['Search Volume'].sum())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t["kpi_lost_total"], f"-{total_traffic_loss:,}".replace(',', '.'))
    with col2:
        st.metric(t["kpi_value_total"], f"-{total_value_loss:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'))
    with col3:
        st.metric(t["kpi_gained_total"], f"+{total_traffic_gained:,}".replace(',', '.'))
        
    st.write("")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(t["kpi_top3_drops"], len(top3_drops), delta=f"-{int(top3_drops['Traffic Loss'].sum())} {t['traffic']}", delta_color="normal")
    with col5:
        st.metric(t["kpi_top10_drops"], len(top10_drops), delta=f"-{int(top10_drops['Traffic Loss'].sum())} {t['traffic']}", delta_color="normal")
    with col6:
        st.metric(t["kpi_lhf"], len(low_hanging), delta=f"{lhf_search_vol:,} SV".replace(',', '.'), delta_color="off", help=t["kpi_lhf_help"])
        st.markdown(f"<div style='font-size: 14px; color: gray;'>{t.get('kpi_lhf_link', '')}</div>", unsafe_allow_html=True)
        
    st.write("---")
    
    viz_col1, viz_col2 = st.columns(2)
    with viz_col1:
        st.markdown("#### " + t["kpi_cluster_title"])
        cluster_net = df.groupby('Cluster')['Traffic Change'].sum().reset_index()
        cluster_net = cluster_net[cluster_net['Cluster'] != "undefined"]
        
        if not cluster_net.empty:
            best_cluster = cluster_net.loc[cluster_net['Traffic Change'].idxmax()]
            worst_cluster = cluster_net.loc[cluster_net['Traffic Change'].idxmin()]
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(t["kpi_best_cluster"], best_cluster['Cluster'], f"{int(best_cluster['Traffic Change']):,} {t['traffic']}".replace(',', '.'))
            with c2:
                st.metric(t["kpi_worst_cluster"], worst_cluster['Cluster'], f"{int(worst_cluster['Traffic Change']):,} {t['traffic']}".replace(',', '.'))
                
            top_bottom = pd.concat([cluster_net.nlargest(3, 'Traffic Change'), cluster_net.nsmallest(3, 'Traffic Change')]).drop_duplicates()
            top_bottom = top_bottom.sort_values('Traffic Change')
            fig_net = px.bar(
                top_bottom, x='Traffic Change', y='Cluster', orientation='h',
                color='Traffic Change', color_continuous_scale='RdYlGn',
                height=200
            )
            fig_net.update_layout(margin=dict(l=0, r=0, t=0, b=0), yaxis_title=None, xaxis_title=None)
            st.plotly_chart(fig_net, use_container_width=True)

    with viz_col2:
        st.markdown("#### " + t["kpi_top3_title"])
        if not top3_drops.empty:
            worst_top3 = top3_drops.nlargest(5, 'Traffic Loss').sort_values('Traffic Loss', ascending=True)
            fig_t3 = px.bar(
                worst_top3, x='Traffic Loss', y='Keyword', orientation='h',
                color_discrete_sequence=['#ff4b4b'], height=270
            )
            fig_t3.update_layout(margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None, xaxis_title=None)
            st.plotly_chart(fig_t3, use_container_width=True)
        else:
            st.info(t["rd_t3_empty"])
            
    st.write("---")

    def display_styled_dataframe(df_to_show, sort_col, ascending=False):
        loss_cols = [c for c in ['Traffic Loss', 'Lost Value €'] if c in df_to_show.columns]
        gain_cols = [c for c in ['Traffic Gain'] if c in df_to_show.columns]
        
        styler = df_to_show.sort_values(sort_col, ascending=ascending).style
        format_dict = {}
        
        if loss_cols:
            styler = styler.map(lambda x: 'color: #ff4b4b; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=loss_cols)
            for c in loss_cols:
                if c == 'Lost Value €':
                    format_dict[c] = lambda x: f"▼ -{x:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) and x > 0 else ("0,00 €" if pd.notnull(x) else "")
                else:
                    format_dict[c] = lambda x: f"▼ -{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) and x > 0 else ("0,00" if pd.notnull(x) else "")
                
        if gain_cols:
            styler = styler.map(lambda x: 'color: #09ab3b; font-weight: bold;' if pd.notnull(x) and x > 0 else '', subset=gain_cols)
            for c in gain_cols:
                format_dict[c] = lambda x: f"▲ +{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) and x > 0 else ("0,00" if pd.notnull(x) else "")
                
        for c in ['Search Volume', 'Traffic#1', 'Traffic#2', 'Traffic Change']:
            if c in df_to_show.columns:
                format_dict[c] = lambda x: f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if pd.notnull(x) else ""
                
        for c in ['Position#1', 'Position#2']:
            if c in df_to_show.columns:
                format_dict[c] = lambda x: "-" if pd.notnull(x) and x == 101 else (f"{x:.2f}".replace('.', ',') if pd.notnull(x) else "")
        
        for c in ['Position Change']:
            if c in df_to_show.columns:
                styler = styler.map(lambda x: 'color: #09ab3b;' if pd.notnull(x) and x > 0 else ('color: #ff4b4b;' if pd.notnull(x) and x < 0 else ''), subset=[c])
                format_dict[c] = lambda x: f"▲ +{x:.2f}".replace('.', ',') if pd.notnull(x) and x > 0 else (f"▼ {x:.2f}".replace('.', ',') if pd.notnull(x) and x < 0 else "0,00")
                
        styler = styler.format(format_dict)
        st.dataframe(styler, use_container_width=True)

    st.header("Details" if lang == "DE" else "Details")
    
    tab_d, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t["tab_dir"],
        t["tab_cluster"],
        t["tab_drops"],
        t["tab_lhf"],
        t["tab_winners"],
        t["tab_all"]
    ])
    
    with tab_d:
        st.subheader(t["dir_sub"])
        if not top10_drops.empty:
            dir_vol = top10_drops.groupby('Directory').agg(
                Traffic_Loss=('Traffic Loss', 'sum'),
                Value_Loss=('Lost Value €', 'sum')
            ).reset_index()
            dir_vol = dir_vol[dir_vol['Traffic_Loss'] > 0].sort_values('Traffic_Loss', ascending=False).head(15)
            
            fig = px.bar(dir_vol, x='Directory', y='Traffic_Loss', 
                         title=t["dir_chart_title"],
                         labels={'Directory': t["dir_chart_label_d"], 'Traffic_Loss': t["dir_chart_label_t"]},
                         hover_data=['Value_Loss'],
                         color='Traffic_Loss', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t["dir_empty"])

    with tab1:
        st.subheader(t["cl_sub"])
        st.markdown(t["cl_desc"])
        
        if not losers.empty:
            cluster_vol = losers.groupby('Cluster').agg(
                Traffic_Loss=('Traffic Loss', 'sum'),
                Value_Loss=('Lost Value €', 'sum'),
                Keyword_Count=('Keyword', 'count')
            ).reset_index()
            cluster_vol = cluster_vol[cluster_vol['Traffic_Loss'] > 0].sort_values('Traffic_Loss', ascending=False)
            
            fig_cluster = px.bar(cluster_vol, x='Cluster', y='Traffic_Loss', 
                         title=t["cl_chart_title"],
                         labels={'Cluster': t["cl_chart_label_c"], 'Traffic_Loss': t["cl_chart_label_t"]},
                         hover_data=['Value_Loss', 'Keyword_Count'],
                         color='Traffic_Loss', color_continuous_scale='Blues')
            st.plotly_chart(fig_cluster, use_container_width=True)
            
            st.markdown(t["cl_detail"])
            opts = [c for c in cluster_vol['Cluster'].tolist() if c != "undefined"] + ["undefined"]
            selected_clusters = st.multiselect(t["cl_select"], options=opts)
            if selected_clusters:
                cluster_df = losers[losers['Cluster'].isin(selected_clusters)]
                st.write(f"{t['cl_sum']} **{int(cluster_df['Search Volume'].sum()):,}**".replace(',', '.'))
                display_styled_dataframe(cluster_df[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Traffic Loss')
        else:
            st.info(t["cl_empty"])

    with tab2:
        st.subheader(t["rd_sub"])
        kw_filter = st.text_input(t["rd_filter"]).strip().lower()
        
        f_top3 = top3_drops[top3_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top3_drops
        f_top10 = top10_drops[top10_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else top10_drops
        f_page2 = page2_drops[page2_drops['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else page2_drops
        f_total = total_loss[total_loss['Keyword'].astype(str).str.lower().str.contains(kw_filter, na=False)] if kw_filter else total_loss
        
        st.markdown(t["rd_t3_title"])
        if not f_top3.empty:
            st.write(f"{t['rd_sum_vol']} **{int(f_top3['Search Volume'].sum()):,}** {t['rd_sum_traf']} {int(f_top3['Traffic Loss'].sum()):,})".replace(',', '.'))
            display_styled_dataframe(f_top3[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Traffic Loss')
        else:
            st.info(t["rd_t3_empty"])
            
        st.markdown(t["rd_t10_title"])
        if not f_top10.empty:
            st.write(f"{t['rd_sum_vol']} **{int(f_top10['Search Volume'].sum()):,}** {t['rd_sum_traf']} {int(f_top10['Traffic Loss'].sum()):,})".replace(',', '.'))
            display_styled_dataframe(f_top10[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Traffic Loss')
        else:
            st.info(t["rd_t10_empty"])
            
        st.markdown(t["rd_p2_title"])
        if not f_page2.empty:
            st.write(f"{t['rd_sum_vol']} **{int(f_page2['Search Volume'].sum()):,}** {t['rd_sum_traf']} {int(f_page2['Traffic Loss'].sum()):,})".replace(',', '.'))
            display_styled_dataframe(f_page2[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Traffic Loss')
        else:
            st.info(t["rd_p2_empty"])
            
        st.markdown(t["rd_100_title"])
        if not f_total.empty:
            st.write(f"{t['rd_sum_vol']} **{int(f_total['Search Volume'].sum()):,}** {t['rd_sum_traf']} {int(f_total['Traffic Loss'].sum()):,})".replace(',', '.'))
            display_styled_dataframe(f_total[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory', 'URL']], sort_col='Traffic Loss')
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
            display_styled_dataframe(winners[['Keyword', 'Position Change', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Gain', 'Directory']], sort_col='Traffic Gain')
            
            fig_win = px.scatter(
                winners, x="Search Volume", y="Position#2", 
                size="Traffic Gain", color="Directory",
                hover_name="Keyword", title=t["win_chart_title"],
                labels={'Position#2': t["win_chart_label_pos"]}
            )
            fig_win.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_win, use_container_width=True)
        else:
            st.info(t["win_empty"])

    with tab5:
        st.subheader(t["ad_sub"])
        
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        all_clusters = sorted([c for c in df['Cluster'].dropna().unique() if c != 'undefined']) + ['undefined']
        with f_col1:
            sel_clusters = st.multiselect(t["ad_filter_cluster"], options=all_clusters)
            
        all_changes = sorted(df['Change'].unique().tolist())
        with f_col2:
            sel_changes = st.multiselect(t["ad_filter_change"], options=all_changes)
            
        all_dirs = sorted(df['Directory'].unique().tolist())
        with f_col3:
            sel_dirs = st.multiselect(t["ad_filter_dir"], options=all_dirs)
            
        with f_col4:
            search_kw = st.text_input(t["ad_filter_kw"]).strip().lower()
            
        filtered_df = df.copy()
        if sel_clusters:
            filtered_df = filtered_df[filtered_df['Cluster'].isin(sel_clusters)]
        if sel_changes:
            filtered_df = filtered_df[filtered_df['Change'].isin(sel_changes)]
        if sel_dirs:
            filtered_df = filtered_df[filtered_df['Directory'].isin(sel_dirs)]
        if search_kw:
            filtered_df = filtered_df[filtered_df['Keyword'].astype(str).str.lower().str.contains(search_kw, na=False)]
            
        all_cols = ['Cluster', 'Directory', 'Keyword', 'Change', 'Position Change', 'Traffic Change', 'Lost Value €', 'Position#1', 'Position#2', 'Search Volume', 'Traffic#1', 'Traffic#2', 'URL']
        all_cols = [c for c in all_cols if c in filtered_df.columns]
        
        display_styled_dataframe(filtered_df[all_cols], sort_col='Traffic Change', ascending=True)

else:
    st.info(t.get("info_upload", "Bitte lade eine Sistrix CSV-Datei hoch und klicke auf 'Analysieren'."))

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.9em;'>"
    "MIT License &copy; 2026 Benjamin &quot;SEOux Indianer&quot; Wingerter | Made with ❤️ in Munich & Bangkok: <a href='https://seouxindianer.de' target='_blank' style='color: gray; text-decoration: underline;'>seouxindianer.de</a>"
    "</div>", 
    unsafe_allow_html=True
)
