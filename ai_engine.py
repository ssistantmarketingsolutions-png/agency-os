import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set. Add it to your .env file.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


BRAND_VOICE = """
You are the AI assistant for A.K.'s marketing agency. A.K. runs a lead generation and appointment setting agency,
specializing in gyms and service-based businesses.

Brand voice: Polite, welcoming, and professional — but conversational, like talking to a friend.
Not pushy. Genuine. The goal is for people to feel taken care of, not sold to.
Always write in a way that reflects care, expertise, and a true marketing partnership mindset.
"""


def generate_content(client_name: str, niche: str, platform: str, content_type: str, brief: str = ""):
    """
    Stream AI-generated social media content.
    Yields text chunks for use with st.write_stream().
    """
    platform_guidance = {
        "Instagram": "Write for Instagram. Use engaging hooks, emojis where appropriate, and relevant hashtags at the end.",
        "Facebook": "Write for Facebook. More conversational, slightly longer form is fine. Community-oriented tone.",
        "TikTok": "Write for TikTok. High energy, trend-aware, punchy. Short sentences. Hook in the first line.",
    }

    type_guidance = {
        "Caption": "Write a social media caption.",
        "Script": "Write a short-form video script with clear sections: Hook, Body, CTA.",
        "Reel Hook": "Write 5 attention-grabbing first-line hooks for a Reel or short video. One per line.",
        "Story": "Write engaging Instagram/Facebook Story copy — short, punchy, with a clear CTA or poll idea.",
    }

    system = f"{BRAND_VOICE}\n\n{platform_guidance.get(platform, '')}\n{type_guidance.get(content_type, '')}"

    user_message = f"Client: {client_name}\nNiche: {niche}\nPlatform: {platform}\nContent Type: {content_type}"
    if brief:
        user_message += f"\n\nBrief / Talking Points:\n{brief}"
    user_message += "\n\nGenerate the content now."

    client = _get_client()
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def generate_proposal(lead_info: dict, service_tier: str):
    """
    Stream a full professional proposal for a lead.
    Yields text chunks for use with st.write_stream().
    """
    tier_descriptions = {
        "Lead Gen Only": "Lead generation via Meta and/or Google Ads — driving inbound leads directly to the client.",
        "Lead Gen + Appt Setting": "Full lead generation via paid ads PLUS appointment setting — we handle the follow-up and booking so the client only shows up to calls.",
        "Full Partnership": "Complete marketing partnership: organic content, paid ads (Meta + Google), appointment setting, and ongoing strategy. We own the marketing so the client can focus on their business.",
    }

    system = f"""{BRAND_VOICE}

You are writing a professional marketing proposal. The proposal should:
- Open with a warm, personalized introduction
- Clearly articulate the client's problem/opportunity
- Present the proposed solution with the selected service tier
- Include what's included, expected outcomes, and investment
- Close with confidence and a clear next step
- Be formatted cleanly with headers and bullet points
- Sound like it came from a trusted marketing partner, not a generic agency"""

    user_message = f"""Write a full proposal for this lead:

Name: {lead_info.get('name', 'N/A')}
Business: {lead_info.get('business_name', 'N/A')}
Niche: {lead_info.get('niche', 'N/A')}
Source: {lead_info.get('source', 'N/A')}
Notes: {lead_info.get('notes', 'N/A')}

Selected Service Tier: {service_tier}
Tier Description: {tier_descriptions.get(service_tier, service_tier)}

Generate a complete, professional proposal ready to send."""

    client = _get_client()
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "enabled", "budget_tokens": 5000},
        system=system,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for event in stream:
            if hasattr(event, "type"):
                if event.type == "content_block_delta":
                    delta = event.delta
                    if hasattr(delta, "type") and delta.type == "text_delta":
                        yield delta.text


def analyze_campaign(campaign_data: dict) -> str:
    """
    Returns a structured AI analysis of campaign performance.
    Not streamed — returns full string.
    """
    cpl = None
    cost_per_appt = None
    if campaign_data.get("leads_generated", 0) > 0 and campaign_data.get("spend", 0) > 0:
        cpl = campaign_data["spend"] / campaign_data["leads_generated"]
    if campaign_data.get("appointments_set", 0) > 0 and campaign_data.get("spend", 0) > 0:
        cost_per_appt = campaign_data["spend"] / campaign_data["appointments_set"]

    metrics_summary = f"""
Campaign: {campaign_data.get('campaign_name')}
Platform: {campaign_data.get('platform')}
Budget: ${campaign_data.get('budget', 0):,.2f}
Spend: ${campaign_data.get('spend', 0):,.2f}
Leads Generated: {campaign_data.get('leads_generated', 0)}
Appointments Set: {campaign_data.get('appointments_set', 0)}
Cost Per Lead (CPL): {'${:.2f}'.format(cpl) if cpl else 'N/A'}
Cost Per Appointment: {'${:.2f}'.format(cost_per_appt) if cost_per_appt else 'N/A'}
Notes: {campaign_data.get('notes', 'None')}
"""

    system = f"""{BRAND_VOICE}

You are a media buying analyst. Given campaign performance data, provide:
1. **Performance Summary** — how the campaign is performing overall
2. **What's Working** — specific positives to double down on
3. **What to Improve** — specific issues or underperformances
4. **Budget Recommendations** — should budget increase, decrease, or reallocate?
5. **Next Steps** — 2-3 actionable recommendations

Be specific, data-driven, and practical. Keep it concise."""

    client = _get_client()
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": f"Analyze this campaign:\n{metrics_summary}"}],
    )
    return message.content[0].text
