import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db
import ai_engine

st.set_page_config(page_title="Content Generator", page_icon="✍️", layout="wide")
st.title("✍️ Content Generator")
st.caption("AI-powered content creation — captions, scripts, hooks, and stories")

col_gen, col_saved = st.columns([1, 1])

# ── Generate ──────────────────────────────────────────────────────────────────

with col_gen:
    st.subheader("Generate Content")

    clients = db.get_clients(status_filter="Active")
    client_options = {f"{c['name']} ({c.get('business_name', '')})": c for c in clients}

    if not clients:
        st.warning("No active clients found. Add a client first.")
    else:
        selected_label = st.selectbox("Select Client", list(client_options.keys()))
        selected_client = client_options[selected_label]

        platform = st.selectbox("Platform", ["Instagram", "Facebook", "TikTok"])
        content_type = st.selectbox("Content Type", ["Caption", "Script", "Reel Hook", "Story"])
        brief = st.text_area(
            "Brief / Talking Points (optional)",
            placeholder="E.g. New membership promo, 20% off for the first month, targeting busy professionals...",
            height=120,
        )

        if st.button("✨ Generate Content", type="primary"):
            st.divider()
            st.subheader("Generated Content")

            output_placeholder = st.empty()
            full_text = ""

            def stream_gen():
                return ai_engine.generate_content(
                    client_name=selected_client["name"],
                    niche=selected_client.get("niche", ""),
                    platform=platform,
                    content_type=content_type,
                    brief=brief,
                )

            try:
                full_text = st.write_stream(stream_gen())
                st.session_state["last_generated_content"] = {
                    "text": full_text,
                    "client_id": selected_client["id"],
                    "platform": platform,
                    "content_type": content_type,
                }
            except Exception as e:
                st.error(f"Error generating content: {e}")

        # Save button (shown after generation)
        if "last_generated_content" in st.session_state:
            saved = st.session_state["last_generated_content"]
            if st.button("💾 Save as Draft"):
                db.add_content_item(
                    client_id=saved["client_id"],
                    platform=saved["platform"],
                    content_type=saved["content_type"],
                    content_text=saved["text"],
                    status="Draft",
                )
                st.success("Saved to Content Library as Draft!")
                del st.session_state["last_generated_content"]
                st.rerun()

# ── Saved Content ─────────────────────────────────────────────────────────────

with col_saved:
    st.subheader("Content Library")

    all_clients = db.get_clients()
    filter_options = ["All Clients"] + [f"{c['name']} ({c.get('business_name', '')})" for c in all_clients]
    filter_client = st.selectbox("Filter by Client", filter_options, key="content_filter_client")

    client_id_filter = None
    if filter_client != "All Clients":
        for c in all_clients:
            if f"{c['name']} ({c.get('business_name', '')})" == filter_client:
                client_id_filter = c["id"]
                break

    content_items = db.get_content_items(client_id=client_id_filter)

    status_icons = {"Draft": "📝", "Approved": "✅", "Published": "🚀"}

    if content_items:
        for item in content_items:
            icon = status_icons.get(item["status"], "📄")
            label = f"{icon} {item['content_type']} · {item['platform']} · {item.get('client_name', '')} · {item['created_at'][:10]}"
            with st.expander(label):
                st.text_area("Content", value=item["content_text"], height=150, key=f"content_text_{item['id']}", disabled=True)
                new_status = st.selectbox(
                    "Status",
                    ["Draft", "Approved", "Published"],
                    index=["Draft", "Approved", "Published"].index(item["status"]),
                    key=f"content_status_{item['id']}",
                )
                if st.button("Update Status", key=f"update_content_{item['id']}"):
                    db.update_content_item(item["id"], status=new_status)
                    st.success("Status updated!")
                    st.rerun()
    else:
        st.info("No content saved yet. Generate and save content above.")
