import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "agency_os.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            business_name TEXT,
            email TEXT,
            phone TEXT,
            niche TEXT,
            service_tier TEXT,
            monthly_retainer REAL,
            status TEXT DEFAULT 'Active',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            business_name TEXT,
            email TEXT,
            phone TEXT,
            niche TEXT,
            source TEXT,
            status TEXT DEFAULT 'New',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            platform TEXT,
            campaign_name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            budget REAL,
            spend REAL DEFAULT 0,
            leads_generated INTEGER DEFAULT 0,
            appointments_set INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS content_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            platform TEXT,
            content_type TEXT,
            content_text TEXT,
            status TEXT DEFAULT 'Draft',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS video_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            editor_name TEXT,
            status TEXT DEFAULT 'Raw Received',
            raw_file_path TEXT,
            output_file_path TEXT,
            due_date TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            proposal_text TEXT,
            status TEXT DEFAULT 'Draft',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)

    conn.commit()
    conn.close()


# ── Clients ──────────────────────────────────────────────────────────────────

def add_client(name, business_name, email, phone, niche, service_tier, monthly_retainer, status, notes):
    conn = get_connection()
    conn.execute(
        "INSERT INTO clients (name, business_name, email, phone, niche, service_tier, monthly_retainer, status, notes) VALUES (?,?,?,?,?,?,?,?,?)",
        (name, business_name, email, phone, niche, service_tier, monthly_retainer, status, notes),
    )
    conn.commit()
    conn.close()


def get_clients(status_filter=None):
    conn = get_connection()
    if status_filter:
        rows = conn.execute("SELECT * FROM clients WHERE status=? ORDER BY created_at DESC", (status_filter,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM clients ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_client(client_id, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [client_id]
    conn = get_connection()
    conn.execute(f"UPDATE clients SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()


# ── Leads ─────────────────────────────────────────────────────────────────────

def add_lead(name, business_name, email, phone, niche, source, status, notes):
    conn = get_connection()
    conn.execute(
        "INSERT INTO leads (name, business_name, email, phone, niche, source, status, notes) VALUES (?,?,?,?,?,?,?,?)",
        (name, business_name, email, phone, niche, source, status, notes),
    )
    conn.commit()
    conn.close()


def get_leads(status_filter=None):
    conn = get_connection()
    if status_filter:
        rows = conn.execute("SELECT * FROM leads WHERE status=? ORDER BY created_at DESC", (status_filter,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_lead(lead_id, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [lead_id]
    conn = get_connection()
    conn.execute(f"UPDATE leads SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()


# ── Campaigns ─────────────────────────────────────────────────────────────────

def add_campaign(client_id, platform, campaign_name, start_date, end_date, budget, spend, leads_generated, appointments_set, notes):
    conn = get_connection()
    conn.execute(
        "INSERT INTO campaigns (client_id, platform, campaign_name, start_date, end_date, budget, spend, leads_generated, appointments_set, notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (client_id, platform, campaign_name, start_date, end_date, budget, spend, leads_generated, appointments_set, notes),
    )
    conn.commit()
    conn.close()


def get_campaigns(client_id=None):
    conn = get_connection()
    if client_id:
        rows = conn.execute(
            "SELECT c.*, cl.name as client_name FROM campaigns c LEFT JOIN clients cl ON c.client_id=cl.id WHERE c.client_id=? ORDER BY c.created_at DESC",
            (client_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT c.*, cl.name as client_name FROM campaigns c LEFT JOIN clients cl ON c.client_id=cl.id ORDER BY c.created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_campaign(campaign_id, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [campaign_id]
    conn = get_connection()
    conn.execute(f"UPDATE campaigns SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()


# ── Content ───────────────────────────────────────────────────────────────────

def add_content_item(client_id, platform, content_type, content_text, status="Draft"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO content_items (client_id, platform, content_type, content_text, status) VALUES (?,?,?,?,?)",
        (client_id, platform, content_type, content_text, status),
    )
    conn.commit()
    conn.close()


def get_content_items(client_id=None):
    conn = get_connection()
    if client_id:
        rows = conn.execute(
            "SELECT ci.*, cl.name as client_name FROM content_items ci LEFT JOIN clients cl ON ci.client_id=cl.id WHERE ci.client_id=? ORDER BY ci.created_at DESC",
            (client_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT ci.*, cl.name as client_name FROM content_items ci LEFT JOIN clients cl ON ci.client_id=cl.id ORDER BY ci.created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_content_this_week():
    conn = get_connection()
    rows = conn.execute(
        "SELECT COUNT(*) as cnt FROM content_items WHERE created_at >= date('now', '-7 days')"
    ).fetchone()
    conn.close()
    return rows["cnt"] if rows else 0


def update_content_item(item_id, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [item_id]
    conn = get_connection()
    conn.execute(f"UPDATE content_items SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()


# ── Video Projects ────────────────────────────────────────────────────────────

def add_video_project(client_id, title, description, editor_name, status, raw_file_path, due_date, notes):
    conn = get_connection()
    conn.execute(
        "INSERT INTO video_projects (client_id, title, description, editor_name, status, raw_file_path, due_date, notes) VALUES (?,?,?,?,?,?,?,?)",
        (client_id, title, description, editor_name, status, raw_file_path, due_date, notes),
    )
    conn.commit()
    conn.close()


def get_video_projects(client_id=None, status_filter=None):
    conn = get_connection()
    base = "SELECT vp.*, cl.name as client_name FROM video_projects vp LEFT JOIN clients cl ON vp.client_id=cl.id"
    conditions, params = [], []
    if client_id:
        conditions.append("vp.client_id=?")
        params.append(client_id)
    if status_filter:
        conditions.append("vp.status=?")
        params.append(status_filter)
    if conditions:
        base += " WHERE " + " AND ".join(conditions)
    base += " ORDER BY vp.created_at DESC"
    rows = conn.execute(base, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_video_project(project_id, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [project_id]
    conn = get_connection()
    conn.execute(f"UPDATE video_projects SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()


# ── Proposals ─────────────────────────────────────────────────────────────────

def add_proposal(lead_id, proposal_text, status="Draft"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO proposals (lead_id, proposal_text, status) VALUES (?,?,?)",
        (lead_id, proposal_text, status),
    )
    conn.commit()
    conn.close()


def get_proposals(lead_id=None):
    conn = get_connection()
    if lead_id:
        rows = conn.execute(
            "SELECT p.*, l.name as lead_name FROM proposals p LEFT JOIN leads l ON p.lead_id=l.id WHERE p.lead_id=? ORDER BY p.created_at DESC",
            (lead_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT p.*, l.name as lead_name FROM proposals p LEFT JOIN leads l ON p.lead_id=l.id ORDER BY p.created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_proposal(proposal_id, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [proposal_id]
    conn = get_connection()
    conn.execute(f"UPDATE proposals SET {fields} WHERE id=?", values)
    conn.commit()
    conn.close()


# Initialise on import
init_db()
