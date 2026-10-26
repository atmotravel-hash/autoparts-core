from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.db.models import ErrorEvent, SearchRunHistory
from autoparts_core.db.session import get_session
from autoparts_core.jobs.queue import enqueue, list_jobs

st.set_page_config(page_title="Jobs and Logs", layout="wide")
ensure_app_ready()
page_header("Jobs and Logs", "Structured errors · search history · bounded queue")

if st.button("Enqueue demo revalidation job"):
    with get_session() as session:
        item = enqueue(session, "revalidate_stale", {"limit": 10})
        st.write(f"Queued job id={item.id if item else None}")

with get_session() as session:
    st.subheader("Job queue")
    jobs = list_jobs(session)
    st.dataframe(
        [
            {
                "id": j.id,
                "type": j.job_type,
                "status": j.status,
                "attempts": j.attempts,
                "error": j.last_error,
                "created": j.created_at.isoformat() if j.created_at else None,
            }
            for j in jobs
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.subheader("Search history")
    hist = session.query(SearchRunHistory).order_by(SearchRunHistory.created_at.desc()).limit(50).all()
    st.dataframe(
        [
            {
                "when": h.created_at.isoformat() if h.created_at else None,
                "workflow": h.workflow,
                "label": h.label,
                "results": h.result_count,
            }
            for h in hist
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.subheader("Error events")
    errs = session.query(ErrorEvent).order_by(ErrorEvent.created_at.desc()).limit(50).all()
    st.dataframe(
        [
            {
                "when": e.created_at.isoformat() if e.created_at else None,
                "category": e.category,
                "source": e.source_id,
                "message": e.message,
            }
            for e in errs
        ],
        use_container_width=True,
        hide_index=True,
    )
