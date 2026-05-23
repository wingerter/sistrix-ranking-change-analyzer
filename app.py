import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from urllib.parse import urlparse
import io

st.set_page_config(page_title="Sistrix SEO Analyzer", layout="wide")

st.title("Sistrix SEO Drop Analyzer Pro")
st.markdown("Lade deinen Sistrix-Vergleichsexport hoch und analysiere Keyword-Verluste, Traffic-Impact und Quick Wins.")

# Sidebar - Settings
st.sidebar.header("1. Daten & Einstellungen")

uploaded_file = st.sidebar.file_uploader("Sistrix CSV Upload", type=["csv"])

st.sidebar.subheader("Datumsangaben für die Diagramme")
date_old = st.sidebar.date_input("Datum für Position#1 (Alt)", value=pd.to_datetime('today') - pd.DateOffset(months=1))
date_new = st.sidebar.date_input("Datum für Position#2 (Neu)", value=pd.to_datetime('today'))

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

if uploaded_file is not None:
    if st.sidebar.button("Analysieren", type="primary"):
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
        
        # Try multiple combinations of encoding and separators
        for enc in ['utf-8', 'utf-16', 'latin1', 'utf-8-sig']:
            for sep in ['\t', ';', ',']:
                for skip in [0, 1, 2, 3, 4, 5]:
                    try:
                        temp_df = pd.read_csv(io.BytesIO(content), encoding=enc, sep=sep, skiprows=skip, on_bad_lines='skip')
                        # Clean column names (strip whitespace and quotes just in case)
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
            raise Exception("Konnte das Sistrix-Format nicht erkennen. Bitte prüfe die Datei (Spaltennamen 'Keyword' und 'Position#1' müssen exakt so existieren).")
             
    except Exception as e:
        st.error(f"Fehler beim Lesen der CSV: {e}")
        st.stop()
        
    st.success("Datei erfolgreich geladen und analysiert!")
    
    # Required columns check
    req_cols = ["Keyword", "Position#1", "Position#2", "Search Volume", "URL"]
    missing_cols = [col for col in req_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"Die folgenden benötigten Spalten fehlen in der CSV: {missing_cols}")
        st.write("Vorhandene Spalten:", df.columns.tolist())
        st.stop()
        
    # --- Data Cleaning ---
    if df['Search Volume'].dtype == 'object':
        df['Search Volume'] = df['Search Volume'].astype(str).str.replace('.', '', regex=False).str.replace(',', '', regex=False)
    df['Search Volume'] = pd.to_numeric(df['Search Volume'], errors='coerce').fillna(0)
    
    # Clean CPC
    if 'CPC' in df.columns:
        if df['CPC'].dtype == 'object':
            df['CPC'] = df['CPC'].astype(str).str.replace(',', '.', regex=False)
        df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce').fillna(0.0)
    else:
        df['CPC'] = 0.0

    # Clean Competition
    if 'Competition' in df.columns:
        if df['Competition'].dtype == 'object':
            df['Competition'] = df['Competition'].astype(str).str.replace(',', '.', regex=False)
        df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce').fillna(0.0)
    else:
        df['Competition'] = 0.0
    
    # Clean Positions
    for col in ['Position#1', 'Position#2']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(101)
        df[col] = df[col].replace(0, 101)
        
    # Extract Directory
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
    
    # Calculate Monetary Value of lost traffic
    df['Lost Value €'] = df['Traffic Loss'].clip(lower=0) * df['CPC']
    
    st.write("---")
    
    # Segments
    # 1. Top 10 Drops
    top10_drops = df[(df['Position#1'] <= 10) & (df['Position#2'] > 10)]
    
    # 2. Low Hanging Fruits (Dropped from Top 10 to Pos 11-15)
    low_hanging = df[(df['Position#1'] <= 10) & (df['Position#2'] >= 11) & (df['Position#2'] <= 15)]
    
    # 3. Total Loss
    total_loss = df[(df['Position#1'] <= 100) & (df['Position#2'] > 100)]
    
    # 4. Winners
    winners = df[(df['Position#1'] > 10) & (df['Position#2'] <= 10)].copy()
    
    # 5. Page 2 Drops
    page2_drops = df[(df['Position#1'] > 10) & (df['Position#1'] <= 20) & (df['Position#2'] > 20)]
    
    # --- KPIs ---
    st.header("Überblick: Business Impact")
    
    total_traffic_loss = int(top10_drops['Traffic Loss'].sum())
    total_value_loss = top10_drops['Lost Value €'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Top 10 Abstürze", len(top10_drops))
    with col2:
        st.metric("Geschätzter Traffic-Verlust", f"{total_traffic_loss:,}".replace(',', '.'))
    with col3:
        st.metric("Monetärer Verlust (AdWords Äquivalent)", f"{total_value_loss:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.'))
    with col4:
        st.metric("Gewinner (Neu in Top 10)", len(winners), delta=f"+ {int(winners['Traffic Gain'].sum())} Traffic")
        
    st.write("---")
    
    # --- Visualizations & Tabs ---
    st.header("Visualisierungen")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Verzeichnis-Analyse", 
        "Low Hanging Fruits", 
        "Gewinner",
        "Keyword-Veränderungen"
    ])
    
    with tab1:
        st.subheader("Verlorener Traffic & Wert nach Verzeichnis")
        if not top10_drops.empty:
            dir_vol = top10_drops.groupby('Directory').agg(
                Traffic_Loss=('Traffic Loss', 'sum'),
                Value_Loss=('Lost Value €', 'sum')
            ).reset_index()
            dir_vol = dir_vol[dir_vol['Traffic_Loss'] > 0].sort_values('Traffic_Loss', ascending=False).head(15)
            
            fig = px.bar(dir_vol, x='Directory', y='Traffic_Loss', 
                         title='Welche Verzeichnisse kosten uns am meisten Traffic?',
                         labels={'Directory': 'Verzeichnis', 'Traffic_Loss': 'Verlorene Klicks (Schätzung)'},
                         hover_data=['Value_Loss'],
                         color='Traffic_Loss', color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Keine Daten vorhanden.")
            
    with tab2:
        st.subheader("Low Hanging Fruits (Position 11 - 15)")
        st.write("Diese Keywords sind knapp auf Seite 2 abgerutscht. Mit kleinen Optimierungen holst du sie schnell zurück!")
        if not low_hanging.empty:
            st.dataframe(low_hanging[['Keyword', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Lost Value €', 'Directory']].sort_values('Traffic Loss', ascending=False))
        else:
            st.info("Keine Keywords im Bereich 11-15 gefunden.")
            
    with tab3:
        st.subheader("Gewinner (Neu in den Top 10)")
        if not winners.empty:
            st.dataframe(winners[['Keyword', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Gain', 'Directory']].sort_values('Traffic Gain', ascending=False))
            
            fig_win = px.scatter(
                winners, x="Search Volume", y="Position#2", 
                size="Traffic Gain", color="Directory",
                hover_name="Keyword", title="Gewinner-Keywords nach Suchvolumen",
                labels={'Position#2': 'Neue Position'}
            )
            fig_win.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_win, use_container_width=True)
        else:
            st.info("Keine neuen Rankings in den Top 10.")

    with tab4:
        st.subheader("Alle Abstürze in der Übersicht")
        
        st.markdown("#### 1. Top 10 Drops (Aus Top 10 gerutscht)")
        
        # Directory Filter
        available_dirs = sorted(top10_drops['Directory'].unique().tolist())
        selected_dirs = st.multiselect("Nach Verzeichnis filtern (leer lassen = alle anzeigen):", options=available_dirs, default=[], key="top10_dir_filter")
        
        filtered_top10 = top10_drops
        if selected_dirs:
            filtered_top10 = top10_drops[top10_drops['Directory'].isin(selected_dirs)]
            
        st.write(f"Angezeigtes Suchvolumen: **{int(filtered_top10['Search Volume'].sum()):,}** (Geschätzter Traffic-Verlust: {int(filtered_top10['Traffic Loss'].sum()):,})".replace(',', '.'))
        st.dataframe(filtered_top10[['Keyword', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Directory', 'URL']].sort_values('Search Volume', ascending=False))
        
        st.markdown("#### 2. Seite 2 Drops (Von Seite 2 weiter nach hinten)")
        st.write(f"Gesamtes betroffenes Suchvolumen: **{int(page2_drops['Search Volume'].sum()):,}** (Geschätzter Traffic-Verlust: {int(page2_drops['Traffic Loss'].sum()):,})".replace(',', '.'))
        st.dataframe(page2_drops[['Keyword', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Directory', 'URL']].sort_values('Search Volume', ascending=False))
        
        st.markdown("#### 3. Komplette Verluste (Aus Top 100 gefallen)")
        st.write(f"Gesamtes betroffenes Suchvolumen: **{int(total_loss['Search Volume'].sum()):,}** (Geschätzter Traffic-Verlust: {int(total_loss['Traffic Loss'].sum()):,})".replace(',', '.'))
        st.dataframe(total_loss[['Keyword', 'Position#1', 'Position#2', 'Search Volume', 'Traffic Loss', 'Directory', 'URL']].sort_values('Search Volume', ascending=False))

else:
    st.info("Bitte lade eine Sistrix CSV-Datei hoch und klicke auf 'Analysieren'.")

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.9em;'>"
    "MIT License &copy; 2026 Benjamin &quot;SEOux Indianer&quot; Wingerter | Made with ❤️ in Munich & Bangkok: <a href='https://seouxindianer.de' target='_blank' style='color: gray; text-decoration: underline;'>seouxindianer.de</a>"
    "</div>", 
    unsafe_allow_html=True
)
