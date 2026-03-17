import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db
import ai_engine

st.set_page_config(page_title="Proposal Builder", page_icon="📄", layout="wide")
st.title("📄 Proposal Builder")
st.caption("Generate professional, personalized proposals — powered by Claude AI")

col_build, col_saved = st.columns([1, 1])

# ── Build Proposal ────────────────────────────────────────────────────────────

with col_build:
    st.subheader("Build a Proposal")

    leads = db.get_leads()
    open_leads = [l for l in leads if l["status"] not in ("Closed Won", "Closed Lost")]

    if not open_leads:
        st.warning("No open leads found. Add leads in Clients & Leads first.")
    else:
        lead_options = {f"{l['name']} ({l.get('business_name', '')})": l for l in open_leads}
        selected_label = st.selectbox("Select Lead", list(lead_options.keys()))
        selected_lead = lead_options[selected_label]

        # Show lead details
        with st.container():
            st.caption(f"**Niche:** {selected_lead.get('niche', '—')} · **Source:** {selected_lead.get('source', '—')} · **Status:** {selected_lead.get('status', '—')}")
            if selected_lead.get("notes"):
                st.caption(f"**Notes:** {selected_lead['notes']}")

        service_tier = st.selectbox(
            "Service Package",
            ["Lead Gen Only", "Lead Gen + Appt Setting", "Full Partnership"],
            help="Lead Gen Only: Paid ads to drive inbound leads\nLead Gen + Appt Setting: Ads + we handle follow-up & booking\nFull Partnership: Organic content + ads + appt setting + strategy",
        )

        tier_descriptions = {
            "Lead Gen Only": "Paid ads (Meta/Google) driving inbound leads directly to you.",
            "Lead Gen + Appt Setting": "Paid ads + full follow-up and appointment booking handled for you.",
            "Full Partnership": "Complete marketing takeover: organic content, ads, appointment setting, and strategy.",
        }
        st.info(tier_descriptions[service_tier])

        if st.button("✨ Generate Proposal", type="primary"):
            st.divider()
            st.subheader("Your Proposal")

            full_text = ""

            def proposal_stream():
                return ai_engine.generate_proposal(
                    lead_info=selected_lead,
                    service_tier=service_tier,
                )

            try:
                full_text = st.write_stream(proposal_stream())
                st.session_state["last_generated_proposal"] = {
                    "text": full_text,
                    "lead_id": selected_lead["id"],
                    "lead_name": selected_lead["name"],
                }
            except Exception as e:
                st.error(f"Error generating proposal: {e}")

        if "last_generated_proposal" in st.session_state:
            saved = st.session_state["last_generated_proposal"]
            col_save, col_copy = st.columns(2)

            with col_save:
                if st.button("💾 Save as Draft"):
                    db.add_proposal(lead_id=saved["lead_id"], proposal_text=saved["text"], status="Draft")
                    st.success(f"Proposal saved for {saved['lead_name']}!")
                    del st.session_state["last_generated_proposal"]
                    st.rerun()

            with col_copy:
                st.text_area(
                    "Copy Proposal Text",
                    value=saved["text"],
                    height=200,
                    key="copy_proposal_area",
                    help="Select all and copy from here",
                )

# ── Saved Proposals ───────────────────────────────────────────────────────────

with col_saved:
    st.subheader("Saved Proposals")

    proposals = db.get_proposals()
    status_icons = {"Draft": "📝", "Sent": "📤", "Accepted": "✅", "Rejected": "❌"}

    if proposals:
        for prop in proposals:
            icon = status_icons.get(prop["status"], "📄")
            label = f"{icon} {prop.get('lead_name', 'Unknown')} · {prop['status']} · {prop['created_at'][:10]}"
            with st.expander(label):
                st.text_area(
                    "Proposal",
                    value=prop["proposal_text"],
                    height=200,
                    key=f"prop_text_{prop['id']}",
                    disabled=True,
                )
                new_status = st.selectbox(
                    "Update Status",
                    ["Draft", "Sent", "Accepted", "Rejected"],
                    index=["Draft", "Sent", "Accepted", "Rejected"].index(prop["status"]),
                    key=f"prop_status_{prop['id']}",
                )
                if st.button("Save Status", key=f"save_prop_{prop['id']}"):
                    db.update_proposal(prop["id"], status=new_status)
                    st.success("Updated!")
                    st.rerun()
    else:
        st.info("No proposals saved yet. Generate one to get started.")
