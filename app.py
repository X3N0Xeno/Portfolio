"""
Joseph Xeno O. Banzon — Autobiography & Portfolio
CSIT 349 · Applied AI · Streamlit activity

Theme: inspired by the manga *Tomodachi Game* — a clean black / white / one-red
look, "rounds" instead of pages, and a background made of nodes that bond to
your cursor. No official art or logos are used.

Run:  streamlit run app.py
"""
from __future__ import annotations

import base64
import io
import re
import time
import urllib.parse
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
#  EDIT ME — personal constants
# ─────────────────────────────────────────────────────────────────────────────
NAME = "Joseph Xeno O. Banzon"
SHORT_NAME = "Joseph Xeno Banzon"
COURSE = "CSIT 349 · Applied AI"
SECTION = "Section — F1"
SCHOOL = "Cebu Institute of Technology – University"
PROGRAM = "BS Computer Science"
YEAR_LEVEL = "3rd year"
EMAIL = "josephxeno.contact@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/josephxeno"
GITHUB = "https://github.com/X3N0Xeno"
# Per-project repo links: for now they all point at your GitHub profile.
# Replace each one with the real repository URL when you are ready.
REPO = {
    "delegate": "https://github.com/X3N0Xeno/DeleGate",
    "stashraid": "https://github.com/X3N0Xeno/StashRaid",
    "wildfeast": "https://github.com/X3N0Xeno/WildFEAST",
    "equinox": "https://github.com/X3N0Xeno/Project-Equinox",
    "encore": "https://github.com/asterialumi/Encore",
}

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

ACCENTS = {  # name -> (hex, "r,g,b")
    "Crimson": ("#e11d48", "225,29,72"),
    "Gold": ("#f5b83d", "245,184,61"),
    "Ice": ("#5cc8ff", "92,200,255"),
    "Jade": ("#34d399", "52,211,153"),
    "Violet": ("#a78bfa", "167,139,250"),
}

st.set_page_config(
    page_title=f"{SHORT_NAME} · Portfolio",
    page_icon=":material/diversity_3:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  Online assets (icons + logos)
# ─────────────────────────────────────────────────────────────────────────────
DEVICON = "https://cdn.jsdelivr.net/npm/devicon@2.18.0/icons/{0}/{0}-{1}.svg"
# key -> (label, devicon folder, variant, needs-invert-on-dark)
TECH = {
    "kotlin": ("Kotlin", "kotlin", "original", False),
    "java": ("Java", "java", "original", False),
    "csharp": ("C#", "csharp", "original", False),
    "cpp": ("C++", "cplusplus", "original", False),
    "python": ("Python", "python", "original", False),
    "godot": ("Godot", "godot", "original", False),
    "mysql": ("MySQL", "mysql", "original", False),
    "sqlite": ("SQLite", "sqlite", "original", False),
    "postgres": ("PostgreSQL", "postgresql", "original", False),
    "django": ("Django", "django", "plain", True),
    "android": ("Android Studio", "androidstudio", "original", False),
    "figma": ("Figma", "figma", "original", False),
    "vercel": ("Vercel", "vercel", "original", True),
    "git": ("Git", "git", "original", False),
    "github": ("GitHub", "github", "original", True),
    "dotnet": (".NET", "dotnetcore", "original", False),
}


def tech_url(key: str) -> str:
    _, folder, variant, _ = TECH[key]
    return DEVICON.format(folder, variant)


def ic(name: str, color: str = "f3eee4", cls: str = "x-ico") -> str:
    """Phosphor icon (fill) served by Iconify, as an <img>."""
    return f'<img class="{cls}" alt="" src="https://api.iconify.design/ph/{name}-fill.svg?color=%23{color}">'


def tile(key: str, i: int = 0) -> str:
    label, _, _, inv = TECH[key]
    return (
        f'<div class="x-tech-tile" style="--i:{i}"><img class="{"x-inv" if inv else ""}" '
        f'alt="{label}" loading="lazy" src="{tech_url(key)}"><span>{label}</span></div>'
    )


def chip(text: str, key: str | None = None) -> str:
    img = ""
    if key:
        inv = "x-inv" if TECH[key][3] else ""
        img = f'<img class="{inv}" alt="" src="{tech_url(key)}">'
    return f'<span class="x-chip">{img}{text}</span>'


# ─────────────────────────────────────────────────────────────────────────────
#  Content (everything is sourced from the resume — edit freely)
# ─────────────────────────────────────────────────────────────────────────────
ROUNDS = [
    ("prologue", "Prologue", "home"),
    ("story", "1 · Story", "menu_book"),
    ("skills", "2 · Skills", "bolt"),
    ("projects", "3 · Projects", "deployed_code"),
    ("honors", "4 · Honors", "emoji_events"),
    ("contact", "Final · Contact", "mail"),
]
ROUND_IDS = [r[0] for r in ROUNDS]
ROUND_LABEL = {r[0]: f":material/{r[2]}: {r[1]}" for r in ROUNDS}
ROUND_PLAIN = {r[0]: r[1] for r in ROUNDS}

CHAPTERS = {
    "Origins": (
        "Where it started",
        f"I'm **{SHORT_NAME}**, a Computer Science student at {SCHOOL} in Cebu City, Philippines. "
        "My way in was STEM — I finished Senior High on the STEM track with honors (2022–2024) — "
        "and the pattern was set early: pick a problem, build something that works, then put it in "
        "front of people and see if it holds up. Science fairs and robotics were where that habit began.",
    ),
    "Robotics years": (
        "Competing, then coaching",
        "Robotics taught me teamwork under a clock. I placed **3rd** at the National Virtual Robotics "
        "Competition (2021) and **2nd** at the CESAFI Robotics Cup (2023). In 2022 I took **1st** at the "
        "Division and **2nd** at the Regional level of the LIKHA Science, Technology and Math Fair. "
        "In 2023 I switched seats and mentored a team at RoboQuest — they finished **6th**.",
    ),
    "DOST & CIT-U": (
        "Scholar, designer, organiser",
        "In 2024 I started my BS in Computer Science at CIT-U as a **DOST Undergraduate Scholar**. "
        "Outside class I joined the DOST Scholars' Association (DOST SA CIT-U) as a Creatives Committee "
        "member and **Director for Events and Logistics**, handling visual branding and keeping scholar "
        "events running. I'm also part of DOST SA SIETE (regional), the SPARKS Collective, and START-DOST (national).",
    ),
    "Right now": (
        "Building across stacks",
        "These days I build in whatever the problem needs: Kotlin for Android, Java and JavaFX for desktop, "
        "Python and Django for the web, C# for simulations, and Godot for 2D games. What ties it together is "
        "structure first — MVP on Android, normalised schemas on the back end — and then polish on top.",
    ),
}

TIMELINE = [
    ("2021", "3rd · National Virtual Robotics Competition", "The first podium — and the start of competing seriously.", "robot"),
    ("2022", "LIKHA Science, Technology & Math Fair", "1st at Division level, 2nd at Regional level. Started the STEM track at CIT-U Senior High.", "flask"),
    ("2023", "CESAFI Robotics Cup & RoboQuest", "2nd place as a competitor, then mentored a team to 6th at RoboQuest.", "medal"),
    ("2024", "Honors graduate → DOST Scholar", "Finished Senior High with honors and began BS Computer Science at CIT-U.", "graduation-cap"),
    ("2024–25", "DOST SA CIT-U leadership", "Creatives Committee and Director for Events and Logistics.", "users-three"),
    ("Now", "Shipping projects across five stacks", "Android, desktop, web, simulation and games — five featured projects and counting.", "rocket-launch"),
]

INTERESTS = {
    "Game development": ("game-controller", "Godot is where I experiment most — custom physics loops, tilemap collisions, rhythm-synchronised mechanics and the in-engine tools that make levels faster to build."),
    "Robotics": ("robot", "Three competition podiums and one mentoring seat. Robotics is where I learned to debug a system that physically refuses to cooperate."),
    "Simulations": ("cpu", "Fuzzy logic, weather dynamics and population evolution: I like systems where simple rules produce surprising behaviour."),
    "Manga & visual storytelling": ("book-open-text", "Tomodachi Game is my favourite manga. Its clean, simple art style never loses detail and still reaches incredible visuals without leaning on realism — which is the exact balance I wanted for this site."),
}

# name, kind, domain, level (self-rated 0-100 — EDIT THESE to your own numbers), logo key
SKILLS = [
    ("Kotlin", "Language", "Mobile", 82, "kotlin"),
    ("Android Studio (MVP)", "Framework", "Mobile", 80, "android"),
    ("XML layouts", "Markup", "Mobile", 78, None),
    ("Java", "Language", "Desktop & Sim", 90, "java"),
    ("JavaFX", "Framework", "Desktop & Sim", 90, "java"),
    ("C#", "Language", "Desktop & Sim", 85, "csharp"),
    (".NET WinForms", "Framework", "Desktop & Sim", 70, "dotnet"),
    ("Simulation logic", "Concept", "Desktop & Sim", 75, None),
    ("Python", "Language", "Web", 90, "python"),
    ("Django", "Framework", "Web", 75, "django"),
    ("Vercel", "Tool", "Web", 90, "vercel"),
    ("GDScript", "Language", "Games", 90, "godot"),
    ("Godot Engine", "Framework", "Games", 95, "godot"),
    ("SQL", "Language", "Data", 80, "mysql"),
    ("MySQL", "Tool", "Data", 80, "mysql"),
    ("SQLite", "Tool", "Data", 80, "sqlite"),
    ("Figma", "Tool", "Design", 90, "figma"),
    ("UI/UX design", "Concept", "Design", 80, "figma"),
    ("C++", "Language", "Core CS", 90, "cpp"),
    ("Git & GitHub", "Tool", "Core CS", 85, "git"),
    ("OOP", "Concept", "Core CS", 85, None),
    ("Data structures & algorithms", "Concept", "Core CS", 80, None),
]
DOMAINS = ["Mobile", "Games", "Web", "Desktop & Sim", "Data", "Design", "Core CS"]

PROJECTS = [
    {
        "id": "delegate",
        "title": "DeleGate",
        "subtitle": "Project & Production Tracker",
        "domain": "Web",
        "role": "Architect & full-stack developer",
        "tools": ["python", "django", "sqlite", "postgres"],
        "stack": ["Python", "Django", "SQLite"],
        "summary": "A web app for tracking project progress, coordinating team workflow and delegating resources.",
        "built": [
            "Architected and deployed the application end to end.",
            "Designed relational models and customised user-permission flows.",
            "Implemented responsive front-end management views.",
        ],
        "outcome": "Deployed web application for team progress tracking and resource delegation.",
        "icon": "kanban",
    },
    {
        "id": "stashraid",
        "title": "StashRaid",
        "subtitle": "Android Study & Notes App",
        "domain": "Mobile",
        "role": "Android developer",
        "tools": ["kotlin", "android"],
        "stack": ["Kotlin", "Android Studio (MVP)", "XML layouts"],
        "summary": "An offline-capable study app for fast note organisation and revision indexing.",
        "built": [
            "Structured the app with Model-View-Presenter for clean, modular separation.",
            "Built responsive custom XML layouts.",
            "Kept local data persistence for quick note organisation and revision indexing.",
        ],
        "outcome": "Working offline-first Android app with local persistence.",
        "icon": "device-mobile",
    },
    {
        "id": "wildfeast",
        "title": "WildFEAST",
        "subtitle": "Online Canteen Ordering System",
        "domain": "Desktop & Sim",
        "role": "Full-stack developer",
        "tools": ["java", "mysql"],
        "stack": ["Java", "JavaFX", "MySQL"],
        "summary": "An ordering platform with separate dashboards for cafeteria merchants and student customers.",
        "built": [
            "Built distinct portal dashboards for merchants and students.",
            "Engineered normalised relational tables in MySQL.",
            "Integrated JDBC for live order queues, inventory updates and transactions.",
        ],
        "outcome": "Two-sided ordering system with live queues, inventory and transactions.",
        "icon": "fork-knife",
    },
    {
        "id": "equinox",
        "title": "Project Equinox / SeasonFuzzy",
        "subtitle": "Systems Simulation Engine",
        "domain": "Desktop & Sim",
        "role": "Designer & developer",
        "tools": ["csharp", "dotnet"],
        "stack": ["C#", ".NET WinForms", "Simulation logic"],
        "summary": "A desktop engine modelling weather dynamics, fuzzy-logic decisions and population evolution.",
        "built": [
            "Designed a multi-variable simulation engine for weather, fuzzy logic and population evolution.",
            "Created real-time graphic visualisation components.",
            "Wrote algorithmic state evaluators to drive the simulation.",
        ],
        "outcome": "Real-time desktop simulation with live visualisation.",
        "icon": "cloud-sun",
    },
    {
        "id": "encore",
        "title": "Encore & Revelation",
        "subtitle": "2D Interactive Games",
        "domain": "Games",
        "role": "Game developer & tools builder",
        "tools": ["godot"],
        "stack": ["GDScript", "Godot Engine"],
        "summary": "2D gameplay prototypes with custom physics, tilemap collisions and rhythm-synced mechanics.",
        "built": [
            "Built 2D prototypes with custom physics loops and tilemap collision boundaries.",
            "Implemented rhythm-synchronised mechanics.",
            "Created in-engine level-design utilities and dynamic event handling.",
        ],
        "outcome": "Playable 2D game prototypes with in-engine level tooling.",
        "icon": "music-notes",
    },
]

# year, achievement, category, where, rank (1/2/3, 0 = not a placement)
HONORS = [
    (2021, "3rd Place — National Virtual Robotics Competition", "Robotics", "National", 3),
    (2022, "1st Place — Division Science, Technology & Math Fair (LIKHA)", "STEM fair", "Division", 1),
    (2022, "2nd Place — Regional Science, Technology & Math Fair (LIKHA)", "STEM fair", "Regional", 2),
    (2023, "2nd Place — CESAFI Robotics Cup", "Robotics", "CESAFI", 2),
    (2023, "Robotics Mentor — RoboQuest 2023 (mentored the 6th-place team)", "Mentoring", "RoboQuest", 0),
    (2024, "Graduated with Honors — CIT-U Senior High (STEM)", "Academic", "CIT-U", 0),
    (2024, "DOST Undergraduate Scholar — CIT-U BS Computer Science", "Academic", "DOST", 0),
    (2024, "Creatives Committee Member & Director for Events and Logistics — DOST SA CIT-U", "Leadership", "CIT-U", 0),
    (2024, "Member — START-DOST (National) · DOST SA SIETE · SPARKS Collective", "Leadership", "DOST network", 0),
]


# ─────────────────────────────────────────────────────────────────────────────
#  Cached data
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def skills_df() -> pd.DataFrame:
    rows = []
    for name, kind, domain, level, logo in SKILLS:
        used = [p["title"].split(" / ")[0] for p in PROJECTS if name in p["stack"]]
        tier = "Strong" if level >= 80 else "Solid" if level >= 70 else "Growing"
        rows.append(
            {
                "Logo": tech_url(logo) if logo else "",
                "Skill": name,
                "Type": kind,
                "Domain": domain,
                "Trust level": level,
                "Tier": tier,
                "Used in": ", ".join(used) if used else "—",
            }
        )
    return pd.DataFrame(rows)


@st.cache_data
def honors_df() -> pd.DataFrame:
    return pd.DataFrame(HONORS, columns=["Year", "Achievement", "Category", "Where", "Rank"])


# ─────────────────────────────────────────────────────────────────────────────
#  Session state + theme
# ─────────────────────────────────────────────────────────────────────────────
ss = st.session_state
ss.setdefault("round", "prologue")
ss.setdefault("round_prev", "prologue")
ss.setdefault("visited", {"prologue"})
ss.setdefault("messages", [])
ss.setdefault("calm", False)
ss.setdefault("accent", "Crimson")


def _keep_round() -> None:
    """The segmented control can be un-selected; always keep one round active."""
    if ss.round is None:
        ss.round = ss.round_prev
    else:
        ss.round_prev = ss.round


def jump(round_id: str) -> None:
    ss.round = round_id
    ss.round_prev = round_id


current = ss.round or ss.round_prev
ss.visited = set(ss.visited) | {current}
ACCENT_HEX, ACCENT_RGB = ACCENTS[ss.accent]

css = (BASE / "style.css").read_text(encoding="utf-8")
js = (BASE / "fx.js").read_text(encoding="utf-8")
# st.html sanitises script text: "<" directly followed by a letter, "/" or "!" gets the whole script dropped.
assert not re.search(r"<[A-Za-z/!]", js), "fx.js contains a character sequence the HTML sanitiser rejects"
calm_css = ""
if ss.calm:
    calm_css = (
        '[data-testid="stApp"] *,[data-testid="stApp"] *::before,[data-testid="stApp"] *::after{animation:none!important}'
        "#xeno-ring,#xeno-dot{display:none!important}"
    )
st.html(
    f"<style>{css}\n:root{{--accent:{ACCENT_HEX};--accent-rgb:{ACCENT_RGB};--calm:{1 if ss.calm else 0}}}\n{calm_css}</style>"
)
st.html(f"<script>{js}</script>", unsafe_allow_javascript=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Photo (assets/photo.* > uploaded in sidebar > online avatar stand-in)
# ─────────────────────────────────────────────────────────────────────────────
SILHOUETTE = "data:image/svg+xml;utf8," + urllib.parse.quote(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 500'><rect width='400' height='500' fill='#1a1a26'/>"
    "<circle cx='200' cy='190' r='72' fill='#2a2a3c'/><path d='M60 500c0-95 62-150 140-150s140 55 140 150z' fill='#2a2a3c'/></svg>"
)
AVATAR = "https://api.dicebear.com/9.x/notionists/svg?seed=JosephXeno&backgroundColor=1a1a26"


def photo_source() -> tuple[str, bool]:
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = ASSETS / f"photo.{ext}"
        if p.exists():
            return f"data:image/{ext.replace('jpg', 'jpeg')};base64," + base64.b64encode(p.read_bytes()).decode(), True
    if ss.get("photo_b64"):
        return ss.photo_b64, True
    return AVATAR, False


def photo_html(compact: bool = False) -> str:
    src, real = photo_source()
    tag = "Joseph Xeno · portrait" if real else "Stand-in avatar · swap in your photo"
    seal = "" if compact else f'<div class="seal">CS<br>{date.today().year}</div>'
    return (
        f'<div class="x-photo"><div class="img" style="background-image:url(\'{src}\'),url(\'{SILHOUETTE}\')"></div>'
        f'{seal}<div class="tag">{tag}</div></div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Reusable pieces
# ─────────────────────────────────────────────────────────────────────────────
def autobiography_md() -> str:
    parts = [f"# {NAME}\n", f"{PROGRAM} · {SCHOOL} · DOST Undergraduate Scholar\n"]
    for title, (sub, body) in CHAPTERS.items():
        parts.append(f"## {title} — {sub}\n\n{body}\n")
    parts.append("## Timeline\n")
    parts += [f"- **{y}** — {t}: {d}" for y, t, d, _ in TIMELINE]
    return "\n".join(parts)


def round_banner(rid: str, n: str, title: str, sub: str) -> None:
    st.html(
        f'<div class="x-round" data-round="{rid}"><div class="no">{n}</div>'
        f'<h2 data-ghost="{title}">{title}</h2><p>{sub}</p></div>'
    )


def next_round(rid: str) -> None:
    nxt = ROUND_IDS[ROUND_IDS.index(rid) + 1]
    st.write("")
    c1, _ = st.columns([1, 2])
    c1.button(
        f"Next · {ROUND_PLAIN[nxt]}",
        icon=":material/arrow_forward:",
        type="primary",
        key=f"next_{rid}",
        on_click=jump,
        args=(nxt,),
        width="stretch",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.html(
        f'<div style="display:flex;align-items:center;gap:.8rem;margin:.2rem 0 .6rem">'
        f'<div style="width:54px;height:54px;border-radius:14px;background:url(\'{photo_source()[0]}\') center/cover,url(\'{SILHOUETTE}\') center/cover;'
        f'border:2px solid var(--accent);flex:none"></div>'
        f'<div><div style="font:400 1.5rem var(--display);letter-spacing:.04em;line-height:1">{SHORT_NAME}</div>'
        f'<div style="font:500 .68rem var(--mono);letter-spacing:.12em;color:var(--muted);text-transform:uppercase;margin-top:.25rem">'
        f"{COURSE}<br>{SECTION}</div></div></div>"
    )
    st.divider()

    st.markdown("##### Rounds cleared")
    done = len(ss.visited)
    st.progress(done / len(ROUNDS), text=f"{done} of {len(ROUNDS)} explored")
    rows = ""
    for rid, label, _ in ROUNDS:
        seen = rid in ss.visited
        here = rid == current
        col = ACCENT_HEX.lstrip("#") if seen else "5b5868"
        weight = "700" if here else "500"
        color = "var(--paper)" if seen else "var(--muted)"
        mark = "check-circle" if seen else "circle"
        rows += (
            f'<div style="display:flex;align-items:center;gap:.5rem;padding:.18rem 0;font:{weight} .85rem var(--body);color:{color}">'
            f'{ic(mark, col)}{label}{"  ◂" if here else ""}</div>'
        )
    st.html(f'<div style="margin:.3rem 0 .2rem">{rows}</div>')
    st.divider()

    st.markdown("##### Comfort")
    st.toggle(
        "Calm mode",
        key="calm",
        help="Turns off the moving background, cursor ring, card tilt and animations. The content stays identical.",
    )
    with st.expander("Swap in your photo", icon=":material/add_a_photo:"):
        up = st.file_uploader("Upload a portrait", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")
        if up is not None:
            from PIL import Image

            img = Image.open(up).convert("RGB")
            img.thumbnail((700, 875))
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=86)
            ss.photo_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
            st.caption("Applied for this session. To make it permanent, save the file as `assets/photo.jpg`.")
    st.divider()

    resume_path = ASSETS / "Resume.docx"
    if resume_path.exists():
        st.download_button(
            "Download résumé",
            resume_path.read_bytes(),
            file_name="Resume - Joseph Xeno O. Banzon.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            icon=":material/download:",
            width="stretch",
        )
    st.download_button(
        "Download my story (.md)",
        autobiography_md(),
        file_name="autobiography.md",
        mime="text/markdown",
        icon=":material/description:",
        width="stretch",
    )
    st.link_button("GitHub", GITHUB, icon=":material/code:", width="stretch")
    st.link_button("LinkedIn", LINKEDIN, icon=":material/work:", width="stretch")
    st.link_button("Email me", f"mailto:{EMAIL}", icon=":material/mail:", width="stretch")

# ─────────────────────────────────────────────────────────────────────────────
#  Top bar + sticky round navigator
# ─────────────────────────────────────────────────────────────────────────────
st.html(
    f'<div class="x-brand"><div class="l"><span class="x-live"></span><span><b>{NAME}</b></span></div>'
    f"<div>{COURSE} · <b>{SECTION}</b></div></div>"
)
with st.container(key="nav"):
    st.segmented_control(
        "Round",
        options=ROUND_IDS,
        format_func=lambda r: ROUND_LABEL[r],
        key="round",
        selection_mode="single",
        label_visibility="collapsed",
        width="stretch",
        on_change=_keep_round,
    )


# ═════════════════════════════════════════════════════════════════════════════
#  PROLOGUE
# ═════════════════════════════════════════════════════════════════════════════
def prologue() -> None:
    left, right = st.columns([1.4, 1], gap="large", vertical_alignment="center")
    with left:
        st.html(
            f"""
<div data-round="prologue">
  <div class="x-eyebrow"><i></i>Autobiography &amp; portfolio</div>
  <h1 class="x-name">Joseph<br><span class="o">Xeno</span> Banzon</h1>
  <div class="x-line">I build
    <span class="x-roles"><ul><li>Android apps.</li><li>games.</li><li>simulations.</li><li>web tools.</li><li>Android apps.</li></ul></span>
  </div>
  <p class="x-bio"><b>{PROGRAM}, {YEAR_LEVEL}</b> at {SCHOOL}, and a <b>DOST Undergraduate Scholar</b>.
  Robotics competitor turned mentor, campus organiser, and a developer who likes clean structure under a polished surface.</p>
</div>"""
        )
        b1, b2, b3, _ = st.columns([1.15, 1, 1, 0.6])
        b1.button("Start Round 1", icon=":material/play_arrow:", type="primary", key="start", on_click=jump, args=("story",), width="stretch")
        b2.button("See projects", icon=":material/deployed_code:", key="to_proj", on_click=jump, args=("projects",), width="stretch")
        b3.link_button("GitHub", GITHUB, icon=":material/code:", width="stretch")
    with right:
        st.html(photo_html())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Featured projects", len(PROJECTS), "5 stacks", delta_color="off")
    m2.metric("Podium finishes", 4, "1st · 2nd · 2nd · 3rd", delta_color="off")
    m3.metric("Languages", 7, "Kotlin → GDScript", delta_color="off")
    m4.metric("Scholar since", "2024", "DOST · CIT-U", delta_color="off")

    st.write("")
    a, b = st.columns([1.15, 1], gap="large")
    with a:
        with st.container(border=True, key="card-theme"):
            st.html(
                f'<div style="padding:.3rem .2rem"><div class="x-eyebrow" style="margin-bottom:.5rem">{ic("mask-happy", ACCENT_HEX.lstrip("#"))}Why this site looks like this</div>'
                '<p style="color:var(--muted);line-height:1.75;margin:0">I built this around <b style="color:var(--paper)">Tomodachi Game</b>, my favourite manga. '
                "Its art keeps a simple base — clean lines, flat black and white — without losing detail, and still reaches incredible visuals without needing realism. "
                "I borrowed that balance: a plain black-and-white page with one red accent, and detail only where it earns its place. "
                "The background is a web of nodes that bond to your cursor; the pages are <b style=\"color:var(--paper)\">rounds</b>. "
                "If it ever feels like too much, <b style=\"color:var(--paper)\">Calm mode</b> in the sidebar turns every effect off.</p></div>"
            )
    with b:
        with st.container(border=True, key="card-facts"):
            st.markdown("##### Fast facts")
            facts = pd.DataFrame(
                {
                    "": ["Name", "Program", "Year", "School", "Scholarship", "Based in", "Course"],
                    " ": [NAME, PROGRAM, YEAR_LEVEL, SCHOOL, "DOST Undergraduate Scholar", "Cebu, Philippines", f"{COURSE} · {SECTION}"],
                }
            )
            st.table(facts.set_index(""))
    next_round("prologue")


# ═════════════════════════════════════════════════════════════════════════════
#  ROUND 1 — STORY
# ═════════════════════════════════════════════════════════════════════════════
@st.fragment
def interests_block() -> None:
    st.markdown("### What pulls me in")
    pick = st.radio("Interest", list(INTERESTS), horizontal=True, label_visibility="collapsed", key="interest")
    icon, text = INTERESTS[pick]
    with st.container(border=True, key="card-interest"):
        st.html(
            f'<div style="display:flex;gap:1.1rem;align-items:flex-start;padding:.3rem .2rem">'
            f'<div style="flex:none;width:58px;height:58px;border-radius:16px;display:grid;place-items:center;background:rgba(var(--accent-rgb),.14);border:1px solid rgba(var(--accent-rgb),.5)">'
            f'<img style="width:30px;height:30px" alt="" src="https://api.iconify.design/ph/{icon}-fill.svg?color=%23{ACCENT_HEX.lstrip("#")}"></div>'
            f'<div><h4 style="margin:0 0 .3rem;font:600 1.1rem var(--body)">{pick}</h4>'
            f'<p style="margin:0;color:var(--muted);line-height:1.7">{text}</p></div></div>'
        )


def story() -> None:
    round_banner("story", "ROUND 01", "The story so far", "Background, education and the moments that shaped how I work — in order.")
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        tabs = st.tabs(list(CHAPTERS))
        for tab, (name, (sub, body)) in zip(tabs, CHAPTERS.items()):
            with tab:
                st.markdown(f"### {sub}")
                st.markdown(body)
        st.write("")
        interests_block()
    with right:
        items = "".join(
            f'<div class="x-tl-item" style="--i:{i}"><div class="node">{ic(icon, "f3eee4")}</div>'
            f'<div class="yr">{y}</div><h4>{t}</h4><p>{d}</p></div>'
            for i, (y, t, d, icon) in enumerate(TIMELINE)
        )
        with st.container(border=True, key="card-timeline"):
            st.markdown("##### Milestones")
            st.html(f'<div class="x-tl">{items}</div>')
    next_round("story")


# ═════════════════════════════════════════════════════════════════════════════
#  ROUND 2 — SKILLS
# ═════════════════════════════════════════════════════════════════════════════
def radar_fig() -> go.Figure:
    df = skills_df()
    vals = [round(df[df.Domain == d]["Trust level"].mean()) for d in DOMAINS]
    fig = go.Figure(
        go.Scatterpolar(
            r=vals + vals[:1],
            theta=DOMAINS + DOMAINS[:1],
            fill="toself",
            fillcolor=f"rgba({ACCENT_RGB},0.28)",
            line=dict(color=ACCENT_HEX, width=2.5),
            marker=dict(size=7, color=ACCENT_HEX),
            hovertemplate="%{theta}: %{r}<extra></extra>",
        )
    )
    fig.update_layout(
        height=390,
        margin=dict(l=90, r=90, t=20, b=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f3eee4", family="Inter, sans-serif", size=13),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], tickvals=[25, 50, 75, 100], gridcolor="rgba(243,238,228,.12)", linecolor="rgba(243,238,228,.12)", tickfont=dict(size=10, color="#9b97a8")),
            angularaxis=dict(gridcolor="rgba(243,238,228,.12)", linecolor="rgba(243,238,228,.2)"),
        ),
    )
    return fig


@st.fragment
def skills_explorer() -> None:
    df = skills_df()
    st.markdown("### Skill explorer")
    f1, f2, f3 = st.columns([1.4, 1, 1])
    domains = f1.multiselect("Domain", DOMAINS, default=DOMAINS, placeholder="Pick domains")
    kinds = f2.pills("Type", sorted(df.Type.unique()), selection_mode="multi", default=sorted(df.Type.unique()))
    floor = f3.slider("Minimum trust level", 50, 90, 50, step=5)
    view = df[df.Domain.isin(domains) & df.Type.isin(kinds) & (df["Trust level"] >= floor)].sort_values("Trust level", ascending=False)
    st.dataframe(
        view,
        hide_index=True,
        width="stretch",
        height=min(560, 38 * (len(view) + 1) + 3),
        column_config={
            "Logo": st.column_config.ImageColumn("", width="small"),
            "Trust level": st.column_config.ProgressColumn("Trust level", min_value=0, max_value=100, format="%d"),
            "Used in": st.column_config.TextColumn("Used in", width="medium"),
        },
    )
    st.caption(f"Showing {len(view)} of {len(df)} skills. Trust level is self-rated: how much I'd bet on myself with it.")


@st.fragment
def skill_spotlight() -> None:
    df = skills_df()
    st.markdown("##### Skill spotlight")
    name = st.selectbox("Inspect a skill", df.Skill.tolist(), index=df.Skill.tolist().index("Kotlin"), label_visibility="collapsed")
    row = df[df.Skill == name].iloc[0]
    logo = f'<img src="{row.Logo}" style="width:34px;height:34px">' if row.Logo else ic("code", ACCENT_HEX.lstrip("#"), "")
    st.html(
        f'<div style="display:flex;align-items:center;gap:.8rem;margin:.2rem 0 .4rem">{logo}'
        f'<div><div style="font:700 1.05rem var(--body)">{row.Skill}</div>'
        f'<div style="font:500 .68rem var(--mono);letter-spacing:.14em;color:var(--muted);text-transform:uppercase">{row.Domain} · {row.Type} · {row.Tier}</div></div></div>'
    )
    st.progress(int(row["Trust level"]) / 100, text=f"Trust level {int(row['Trust level'])}/100")
    st.caption(f"Used in: {row['Used in']}")


def skills() -> None:
    round_banner("skills", "ROUND 02", "What I can bring", "The toolbox, with honest self-ratings you can filter, sort and inspect.")
    a, b = st.columns([1.1, 1], gap="large")
    with a:
        with st.container(border=True, key="card-radar"):
            st.markdown("##### Strength by domain")
            st.plotly_chart(radar_fig(), width="stretch", theme=None, config={"displayModeBar": False})
    with b:
        with st.container(border=True, key="card-spot"):
            skill_spotlight()
        keys = ["kotlin", "java", "python", "csharp", "cpp", "godot", "mysql", "sqlite", "django", "android", "figma", "git", "github", "vercel"]
        st.html('<div class="x-tech" style="margin-top:.4rem">' + "".join(tile(k, i) for i, k in enumerate(keys)) + "</div>")
    st.write("")
    skills_explorer()
    next_round("skills")


# ═════════════════════════════════════════════════════════════════════════════
#  ROUND 3 — PROJECTS
# ═════════════════════════════════════════════════════════════════════════════
@st.dialog("Case file", width="large")
def case_file(pid: str) -> None:
    p = next(x for x in PROJECTS if x["id"] == pid)
    st.html(
        f'<div class="x-eyebrow" style="margin-bottom:.3rem">{ic(p["icon"], ACCENT_HEX.lstrip("#"))}{p["domain"]}</div>'
        f'<div style="font:400 2.6rem var(--display);letter-spacing:.03em;line-height:1;text-transform:uppercase">{p["title"]}</div>'
        f'<div style="color:var(--muted);margin:.3rem 0 .6rem">{p["subtitle"]}</div>'
    )
    t1, t2, t3 = st.tabs(["Overview", "What I built", "Stack"])
    with t1:
        c1, c2 = st.columns(2)
        c1.metric("My role", p["role"])
        c2.metric("Domain", p["domain"])
        st.markdown(f"**Summary** — {p['summary']}")
        st.success(f"**Outcome:** {p['outcome']}", icon=":material/flag:")
    with t2:
        for line in p["built"]:
            st.markdown(f"- {line}")
    with t3:
        st.html('<div class="x-tech">' + "".join(tile(k, i) for i, k in enumerate(p["tools"])) + "</div>")
        st.caption("Skills exercised: " + ", ".join(p["stack"]))
    st.link_button("View code on GitHub", REPO[pid], icon=":material/open_in_new:")


@st.fragment
def project_board() -> None:
    all_tags = sorted({p["domain"] for p in PROJECTS})
    f1, f2 = st.columns([2, 1])
    tags = f1.pills("Filter by domain", all_tags, selection_mode="multi", default=all_tags)
    order = f2.selectbox("Sort", ["Featured order", "Title (A→Z)", "Domain"], label_visibility="visible")
    shown = [p for p in PROJECTS if p["domain"] in tags]
    if order == "Title (A→Z)":
        shown.sort(key=lambda p: p["title"].lower())
    elif order == "Domain":
        shown.sort(key=lambda p: p["domain"])
    if not shown:
        st.info("No projects match — pick at least one domain.", icon=":material/filter_alt_off:")
    cols = st.columns(2, gap="large")
    for i, p in enumerate(shown):
        with cols[i % 2]:
            with st.container(border=True, key=f"card-p-{p['id']}"):
                logos = "".join(
                    f'<img class="{"x-inv" if TECH[k][3] else ""}" alt="{TECH[k][0]}" style="width:30px;height:30px" src="{tech_url(k)}">' for k in p["tools"]
                )
                st.html(
                    f'<div style="padding:.2rem .1rem">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center">'
                    f'<div class="x-eyebrow" style="margin:0">{ic(p["icon"], ACCENT_HEX.lstrip("#"))}{p["domain"]}</div>'
                    f'<div style="display:flex;gap:.5rem">{logos}</div></div>'
                    f'<div style="font:400 2.1rem var(--display);letter-spacing:.03em;line-height:1;margin:.8rem 0 .15rem;text-transform:uppercase">{p["title"]}</div>'
                    f'<div style="color:var(--muted);font-size:.88rem;margin-bottom:.7rem">{p["subtitle"]}</div>'
                    f'<p style="color:#cfcabd;line-height:1.65;margin:0 0 .5rem;font-size:.95rem">{p["summary"]}</p>'
                    f'<div class="x-chips">{chip("Role · " + p["role"])}{"".join(chip(TECH[k][0], k) for k in p["tools"])}</div></div>'
                )
                b1, b2 = st.columns(2)
                if b1.button("Open case file", icon=":material/folder_open:", key=f"open_{p['id']}", type="primary", width="stretch"):
                    case_file(p["id"])
                b2.link_button("Code", REPO[p["id"]], icon=":material/code:", width="stretch")


def projects() -> None:
    round_banner("projects", "ROUND 03", "Proof of work", "Five projects across mobile, web, desktop, simulation and games. Open a case file for the details.")
    project_board()
    with st.expander("Compare every project at a glance", icon=":material/table_chart:"):
        keys = ["python", "django", "kotlin", "android", "java", "mysql", "csharp", "dotnet", "godot"]
        matrix = pd.DataFrame(
            {
                "Project": [p["title"] for p in PROJECTS],
                "Domain": [p["domain"] for p in PROJECTS],
                "Role": [p["role"] for p in PROJECTS],
                **{TECH[k][0]: [k in p["tools"] for p in PROJECTS] for k in keys},
            }
        )
        st.dataframe(matrix, hide_index=True, width="stretch")
    next_round("projects")


# ═════════════════════════════════════════════════════════════════════════════
#  ROUND 4 — HONORS
# ═════════════════════════════════════════════════════════════════════════════
@st.fragment
def honors_board() -> None:
    df = honors_df()
    f1, f2 = st.columns([1, 1.2])
    y0, y1 = f1.select_slider("Years", options=sorted(df.Year.unique()), value=(int(df.Year.min()), int(df.Year.max())))
    cats = f2.pills("Category", sorted(df.Category.unique()), selection_mode="multi", default=sorted(df.Category.unique()))
    view = df[(df.Year.between(y0, y1)) & (df.Category.isin(cats))]
    c1, c2 = st.columns([1, 1.3], gap="large")
    with c1:
        with st.container(border=True, key="card-chart"):
            st.markdown("##### Milestones per year")
            if view.empty:
                st.info("Nothing in that range.")
            else:
                pivot = view.pivot_table(index="Year", columns="Category", values="Achievement", aggfunc="count", fill_value=0)
                palette = [ACCENT_HEX, "#f3eee4", "#9b97a8", "#f5b83d", "#5cc8ff", "#34d399"]
                st.bar_chart(pivot, color=palette[: len(pivot.columns)], height=300)
    with c2:
        st.dataframe(
            view.sort_values("Year", ascending=False),
            hide_index=True,
            width="stretch",
            column_config={
                "Year": st.column_config.NumberColumn(format="%d", width="small"),
                "Achievement": st.column_config.TextColumn(width="large"),
                "Rank": st.column_config.NumberColumn("Place", help="1/2/3 = podium finish, 0 = not a ranked result", format="%d", width="small"),
            },
        )


def honors() -> None:
    round_banner("honors", "ROUND 04", "Receipts", "Competitions, recognition and the communities I've helped run.")
    df = honors_df()
    m = st.columns(4)
    m[0].metric("1st places", int((df.Rank == 1).sum()))
    m[1].metric("2nd places", int((df.Rank == 2).sum()))
    m[2].metric("3rd places", int((df.Rank == 3).sum()))
    m[3].metric("Teams mentored", 1)
    st.write("")
    honors_board()
    st.markdown("### Leadership & networks")
    a, b, c = st.columns(3, gap="medium")
    cards = [
        (a, "users-three", "DOST SA CIT-U", "Creatives Committee Member & Director for Events and Logistics (2024–2025). Led visual branding and supported event logistics for scholar assemblies."),
        (b, "compass", "Regional network", "Member, DOST SA SIETE (Regional) and the SPARKS Collective (2024–2025)."),
        (c, "flag-checkered", "National network", "Member, START-DOST (National), 2024 – present."),
    ]
    for col, icon, title, text in cards:
        col.html(f'<div class="x-card x-tilt" style="height:100%"><div style="margin-bottom:.5rem">{ic(icon, ACCENT_HEX.lstrip("#"), "x-ico")}</div><h4>{title}</h4><p>{text}</p></div>')
    next_round("honors")


# ═════════════════════════════════════════════════════════════════════════════
#  FINAL ROUND — CONTACT
# ═════════════════════════════════════════════════════════════════════════════
def contact() -> None:
    round_banner("contact", "FINAL ROUND", "Let's talk", "Collaboration, internships, questions about a project, or feedback on this site — send a message below.")
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        with st.form("contact_form", clear_on_submit=True, border=True):
            c1, c2 = st.columns(2)
            who = c1.text_input("Your name *", placeholder="Ada Lovelace")
            mail = c2.text_input("Your email *", placeholder="you@example.com")
            topic = st.selectbox("What's this about?", ["Say hi", "Collaboration / project", "Internship or job", "Feedback on this site", "Question about my work"])
            c3, c4 = st.columns(2)
            reply = c3.radio("Best way to reply", ["Email", "LinkedIn"], horizontal=True)
            speed = c4.select_slider("How soon?", ["Whenever", "This week", "Soon", "Urgent"], value="This week")
            body = st.text_area("Message *", height=150, placeholder="What would you like to talk about?")
            ok = st.checkbox("It's fine to reply using the details above")
            sent = st.form_submit_button("Send message", type="primary", icon=":material/send:")
        if sent:
            problems = []
            if not who.strip():
                problems.append("your name")
            if "@" not in mail or "." not in mail.split("@")[-1]:
                problems.append("a valid email")
            if len(body.strip()) < 10:
                problems.append("a message (10+ characters)")
            if not ok:
                problems.append("permission to reply")
            if problems:
                st.error("Almost there — still needed: " + ", ".join(problems) + ".", icon=":material/error:")
            else:
                with st.status("Preparing your message…", expanded=True) as status:
                    st.write("Checking the details")
                    time.sleep(0.45)
                    st.write("Packaging it for email")
                    time.sleep(0.45)
                    status.update(label="Message ready", state="complete", expanded=False)
                ss.messages.append({"who": who.strip(), "mail": mail.strip(), "topic": topic, "reply": reply, "speed": speed, "body": body.strip()})
                st.toast("Message prepared — one last click to send it.", icon=":material/mark_email_read:")
                st.balloons()
        if ss.messages:
            m = ss.messages[-1]
            subject = f"[Portfolio] {m['topic']} — from {m['who']}"
            text = f"{m['body']}\n\n— {m['who']} ({m['mail']})\nPrefers: {m['reply']} · Reply speed: {m['speed']}"
            link = f"mailto:{EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(text)}"
            with st.container(border=True, key="card-receipt"):
                st.markdown(f"##### Thanks, {m['who'].split()[0]}!")
                st.caption(f"Topic: {m['topic']} · Reply via {m['reply']} · Speed: {m['speed']}")
                st.markdown("> " + m["body"].replace("\n", "\n> "))
                st.link_button("Open in my email app to send", link, icon=":material/outgoing_mail:", type="primary")
                st.caption("This site has no server-side inbox, so the button above hands the message to your email app.")
    with right:
        for icon, title, sub, href in [
            ("envelope-simple", "Email", EMAIL, f"mailto:{EMAIL}"),
            ("linkedin-logo", "LinkedIn", "in/josephxeno", LINKEDIN),
            ("github-logo", "GitHub", "X3N0Xeno", GITHUB),
        ]:
            st.html(
                f'<a href="{href}" target="_blank" style="text-decoration:none"><div class="x-card x-tilt x-hot" style="display:flex;align-items:center;gap:1rem;margin-bottom:.8rem">'
                f'<div style="width:46px;height:46px;border-radius:12px;display:grid;place-items:center;background:rgba(var(--accent-rgb),.14);border:1px solid rgba(var(--accent-rgb),.5)">'
                f'{ic(icon, ACCENT_HEX.lstrip("#"), "")}</div>'
                f'<div><div style="font:700 .98rem var(--body);color:var(--paper)">{title}</div>'
                f'<div style="font:500 .8rem var(--mono);color:var(--muted)">{sub}</div></div></div></a>'
            )
        with st.container(border=True, key="card-feedback"):
            st.markdown("##### Rate this site")
            stars = st.feedback("stars", key="stars")
            if stars is not None:
                st.caption(["Ouch — tell me what to fix above.", "Noted — thank you.", "Good to know.", "Glad you liked it!", "That made my day."][stars])
        with st.popover("About this build", icon=":material/info:", width="stretch"):
            st.markdown(
                "Built with **Streamlit** — tabs, columns, forms, session state, fragments, dialogs, "
                "data tables, charts, a sidebar and a custom theme — plus a little CSS/JS for the cursor-reactive background. "
                "Icons: Devicon & Phosphor. Theme inspired by the manga *Tomodachi Game*; no official art used."
            )
    st.write("")
    c1, _ = st.columns([1, 2])
    c1.button("Back to the start", icon=":material/replay:", on_click=jump, args=("prologue",), width="stretch")


# ─────────────────────────────────────────────────────────────────────────────
#  Router
# ─────────────────────────────────────────────────────────────────────────────
{
    "prologue": prologue,
    "story": story,
    "skills": skills,
    "projects": projects,
    "honors": honors,
    "contact": contact,
}[current]()

if len(ss.visited) == len(ROUNDS) and not ss.get("cleared"):
    ss.cleared = True
    st.toast("All six rounds explored — thanks for reading the whole file.", icon=":material/verified:")

st.html(
    f'<div class="x-foot"><div>© {date.today().year} <b>{NAME}</b> · {COURSE} · <b>{SECTION}</b></div>'
    f"<div>Built with Streamlit · Theme inspired by Tomodachi Game</div></div>"
)
