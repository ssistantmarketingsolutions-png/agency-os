import streamlit as st
import database as db

st.set_page_config(
    page_title="Agency OS",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚀 Agency OS")
st.caption("Your marketing agency operating system — powered by Claude AI")

st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────

clients = db.get_clients(status_filter="Active")
leads = db.get_leads()
open_leads = [l for l in leads if l["status"] not in ("Closed Won", "Closed Lost")]
content_this_week = db.get_content_this_week()
campaigns = db.get_campaigns()
active_campaigns = [c for c in campaigns if not c.get("end_date") or c["end_date"] >= "2024-01-01"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Active Clients", len(clients))
with col2:
    st.metric("Open Leads", len(open_leads))
with col3:
    st.metric("Content This Week", content_this_week)
with col4:
    st.metric("Active Campaigns", len(active_campaigns))

st.divider()

# ── Recent Leads ──────────────────────────────────────────────────────────────

col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("Recent Leads")
    recent_leads = leads[:10]
    if recent_leads:
        status_colors = {
            "New": "🟡",
            "Contacted": "🔵",
            "Proposal Sent": "🟠",
            "Closed Won": "🟢",
            "Closed Lost": "🔴",
        }
        for lead in recent_leads:
            badge = status_colors.get(lead["status"], "⚪")
            with st.container():
                c1, c2, c3 = st.columns([3, 2, 2])
                c1.write(f"**{lead['name']}** — {lead.get('business_name', '')}")
                c2.write(lead.get("niche", "—"))
                c3.write(f"{badge} {lead['status']}")
    else:
        st.info("No leads yet. Add your first lead in Clients & Leads.")

# ── Video Projects Needing Attention ──────────────────────────────────────────

with col_right:
    st.subheader("Video Projects — Action Needed")
    attention_statuses = ["In Edit", "Under Review"]
    attention_projects = []
    for s in attention_statuses:
        attention_projects.extend(db.get_video_projects(status_filter=s))

    if attention_projects:
        for proj in attention_projects:
            status_icon = "✏️" if proj["status"] == "In Edit" else "👀"
            due = proj.get("due_date") or "No due date"
            with st.container():
                st.write(f"{status_icon} **{proj['title']}**")
                st.caption(f"{proj.get('client_name', 'Unknown client')} · Due: {due} · {proj['status']}")
                st.divider()
    else:
        st.info("No video projects need attention right now.")

# ── Quick Nav ─────────────────────────────────────────────────────────────────

st.divider()
st.subheader("Quick Navigation")
nav_cols = st.columns(5)
pages = [
    ("👥", "Clients & Leads", "pages/1_Clients_&_Leads.py"),
    ("✍️", "Content Generator", "pages/2_Content_Generator.py"),
    ("📄", "Proposal Builder", "pages/3_Proposal_Builder.py"),
    ("📊", "Campaign Tracker", "pages/4_Campaign_Tracker.py"),
    ("🎬", "Video Projects", "pages/5_Video_Projects.py"),
]
for col, (icon, label, _) in zip(nav_cols, pages):
    col.info(f"{icon} **{label}**")
