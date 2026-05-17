import streamlit as st
import requests

# ─── Configuratie ─────────────────────────────────────────────────────────────
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxIx-h_CnV6gVSwlV-ns3NSNAJw5ud_jiDHB4gkbe2HNzTB0Or3ln22Y62n9uRlfcr9/exec"

# ─── Alle 72 wedstrijden in volgorde van de Google Sheet ──────────────────────
# Speelronde 1 (wedstrijden 1–24)
RONDE_1 = [
    "Mexico - Zuid-Afrika",           # 1
    "Zuid-Korea - Tsjechië",          # 2
    "Canada - Bosnië & Herzegovina",  # 3
    "Verenigde Staten - Paraguay",    # 4
    "Australië - Turkije",            # 5
    "Qatar - Zwitserland",            # 6
    "Brazillië - Marokko",            # 7
    "Haïti - Schotland",              # 8
    "Duitsland - Curaçao",            # 9
    "Nederland - Japan",              # 10
    "Ivoorkust - Ecuador",            # 11
    "Zweden - Tunesië",               # 12
    "Spanje - Kaapverdië",            # 13
    "België - Egypte",                # 14
    "Saoedi-Arabië - Uruguay",        # 15
    "Iran - Nieuw-Zeeland",           # 16
    "Oostenrijk - Jordanië",          # 17
    "Frankrijk - Senegal",            # 18
    "Irak - Noorwegen",               # 19
    "Argentinië - Algerije",          # 20
    "Portugal - Congo",               # 21
    "Engeland - Kroatië",             # 22
    "Ghana - Panama",                 # 23
    "Oezbekistan - Colombia",         # 24
]

# Speelronde 2 (wedstrijden 25–48)
RONDE_2 = [
    "Tsjechië - Zuid-Afrika",              # 25
    "Zwitserland - Bosnië & Herzegovina",  # 26
    "Canada - Qatar",                      # 27
    "Mexico - Zuid-Korea",                 # 28
    "Turkije - Paraguay",                  # 29
    "Verenigde Staten - Australië",        # 30
    "Schotland - Marokko",                 # 31
    "Brazillië - Haïti",                   # 32
    "Tunesië - Japan",                     # 33
    "Nederland - Zweden",                  # 34
    "Duitsland - Ivoorkust",               # 35
    "Ecuador - Curaçao",                   # 36
    "Spanje - Saoedi-Arabië",              # 37
    "België - Iran",                       # 38
    "Uruguay - Kaapverdië",                # 39
    "Nieuw-Zeeland - Egypte",              # 40
    "Argentinië - Oostenrijk",             # 41
    "Frankrijk - Irak",                    # 42
    "Noorwegen - Senegal",                 # 43
    "Jordanië - Algerije",                 # 44
    "Portugal - Oezbekistan",              # 45
    "Engeland - Ghana",                    # 46
    "Panama - Kroatië",                    # 47
    "Colombia - Congo",                    # 48
]

# Speelronde 3 (wedstrijden 49–72)
RONDE_3 = [
    "Bosnië & Herzegovina - Qatar",   # 49
    "Zwitserland - Canada",           # 50
    "Marokko - Haïti",                # 51
    "Schotland - Brazillië",          # 52
    "Tsjechië - Mexico",              # 53
    "Zuid-Afrika - Zuid-Korea",       # 54
    "Curaçao - Ivoorkust",            # 55
    "Ecuador - Duitsland",            # 56
    "Japan - Zweden",                 # 57
    "Tunesië - Nederland",            # 58
    "Paraguay - Australië",           # 59
    "Turkije - Verenigde Staten",     # 60
    "Noorwegen - Frankrijk",          # 61
    "Senegal - Irak",                 # 62
    "Kaapverdië - Saoedi-Arabië",     # 63
    "Uruguay - Spanje",               # 64
    "Egypte - Iran",                  # 65
    "Nieuw-Zeeland - België",         # 66
    "Kroatië - Ghana",                # 67
    "Panama - Engeland",              # 68
    "Colombia - Portugal",            # 69
    "Congo - Oezbekistan",            # 70
    "Algerije - Oostenrijk",          # 71
    "Jordanië - Argentinië",          # 72
]

ALLE_WEDSTRIJDEN = RONDE_1 + RONDE_2 + RONDE_3

# Splits elke ronde in tabs van max 6 wedstrijden
def maak_tabs(wedstrijden, ronde_naam, start_nr):
    tabs = {}
    for i in range(0, len(wedstrijden), 6):
        groep = wedstrijden[i:i + 6]
        eind_nr = start_nr + i + len(groep) - 1
        label = f"{ronde_naam} · {start_nr + i}–{eind_nr}"
        tabs[label] = groep
    return tabs

TABS_R1 = maak_tabs(RONDE_1, "R1", 1)
TABS_R2 = maak_tabs(RONDE_2, "R2", 25)
TABS_R3 = maak_tabs(RONDE_3, "R3", 49)
ALLE_TABS = {**TABS_R1, **TABS_R2, **TABS_R3}

# Deelnemende landen (voor kampioen-dropdown)
LANDEN = sorted([
    "Algerije", "Argentinië", "Australië", "België", "Bosnië & Herzegovina",
    "Brazillië", "Canada", "Colombia", "Congo", "Curaçao", "Duitsland",
    "Ecuador", "Egypte", "Engeland", "Frankrijk", "Ghana", "Haïti",
    "Iran", "Irak", "Ivoorkust", "Japan", "Jordanië", "Kaapverdië",
    "Kroatië", "Marokko", "Mexico", "Nederland", "Nieuw-Zeeland", "Noorwegen",
    "Oezbekistan", "Oostenrijk", "Panama", "Paraguay", "Portugal", "Qatar",
    "Saoedi-Arabië", "Schotland", "Senegal", "Spanje", "Tsjechië", "Tunesië",
    "Turkije", "Uruguay", "Verenigde Staten", "Zuid-Afrika", "Zuid-Korea",
    "Zweden", "Zwitserland",
])

TIJDSBLOKKEN = [
    "Geen doelpunt",
    "1–15 min",
    "16–30 min",
    "31–45+ min",
    "46–60 min",
    "61–75 min",
    "76–90+ min",
]

# ─── Pagina-instellingen ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="WK 2026 Poule",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("🏆 WK 2026 Poule — Voorspellingen")
st.caption(
    "Vul al je voorspellingen in voor alle 72 groepswedstrijden en klik onderaan op **Verzenden**. "
    "Wedstrijden zijn verdeeld over 3 speelrondes (R1–R3), elke tab bevat 6 wedstrijden."
)

# ─── Persoonsgegevens ─────────────────────────────────────────────────────────
with st.container(border=True):
    st.subheader("👤 Jouw gegevens")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        nickname = st.text_input("Nickname *", placeholder="Bijv. VoetbalKoning")
    with col2:
        email = st.text_input("E-mailadres *", placeholder="jouw@email.nl")
    with col3:
        kampioen = st.selectbox(
            "Voorspelling Kampioen *",
            options=["— kies een land —"] + LANDEN,
        )

st.divider()
st.subheader("⚽ Wedstrijdvoorspellingen")
st.caption("Klik op een wedstrijd om hem uit te klappen. Klik nogmaals om te sluiten.")

# ─── Wedstrijden in tabs ──────────────────────────────────────────────────────
tab_labels = list(ALLE_TABS.keys())
tabs = st.tabs(tab_labels)

for tab, label in zip(tabs, tab_labels):
    with tab:
        for wedstrijd in ALLE_TABS[label]:
            with st.expander(f"⚽ **{wedstrijd}**", expanded=False):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
                with c1:
                    st.text_input(
                        "Uitslag",
                        placeholder="bijv. 2-1",
                        key=f"{wedstrijd}__uitslag",
                    )
                with c2:
                    st.radio(
                        "Rode kaart?",
                        options=["Nee", "Ja"],
                        key=f"{wedstrijd}__rood",
                        horizontal=True,
                    )
                with c3:
                    st.radio(
                        "Corners >8.5?",
                        options=["Meer", "Minder"],
                        key=f"{wedstrijd}__corners",
                        horizontal=True,
                    )
                with c4:
                    st.selectbox(
                        "Tijdsblok 1e doelpunt",
                        options=TIJDSBLOKKEN,
                        key=f"{wedstrijd}__tijd",
                    )

st.divider()

# ─── Verzendknop ─────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 3])
with col_btn:
    verzenden = st.button("📤 Verzenden", type="primary", use_container_width=True)
with col_info:
    st.caption(
        "Door te verzenden ga je akkoord dat jouw voorspellingen worden opgeslagen "
        "in de gedeelde poule-sheet."
    )

if verzenden:
    # ── Validatie ────────────────────────────────────────────────────────────
    fouten = []
    if not nickname.strip():
        fouten.append("⚠️ Vul een nickname in.")
    if not email.strip() or "@" not in email:
        fouten.append("⚠️ Vul een geldig e-mailadres in.")
    if kampioen == "— kies een land —":
        fouten.append("⚠️ Kies een voorspelling voor de kampioen.")

    if fouten:
        for f in fouten:
            st.warning(f)
        st.stop()

    # ── Payload opbouwen (keys exact gelijk aan kolomnamen sheet) ────────────
    payload: dict = {
        "Nickname":               nickname.strip(),
        "E-mailadres":            email.strip(),
        "Voorspelling Kampioen":  kampioen,
    }

    for wedstrijd in ALLE_WEDSTRIJDEN:
        payload[f"{wedstrijd} (Uitslag)"]          = st.session_state.get(f"{wedstrijd}__uitslag", "")
        payload[f"{wedstrijd} (Rode Kaart)"]        = st.session_state.get(f"{wedstrijd}__rood", "Nee")
        payload[f"{wedstrijd} (Corners >8.5)"]      = st.session_state.get(f"{wedstrijd}__corners", "Minder")
        payload[f"{wedstrijd} (Tijd 1e Doelpunt)"]  = st.session_state.get(f"{wedstrijd}__tijd", "Geen doelpunt")

    # ── Versturen naar Google Apps Script ────────────────────────────────────
    try:
        with st.spinner("Voorspellingen worden opgeslagen in de poule-sheet…"):
            response = requests.post(
                APPS_SCRIPT_URL,
                json=payload,
                timeout=20,
                allow_redirects=True,
            )

        if response.status_code == 200:
            st.success(
                f"✅ De voorspelling van **{nickname}** is succesvol opgeslagen! "
                "Veel succes met de poule 🎉"
            )
            st.balloons()
        else:
            st.error(
                f"❌ Fout bij opslaan (HTTP {response.status_code}).\n\n"
                f"Serverrespons: `{response.text[:300]}`"
            )

    except requests.exceptions.Timeout:
        st.error(
            "⏱️ Het verzoek duurde te lang (>20 s). "
            "Controleer je internetverbinding en probeer opnieuw."
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"🚨 Verbindingsfout: {exc}")