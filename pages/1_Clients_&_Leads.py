import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db

st.set_page_config(page_title="Clients & Leads", page_icon="👥", layout="wide")
st.title("👥 Clients & Leads")

tab_clients, tab_leads = st.tabs(["Clients", "Leads"])

# ══════════════════════════════════════════════════════════════════════════════
# CLIENTS
# ══════════════════════════════════════════════════════════════════════════════

with tab_clients:
    col_form, col_list = st.columns([1, 2])

    with col_form:
        st.subheader("Add Client")
        with st.form("add_client_form", clear_on_submit=True):
            name = st.text_input("Contact Name *")
            business_name = st.text_input("Business Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            niche = st.selectbox("Niche", ["Gym / Fitness", "Service Business", "Professional Services", "E-commerce", "Other"])
            service_tier = st.selectbox("Service Tier", ["Lead Gen Only", "Lead Gen + Appt Setting", "Full Partnership"])
            monthly_retainer = st.number_input("Monthly Retainer ($)", min_value=0.0, step=100.0)
            status = st.selectbox("Status", ["Active", "Paused", "Churned"])
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Add Client", type="primary")

        if submitted:
            if not name:
                st.error("Contact name is required.")
            else:
                db.add_client(name, business_name, email, phone, niche, service_tier, monthly_retainer, status, notes)
                st.success(f"Client **{name}** added!")
                st.rerun()

    with col_list:
        st.subheader("Client Roster")
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Paused", "Churned"], key="client_status_filter")
        clients = db.get_clients(status_filter=None if status_filter == "All" else status_filter)

        if clients:
            status_badge = {"Active": "🟢", "Paused": "🟡", "Churned": "🔴"}
            for client in clients:
                badge = status_badge.get(client["status"], "⚪")
                with st.expander(f"{badge} {client['name']} — {client.get('business_name', '')}"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Niche:** {client.get('niche', '—')}")
                    c1.write(f"**Service Tier:** {client.get('service_tier', '—')}")
                    c1.write(f"**Retainer:** ${client.get('monthly_retainer', 0):,.0f}/mo")
                    c2.write(f"**Email:** {client.get('email', '—')}")
                    c2.write(f"**Phone:** {client.get('phone', '—')}")
                    c2.write(f"**Status:** {badge} {client['status']}")
                    if client.get("notes"):
                        st.write(f"**Notes:** {client['notes']}")

                    # Inline status update
                    new_status = st.selectbox(
                        "Update Status",
                        ["Active", "Paused", "Churned"],
                        index=["Active", "Paused", "Churned"].index(client["status"]),
                        key=f"client_status_{client['id']}",
                    )
                    if st.button("Save Status", key=f"save_client_{client['id']}"):
                        db.update_client(client["id"], status=new_status)
                        st.success("Updated!")
                        st.rerun()
        else:
            st.info("No clients found. Add your first client.")

        # Store selected client in session state for cross-page use
        if clients:
            client_names = [f"{c['name']} ({c.get('business_name', '')})" for c in clients]
            selected = st.selectbox("Set Active Client (for AI tools)", ["— none —"] + client_names, key="active_client_selector")
            if selected != "— none —":
                idx = client_names.index(selected)
                st.session_state["active_client"] = clients[idx]
                st.success(f"Active client set: **{clients[idx]['name']}**")


# ══════════════════════════════════════════════════════════════════════════════
# LEADS
# ══════════════════════════════════════════════════════════════════════════════

with tab_leads:
    col_form2, col_list2 = st.columns([1, 2])

    with col_form2:
        st.subheader("Add Lead")
        with st.form("add_lead_form", clear_on_submit=True):
            l_name = st.text_input("Contact Name *")
            l_business = st.text_input("Business Name")
            l_email = st.text_input("Email")
            l_phone = st.text_input("Phone")
            l_niche = st.selectbox("Niche", ["Gym / Fitness", "Service Business", "Professional Services", "E-commerce", "Other"], key="lead_niche")
            l_source = st.selectbox("Source", ["Instagram DM", "Facebook", "Referral", "Cold Outreach", "Website", "TikTok", "Other"])
            l_status = st.selectbox("Status", ["New", "Contacted", "Proposal Sent", "Closed Won", "Closed Lost"])
            l_notes = st.text_area("Notes", key="lead_notes")
            l_submitted = st.form_submit_button("Add Lead", type="primary")

        if l_submitted:
            if not l_name:
                st.error("Contact name is required.")
            else:
                db.add_lead(l_name, l_business, l_email, l_phone, l_niche, l_source, l_status, l_notes)
                st.success(f"Lead **{l_name}** added!")
                st.rerun()

    with col_list2:
        st.subheader("Lead Pipeline")
        lead_status_filter = st.selectbox(
            "Filter by Status",
            ["All", "New", "Contacted", "Proposal Sent", "Closed Won", "Closed Lost"],
            key="lead_status_filter",
        )
        leads = db.get_leads(status_filter=None if lead_status_filter == "All" else lead_status_filter)

        status_colors = {
            "New": "🟡",
            "Contacted": "🔵",
            "Proposal Sent": "🟠",
            "Closed Won": "🟢",
            "Closed Lost": "🔴",
        }

        if leads:
            for lead in leads:
                badge = status_colors.get(lead["status"], "⚪")
                with st.expander(f"{badge} {lead['name']} — {lead.get('business_name', '')}"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Niche:** {lead.get('niche', '—')}")
                    c1.write(f"**Source:** {lead.get('source', '—')}")
                    c1.write(f"**Status:** {badge} {lead['status']}")
                    c2.write(f"**Email:** {lead.get('email', '—')}")
                    c2.write(f"**Phone:** {lead.get('phone', '—')}")
                    if lead.get("notes"):
                        st.write(f"**Notes:** {lead['notes']}")

                    new_status = st.selectbox(
                        "Update Status",
                        ["New", "Contacted", "Proposal Sent", "Closed Won", "Closed Lost"],
                        index=["New", "Contacted", "Proposal Sent", "Closed Won", "Closed Lost"].index(lead["status"]),
                        key=f"lead_status_{lead['id']}",
                    )
                    new_notes = st.text_area("Update Notes", value=lead.get("notes", ""), key=f"lead_notes_{lead['id']}")
                    if st.button("Save", key=f"save_lead_{lead['id']}"):
                        db.update_lead(lead["id"], status=new_status, notes=new_notes)
                        st.success("Updated!")
                        st.rerun()
        else:
            st.info("No leads found. Add your first lead.")
