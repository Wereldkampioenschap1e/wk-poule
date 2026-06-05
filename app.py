# ============================================================
#  WK POULE 2026 – Kompas Publishing
#  app.py  |  Streamlit Cloud deployment
#
#  requirements.txt (minimaal):
#      streamlit>=1.30
#      requests
# ============================================================

import json
import re
import streamlit as st
import requests

# ────────────────────────────────────────────────────────────
# 0.  CONSTANTEN
# ────────────────────────────────────────────────────────────

APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbznnUcqVJOZMc7g8AbT4zCZXQNBTHrzQqL9N7SKU4l07O-i4ieRgWznsbQS7-OMGZXq"
    "/exec"
)

# 24 wedstrijden Speelronde 1  (volgorde = tabindeling)
WEDSTRIJDEN: list[str] = [
    "Mexico - Zuid-Afrika",
    "Zuid-Korea - Tsjechië",
    "Canada - Bosnië & Herzegovina",
    "Verenigde Staten - Paraguay",
    "Australië - Turkije",
    "Qatar - Zwitserland",
    "Brazillië - Marokko",
    "Haïti - Schotland",
    "Duitsland - Curaçao",
    "Nederland - Japan",
    "Ivoorkust - Ecuador",
    "Zweden - Tunesië",
    "Spanje - Kaapverdië",
    "België - Egypte",
    "Saoedi-Arabië - Uruguay",
    "Iran - Nieuw-Zeeland",
    "Oostenrijk - Jordanië",
    "Frankrijk - Senegal",
    "Irak - Noorwegen",
    "Argentinië - Algerije",
    "Portugal - Congo",
    "Engeland - Kroatië",
    "Ghana - Panama",
    "Oezbekistan - Colombia",
]

_PH          = "-- Maak een keuze --"       # selectbox-placeholder
_PH_LAND     = "-- Selecteer een land --"   # kampioen-placeholder

GELE_KAARTEN_OPTIES: list[str] = [
    _PH,
    "0-2 gele kaarten",
    "3-4 gele kaarten",
    "5+ gele kaarten",
]

TIJD_DOELPUNT_OPTIES: list[str] = [
    _PH,
    "Geen doelpunt",
    "1\u201315 min",
    "16\u201330 min",
    "31\u201345+ min",
    "46\u201360 min",
    "61\u201375 min",
    "76\u201390+ min",
]

# 48 deelnemende landen (exact gelijk aan de teams uit de 24 wedstrijden)
LANDEN: list[str] = sorted([
    "Algerije", "Argentinië", "Australië", "België",
    "Bosnië & Herzegovina", "Brazillië", "Canada", "Colombia",
    "Congo", "Curaçao", "Duitsland", "Ecuador", "Egypte",
    "Engeland", "Frankrijk", "Ghana", "Haïti", "Irak", "Iran",
    "Ivoorkust", "Japan", "Jordanië", "Kaapverdië", "Kroatië",
    "Marokko", "Mexico", "Nederland", "Nieuw-Zeeland", "Noorwegen",
    "Oezbekistan", "Oostenrijk", "Panama", "Paraguay", "Portugal",
    "Qatar", "Saoedi-Arabië", "Schotland", "Senegal", "Spanje",
    "Tsjechië", "Tunesië", "Turkije", "Uruguay", "Verenigde Staten",
    "Zuid-Afrika", "Zuid-Korea", "Zweden", "Zwitserland",
])

TOPSPELERS: list[str] = sorted([
    # 🇫🇷 Frankrijk
    "Kylian Mbappé", "Antoine Griezmann", "Ousmane Dembélé", "Marcus Thuram",
    # 🇳🇴 Noorwegen
    "Erling Haaland",
    # 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Engeland
    "Harry Kane", "Jude Bellingham", "Bukayo Saka",
    # 🇧🇷 Brazilië
    "Vinicius Junior", "Raphinha", "Neymar",
    # 🇦🇷 Argentinië
    "Lionel Messi", "Lautaro Martínez",
    # 🇵🇹 Portugal
    "Cristiano Ronaldo", "Rafael Leão", "João Félix",
    # 🇪🇸 Spanje
    "Lamine Yamal", "Pedri", "Nico Williams", "Rodri",
    # 🇧🇪 België
    "Romelu Lukaku", "Kevin De Bruyne",
    # 🇳🇱 Nederland
    "Memphis Depay", "Cody Gakpo", "Virgil van Dijk",
    # 🇩🇪 Duitsland
    "Florian Wirtz", "Jamal Musiala",
    # 🇲🇦 Marokko
    "Achraf Hakimi",
    # 🇪🇬 Egypte
    "Mohamed Salah",
    # 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Schotland
    "Scott McTominay",
    # 🇸🇪 Zweden
    "Viktor Gyökeres", "Alexander Isak",
    # 🇺🇾 Uruguay
    "Darwin Núñez",
    # 🇨🇴 Colombia
    "Luís Díaz",
    # 🇰🇷 Zuid-Korea
    "Son Heung-min",
    # 🇮🇷 Iran
    "Mehdi Taremi",
    # 🇺🇸 Verenigde Staten
    "Christian Pulisic",
    # 🇲🇽 Mexico
    "Santiago Giménez",
    # 🇨🇦 Canada
    "Jonathan David",
])

# ────────────────────────────────────────────────────────────
# 1.  PAGINA-CONFIGURATIE
# ────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="⚽ WK Poule 2026 – Kompas Publishing",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Globale CSS ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Gradiënt-titel ── */
    .wk-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #e85d04 0%, #ffd60a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.15;
    }
    .wk-sub {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 1.4rem;
    }
    /* ── Primaire submit-knop groter ── */
    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        font-size: 1.15rem;
        font-weight: 700;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        letter-spacing: 0.03em;
    }
    /* ── Expander-header iets vetter ── */
    details > summary p {
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────
# 2.  SUCCES-STATUS (voorkomt herhaald insturen na refresh)
# ────────────────────────────────────────────────────────────

if "ingestuurd" not in st.session_state:
    st.session_state["ingestuurd"] = False

# Toon alleen het succes-scherm als al eerder succesvol ingestuurd
if st.session_state["ingestuurd"]:
    st.markdown('<p class="wk-title">⚽ WK Poule 2026</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="wk-sub">Kompas Publishing &nbsp;·&nbsp; Speelronde 1</p>',
        unsafe_allow_html=True,
    )
    st.success(
        "🎉 **Jouw voorspelling is succesvol opgeslagen!**  \n"
        "Veel succes in de WK Poule 2026 – wie weet win jij de grote prijs! 🏆"
    )
    st.balloons()
    st.stop()

# ────────────────────────────────────────────────────────────
# 3.  HEADER
# ────────────────────────────────────────────────────────────

st.markdown('<p class="wk-title">⚽ WK Poule 2026</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="wk-sub">Kompas Publishing &nbsp;·&nbsp; Speelronde 1 &nbsp;·&nbsp; 24 Wedstrijden</p>',
    unsafe_allow_html=True,
)
st.info(
    "📋 Vul jouw voorspellingen in voor alle **24 wedstrijden** van Speelronde 1.  \n"
    "Alle velden zijn verplicht. Je kunt slechts **één keer** insturen per e-mailadres."
)

# ────────────────────────────────────────────────────────────
# 4.  FORMULIER
# ────────────────────────────────────────────────────────────

with st.form("wk_poule_speelronde_1", border=False):

    # ── 4a.  PERSOONSGEGEVENS ────────────────────────────────
    st.subheader("👤 Jouw gegevens")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "Nickname *",
                placeholder="bijv. VoetbalKoning88",
                key="nickname",
            )
        with col2:
            st.text_input(
                "E-mailadres *",
                placeholder="jouw@kompas.nl",
                key="email",
            )
        st.text_input(
            "Genereer je retro look op https://ek88look.nl/ "
            "en plak hier de link naar je foto (Optioneel):",
            placeholder="https://ek88look.nl/jouw-unieke-foto",
            key="ek88_url",
        )

    st.divider()

    # ── 4b.  WEDSTRIJDVOORSPELLINGEN (4 tabs × 6) ────────────
    st.subheader("⚽ Wedstrijdvoorspellingen – Speelronde 1")
    st.caption(
        "Vul per wedstrijd de **uitslag**, **gele kaarten** en "
        "**tijd van het eerste doelpunt** in. Klik op een wedstrijd om deze te openen."
    )

    tab_labels = [
        "🟠 Wedstrijden 1–6",
        "🟡 Wedstrijden 7–12",
        "🟢 Wedstrijden 13–18",
        "🔵 Wedstrijden 19–24",
    ]
    tabs = st.tabs(tab_labels)

    for tab_idx, tab in enumerate(tabs):
        with tab:
            for local_idx in range(6):
                global_idx = tab_idx * 6 + local_idx
                wedstrijd  = WEDSTRIJDEN[global_idx]
                global_nr  = global_idx + 1
                wk         = f"w{global_idx}"   # korte, unieke key-prefix

                with st.expander(f"#{global_nr}  ·  {wedstrijd}", expanded=False):

                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.text_input(
                            "Uitslag *",
                            placeholder="bijv. 2-1",
                            key=f"{wk}_uitslag",
                        )
                    with c2:
                        st.selectbox(
                            "Gele Kaarten *",
                            options=GELE_KAARTEN_OPTIES,
                            key=f"{wk}_gele",
                        )

                    st.selectbox(
                        "Tijd 1e Doelpunt *",
                        options=TIJD_DOELPUNT_OPTIES,
                        key=f"{wk}_tijd",
                    )

                    # 🍊  ORANJE SPECIAL – alleen bij Nederland - Japan
                    if wedstrijd == "Nederland - Japan":
                        st.markdown("---")
                        st.markdown("🍊 **Oranje Special – Dagprijs!**")
                        st.number_input(
                            "In welke minuut valt het allereerste schot op doel van Nederland?",
                            min_value=1,
                            max_value=90,
                            value=15,
                            step=1,
                            key=f"{wk}_schot",
                        )

    st.divider()

    # ── 4c.  BONUSVRAGEN ─────────────────────────────────────
    st.subheader("🏆 Bonusvragen")

    with st.container(border=True):
        st.markdown("**🥇 Wie wordt wereldkampioen?**")
        st.selectbox(
            "Voorspelling Kampioen *",
            options=[_PH_LAND] + LANDEN,
            key="kampioen",
        )

    st.markdown("")

    with st.container(border=True):
        st.markdown("**⚡ Topscorers van Speelronde 1**")
        st.caption(
            "Selecteer precies **4 spelers** waarvan jij verwacht dat zij scoren "
            "in Speelronde 1."
        )
        st.multiselect(
            "Kies 4 topscorers *",
            options=TOPSPELERS,
            max_selections=4,
            key="topscorers",
        )

    st.divider()

    # ── 4d.  SUBMIT-KNOP ─────────────────────────────────────
    submitted = st.form_submit_button(
        "📤 Voorspelling Verzenden",
        type="primary",
        use_container_width=True,
    )

# ────────────────────────────────────────────────────────────
# 5.  POST-SUBMIT: VALIDATIE + DUPLEX CHECK + VERZENDEN
# ────────────────────────────────────────────────────────────

if submitted:

    # ── Waarden uit session_state ophalen ────────────────────
    _nickname   = st.session_state.get("nickname",   "").strip()
    _email      = st.session_state.get("email",      "").strip()
    _ek88       = st.session_state.get("ek88_url",   "").strip()
    _kampioen   = st.session_state.get("kampioen",   _PH_LAND)
    _topscorers = st.session_state.get("topscorers", [])

    errors: list[str] = []

    # ── Validatie 1: Persoonsgegevens ────────────────────────
    if not _nickname:
        errors.append("Nickname mag niet leeg zijn.")
    if not _email:
        errors.append("E-mailadres mag niet leeg zijn.")
    elif "@" not in _email:
        errors.append("Voer een geldig e-mailadres in (inclusief '@').")

    # ── Validatie 2: Kampioen ────────────────────────────────
    if _kampioen == _PH_LAND:
        errors.append("Selecteer een kampioen.")

    # ── Validatie 3: Topscorers ──────────────────────────────
    if len(_topscorers) != 4:
        errors.append(
            f"Selecteer exact 4 topscorers "
            f"(je hebt er nu {len(_topscorers)} gekozen)."
        )

    # ── Validatie 4 & 5: wedstrijden volledig + uitslag-formaat ─
    # Geldig uitslag-formaat: geheel getal 0–10, streepje, geheel getal 0–10
    # Goed: "2-1"  "0-0"  "10-0"   Fout: "1"  "-3"  "abc"  "11-0"
    _UITSLAG_RE = re.compile(r'^(10|[0-9])-(10|[0-9])$')

    incomplete: list[str]        = []
    ongeldig_uitslag: list[str]  = []

    for idx, wedstrijd in enumerate(WEDSTRIJDEN):
        wk      = f"w{idx}"
        uitslag = st.session_state.get(f"{wk}_uitslag", "").strip()
        gele    = st.session_state.get(f"{wk}_gele",    _PH)
        tijd    = st.session_state.get(f"{wk}_tijd",    _PH)

        if not uitslag or gele == _PH or tijd == _PH:
            tab_nr = idx // 6 + 1
            incomplete.append(f"Tab {tab_nr} – {wedstrijd}")
        elif not _UITSLAG_RE.match(uitslag):
            # Veld is ingevuld maar formaat klopt niet
            tab_nr = idx // 6 + 1
            ongeldig_uitslag.append(f"Tab {tab_nr} – {wedstrijd}: \"{uitslag}\"")

    if incomplete:
        voorbeeld = ", ".join(incomplete[:3])
        extra     = f" en nog {len(incomplete) - 3} meer" if len(incomplete) > 3 else ""
        errors.append(
            f"{len(incomplete)} wedstrijd(en) nog niet volledig ingevuld: "
            f"{voorbeeld}{extra}."
        )

    if ongeldig_uitslag:
        voorbeeld_u = ", ".join(ongeldig_uitslag[:3])
        extra_u     = f" en nog {len(ongeldig_uitslag) - 3} meer" if len(ongeldig_uitslag) > 3 else ""
        errors.append(
            f"Ongeldige uitslag bij {len(ongeldig_uitslag)} wedstrijd(en) – gebruik het formaat "
            f"'X-Y' (bijv. '2-1'), beide getallen 0–10. "
            f"Controleer: {voorbeeld_u}{extra_u}."
        )

    # ── Fouten tonen en stoppen ──────────────────────────────
    if errors:
        st.error(
            "⚠️ Je bent vergeten een aantal velden in te vullen. "
            "Loop de tabbladen en wedstrijden goed langs!"
        )
        with st.expander("🔍 Bekijk alle ontbrekende velden"):
            for err in errors:
                st.markdown(f"- {err}")
        st.stop()

    # ── Duplex e-mailcheck via GET ───────────────────────────
    with st.spinner("🔍 Controleren of dit e-mailadres al is gebruikt..."):
        try:
            check = requests.get(APPS_SCRIPT_URL, timeout=15)
            if check.status_code == 200:
                body = check.json()
                # Ondersteun zowel lijst- als dict-response van Apps Script
                rows: list = body if isinstance(body, list) else body.get("data", [])
                bekende_emails: set[str] = {
                    str(row.get("E-mailadres", "")).strip().lower()
                    for row in rows
                    if isinstance(row, dict) and row.get("E-mailadres")
                }
                if _email.lower() in bekende_emails:
                    st.error(
                        "🚨 Dit e-mailadres heeft al meegedaan! "
                        "Je mag maar 1x insturen."
                    )
                    st.stop()
        except Exception as exc:
            # Duplex-check mislukt → doorgaan (zachte degradatie)
            st.warning(
                f"⚠️ Duplex-check tijdelijk niet beschikbaar ({exc}). "
                "Verzenden gaat door."
            )

    # ── Payload opbouwen ─────────────────────────────────────
    payload: dict = {
        "Nickname":              _nickname,
        "E-mailadres":           _email,
        "EK88 Foto URL":         _ek88,
        "Voorspelling Kampioen": _kampioen,
    }

    # Topscorer-spelers als afzonderlijke keys
    for i, speler in enumerate(_topscorers, start=1):
        payload[f"Topscorer Speler {i}"] = speler

    # Wedstrijdvelden
    for idx, wedstrijd in enumerate(WEDSTRIJDEN):
        wk = f"w{idx}"
        payload[f"{wedstrijd} (Uitslag)"]           = st.session_state.get(f"{wk}_uitslag", "")
        payload[f"{wedstrijd} (Gele Kaarten)"]      = st.session_state.get(f"{wk}_gele",    "")
        payload[f"{wedstrijd} (Tijd 1e Doelpunt)"]  = st.session_state.get(f"{wk}_tijd",    "")

        # Oranje Special (alleen Nederland - Japan)
        if wedstrijd == "Nederland - Japan":
            payload["Nederland - Japan (Minuut 1e schot op doel)"] = int(
                st.session_state.get(f"{wk}_schot", 15)
            )

    # ── POST naar Google Apps Script ─────────────────────────
    with st.spinner("📤 Jouw voorspelling wordt verzonden naar de server..."):
        try:
            resp = requests.post(
                APPS_SCRIPT_URL,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            if resp.status_code == 200:
                # Markeer als ingestuurd zodat refresh geen dubbele submit veroorzaakt
                st.session_state["ingestuurd"] = True
                st.success(
                    "🎉 **Gelukt! Jouw voorspelling is opgeslagen.**  \n"
                    "Succes in de WK Poule 2026 – wie weet win jij het grote prijs! 🏆"
                )
                st.balloons()
            else:
                st.error(
                    f"❌ Verzenden mislukt (HTTP {resp.status_code}). "
                    "Probeer het over een paar minuten opnieuw of neem contact op "
                    "met de beheerder."
                )
        except Exception as exc:
            st.error(
                f"❌ Verbindingsfout: {exc}.  \n"
                "Controleer je internetverbinding en probeer opnieuw."
            )

# ────────────────────────────────────────────────────────────
# 6.  FOOTER
# ────────────────────────────────────────────────────────────

st.divider()
st.caption(
    "WK Poule 2026 · Kompas Publishing · "
    "Speelronde 1 · Vragen? Neem contact op met de beheerder."
)
