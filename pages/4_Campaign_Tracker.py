import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db
import ai_engine

st.set_page_config(page_title="Campaign Tracker", page_icon="📊", layout="wide")
st.title("📊 Campaign Tracker")
st.caption("Track ad performance across Meta and Google — with AI-powered analysis")

tab_add, tab_view = st.tabs(["Add Campaign", "View & Analyze"])

# ── Add Campaign ──────────────────────────────────────────────────────────────

with tab_add:
    clients = db.get_clients(status_filter="Active")
    if not clients:
        st.warning("No active clients. Add clients first.")
    else:
        with st.form("add_campaign_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                client_options = {f"{c['name']} ({c.get('business_name', '')})": c["id"] for c in clients}
                client_label = st.selectbox("Client *", list(client_options.keys()))
                campaign_name = st.text_input("Campaign Name *")
                platform = st.selectbox("Platform", ["Meta", "Google"])
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date (optional)", value=None)

            with col2:
                budget = st.number_input("Budget ($)", min_value=0.0, step=50.0)
                spend = st.number_input("Current Spend ($)", min_value=0.0, step=10.0)
                leads_generated = st.number_input("Leads Generated", min_value=0, step=1)
                appointments_set = st.number_input("Appointments Set", min_value=0, step=1)
                notes = st.text_area("Notes")

            submitted = st.form_submit_button("Add Campaign", type="primary")

        if submitted:
            if not campaign_name:
                st.error("Campaign name is required.")
            else:
                db.add_campaign(
                    client_id=client_options[client_label],
                    platform=platform,
                    campaign_name=campaign_name,
                    start_date=str(start_date),
                    end_date=str(end_date) if end_date else None,
                    budget=budget,
                    spend=spend,
                    leads_generated=leads_generated,
                    appointments_set=appointments_set,
                    notes=notes,
                )
                st.success(f"Campaign **{campaign_name}** added!")
                st.rerun()

# ── View & Analyze ────────────────────────────────────────────────────────────

with tab_view:
    all_clients = db.get_clients()
    filter_options = ["All Clients"] + [f"{c['name']} ({c.get('business_name', '')})" for c in all_clients]
    filter_client_label = st.selectbox("Filter by Client", filter_options, key="campaign_filter")

    platform_filter = st.selectbox("Filter by Platform", ["All", "Meta", "Google"], key="platform_filter")

    client_id_filter = None
    if filter_client_label != "All Clients":
        for c in all_clients:
            if f"{c['name']} ({c.get('business_name', '')})" == filter_client_label:
                client_id_filter = c["id"]
                break

    campaigns = db.get_campaigns(client_id=client_id_filter)
    if platform_filter != "All":
        campaigns = [c for c in campaigns if c["platform"] == platform_filter]

    if not campaigns:
        st.info("No campaigns found. Add your first campaign above.")
    else:
        for campaign in campaigns:
            spend = campaign.get("spend", 0) or 0
            leads = campaign.get("leads_generated", 0) or 0
            appts = campaign.get("appointments_set", 0) or 0

            cpl = spend / leads if leads > 0 else None
            cost_per_appt = spend / appts if appts > 0 else None
            budget = campaign.get("budget", 0) or 0
            budget_used_pct = (spend / budget * 100) if budget > 0 else None

            platform_icon = "📘" if campaign["platform"] == "Meta" else "🔍"
            with st.expander(f"{platform_icon} {campaign['campaign_name']} — {campaign.get('client_name', '')}"):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Budget", f"${budget:,.0f}")
                m1.metric("Spend", f"${spend:,.0f}")
                m2.metric("Leads", leads)
                m2.metric("Appointments", appts)
                m3.metric("CPL", f"${cpl:,.2f}" if cpl else "N/A")
                m3.metric("Cost/Appt", f"${cost_per_appt:,.2f}" if cost_per_appt else "N/A")
                m4.metric("Budget Used", f"{budget_used_pct:.1f}%" if budget_used_pct is not None else "N/A")
                m4.metric("Platform", campaign["platform"])

                st.caption(f"Dates: {campaign.get('start_date', '—')} → {campaign.get('end_date', 'Ongoing')}")
                if campaign.get("notes"):
                    st.write(f"**Notes:** {campaign['notes']}")

                # Inline update form
                with st.form(f"update_campaign_{campaign['id']}"):
                    uc1, uc2, uc3 = st.columns(3)
                    new_spend = uc1.number_input("Update Spend ($)", value=float(spend), step=10.0, key=f"us_{campaign['id']}")
                    new_leads = uc2.number_input("Update Leads", value=int(leads), step=1, key=f"ul_{campaign['id']}")
                    new_appts = uc3.number_input("Update Appointments", value=int(appts), step=1, key=f"ua_{campaign['id']}")
                    new_notes = st.text_area("Update Notes", value=campaign.get("notes", ""), key=f"un_{campaign['id']}")
                    if st.form_submit_button("Save Updates"):
                        db.update_campaign(
                            campaign["id"],
                            spend=new_spend,
                            leads_generated=new_leads,
                            appointments_set=new_appts,
                            notes=new_notes,
                        )
                        st.success("Campaign updated!")
                        st.rerun()

                # AI Analysis
                if st.button("🤖 AI Analysis", key=f"ai_analysis_{campaign['id']}"):
                    with st.spinner("Analyzing with Claude..."):
                        try:
                            analysis = ai_engine.analyze_campaign(dict(campaign))
                            st.markdown("---")
                            st.markdown("**AI Campaign Analysis**")
                            st.markdown(analysis)
                        except Exception as e:
                            st.error(f"Analysis error: {e}")
