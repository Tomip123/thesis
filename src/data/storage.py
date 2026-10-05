import json
import os
import sqlite3

import pandas as pd
import streamlit as st

DB_PATH = "reviews.db"

HUMAN_VERIFIER = "human"


def _add_verification_columns(cursor, table):
    existing = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
    if "verified_by" not in existing:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN verified_by TEXT")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS compliance_objectives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            criteria_json TEXT, -- JSON list
            source_ref TEXT,
            regulation TEXT DEFAULT 'EU Data Act',
            verified_by TEXT,      -- who reviewed this objective; 'human' = confirmed in the app
            UNIQUE(title, source_ref, regulation)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS objective_results (
            provider TEXT,
            objective_id INTEGER,
            score INTEGER, -- Coverage score 0-100
            met_criteria_json TEXT, -- JSON list of criteria that were met
            explanation TEXT,
            quotes TEXT,
            regulation TEXT DEFAULT 'EU Data Act',
            verified_by TEXT,      -- who confirmed this row; 'human' = verified in the Review screen
            PRIMARY KEY (provider, objective_id)
        )
    ''')

    _add_verification_columns(c, "compliance_objectives")
    _add_verification_columns(c, "objective_results")

    conn.commit()
    conn.close()


def save_objectives(objectives_list, verified_by=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        for objective in objectives_list:
            fields = (
                objective['title'], objective['description'], json.dumps(objective['criteria']),
                objective['source_ref'], objective.get('regulation', 'EU Data Act'), verified_by,
            )
            if objective.get('id'):
                conn.execute("""
                    UPDATE compliance_objectives
                       SET title = ?, description = ?, criteria_json = ?, source_ref = ?,
                           regulation = ?, verified_by = ?
                     WHERE id = ?
                """, fields + (objective['id'],))
            else:
                conn.execute("""
                    INSERT INTO compliance_objectives
                        (title, description, criteria_json, source_ref, regulation, verified_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(title, source_ref, regulation) DO UPDATE SET
                        description = excluded.description,
                        criteria_json = excluded.criteria_json,
                        verified_by = excluded.verified_by
                """, fields)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Failed to save objectives: {e}")
        return False


def load_objectives(regulation=None):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        if regulation:
            df = pd.read_sql_query(
                "SELECT * FROM compliance_objectives WHERE regulation = ?", conn, params=(regulation,)
            )
        else:
            df = pd.read_sql_query("SELECT * FROM compliance_objectives", conn)
        conn.close()

        if not df.empty and 'criteria_json' in df.columns:
            df['criteria'] = df['criteria_json'].apply(lambda x: json.loads(x) if x else [])
        return df
    except Exception as e:
        st.error(f"Failed to load objectives: {e}")
        return pd.DataFrame()


def save_objective_result(provider, objective_id, result, verified_by=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT OR REPLACE INTO objective_results
                (provider, objective_id, score, met_criteria_json, explanation, quotes, regulation,
                 verified_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            provider, objective_id, result.get('score', 0),
            json.dumps(result.get('met_criteria', [])),
            result.get('explanation', ''),
            json.dumps(result.get('quotes', [])),
            result.get('regulation', 'EU Data Act'),
            verified_by,
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving objective result: {e}")


def verification_counts(regulation=None, table="objective_results"):
    query = f"SELECT COUNT(verified_by), COUNT(*) FROM {table}"
    try:
        conn = sqlite3.connect(DB_PATH)
        if regulation:
            row = conn.execute(query + " WHERE regulation = ?", (regulation,)).fetchone()
        else:
            row = conn.execute(query).fetchone()
        conn.close()
        return row[0], row[1]
    except Exception:
        return 0, 0
