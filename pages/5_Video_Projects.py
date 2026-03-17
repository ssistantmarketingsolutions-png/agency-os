import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

st.set_page_config(page_title="Video Projects", page_icon="🎬", layout="wide")
st.title("🎬 Video Projects")
st.caption("Manage video production pipeline from raw footage to published")

tab_add, tab_pipeline = st.tabs(["Upload & Create", "Pipeline View"])

# ── Upload & Create ───────────────────────────────────────────────────────────

with tab_add:
    clients = db.get_clients(status_filter="Active")
    if not clients:
        st.warning("No active clients. Add clients first.")
    else:
        col_upload, col_form = st.columns([1, 1])

        with col_upload:
            st.subheader("Upload Raw File")
            uploaded_file = st.file_uploader(
                "Upload raw video file",
                type=["mp4", "mov", "avi", "mkv", "webm"],
                help="Supported formats: MP4, MOV, AVI, MKV, WebM",
            )

            saved_path = None
            if uploaded_file:
                save_path = os.path.join(UPLOADS_DIR, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_path = save_path
                st.success(f"Uploaded: **{uploaded_file.name}**")
                st.session_state["last_uploaded_file"] = save_path

        with col_form:
            st.subheader("Create Project")
            with st.form("add_video_project_form", clear_on_submit=True):
                client_options = {f"{c['name']} ({c.get('business_name', '')})": c["id"] for c in clients}
                client_label = st.selectbox("Client *", list(client_options.keys()))
                title = st.text_input("Project Title *")
                description = st.text_area("Description")
                editor_name = st.text_input("Editor Name")
                status = st.selectbox(
                    "Initial Status",
                    ["Raw Received", "In Edit", "Under Review", "Approved", "Published"],
                )
                due_date = st.date_input("Due Date", value=None)
                notes = st.text_area("Notes")

                # Use uploaded file path if available
                raw_file_path = st.session_state.get("last_uploaded_file", "")

                submitted = st.form_submit_button("Create Project", type="primary")

            if submitted:
                if not title:
                    st.error("Project title is required.")
                else:
                    db.add_video_project(
                        client_id=client_options[client_label],
                        title=title,
                        description=description,
                        editor_name=editor_name,
                        status=status,
                        raw_file_path=raw_file_path,
                        due_date=str(due_date) if due_date else None,
                        notes=notes,
                    )
                    st.success(f"Project **{title}** created!")
                    if "last_uploaded_file" in st.session_state:
                        del st.session_state["last_uploaded_file"]
                    st.rerun()

# ── Pipeline View ─────────────────────────────────────────────────────────────

with tab_pipeline:
    all_clients = db.get_clients()
    filter_options = ["All Clients"] + [f"{c['name']} ({c.get('business_name', '')})" for c in all_clients]
    filter_client_label = st.selectbox("Filter by Client", filter_options, key="video_filter_client")

    client_id_filter = None
    if filter_client_label != "All Clients":
        for c in all_clients:
            if f"{c['name']} ({c.get('business_name', '')})" == filter_client_label:
                client_id_filter = c["id"]
                break

    STATUSES = ["Raw Received", "In Edit", "Under Review", "Approved", "Published"]
    status_icons = {
        "Raw Received": "📥",
        "In Edit": "✏️",
        "Under Review": "👀",
        "Approved": "✅",
        "Published": "🚀",
    }

    # Kanban-style columns
    cols = st.columns(len(STATUSES))
    for col, status in zip(cols, STATUSES):
        projects = db.get_video_projects(client_id=client_id_filter, status_filter=status)
        icon = status_icons[status]
        col.markdown(f"**{icon} {status}** ({len(projects)})")
        col.divider()
        for proj in projects:
            with col.container():
                col.markdown(f"**{proj['title']}**")
                col.caption(f"{proj.get('client_name', '—')}")
                if proj.get("due_date"):
                    col.caption(f"Due: {proj['due_date']}")
                if proj.get("editor_name"):
                    col.caption(f"Editor: {proj['editor_name']}")
                col.divider()

    st.divider()
    st.subheader("Project Details")

    all_projects = db.get_video_projects(client_id=client_id_filter)
    if all_projects:
        for proj in all_projects:
            icon = status_icons.get(proj["status"], "📁")
            with st.expander(f"{icon} {proj['title']} — {proj.get('client_name', '')} · {proj['status']}"):
                c1, c2 = st.columns(2)
                c1.write(f"**Editor:** {proj.get('editor_name', '—')}")
                c1.write(f"**Due Date:** {proj.get('due_date', '—')}")
                c1.write(f"**Status:** {proj['status']}")
                c2.write(f"**Description:** {proj.get('description', '—')}")
                if proj.get("notes"):
                    st.write(f"**Notes:** {proj['notes']}")

                # File download
                raw_path = proj.get("raw_file_path")
                if raw_path and os.path.exists(raw_path):
                    with open(raw_path, "rb") as f:
                        file_bytes = f.read()
                    filename = os.path.basename(raw_path)
                    st.download_button(
                        label=f"⬇️ Download Raw File ({filename})",
                        data=file_bytes,
                        file_name=filename,
                        key=f"download_{proj['id']}",
                    )

                # Update form
                with st.form(f"update_video_{proj['id']}"):
                    new_status = st.selectbox(
                        "Update Status",
                        STATUSES,
                        index=STATUSES.index(proj["status"]),
                        key=f"vs_{proj['id']}",
                    )
                    new_notes = st.text_area("Review Notes", value=proj.get("notes", ""), key=f"vn_{proj['id']}")
                    new_editor = st.text_input("Editor Name", value=proj.get("editor_name", ""), key=f"ve_{proj['id']}")
                    if st.form_submit_button("Save Updates"):
                        db.update_video_project(
                            proj["id"],
                            status=new_status,
                            notes=new_notes,
                            editor_name=new_editor,
                        )
                        st.success("Project updated!")
                        st.rerun()
    else:
        st.info("No video projects found. Create one above.")
