"""Bounded in-process job queue with status persistence."""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from autoparts_core.config.settings import get_settings
from autoparts_core.db.models import ErrorEvent, JobQueueItem


def enqueue(session: Session, job_type: str, payload: dict, *, max_attempts: int = 3) -> JobQueueItem | None:
    settings = get_settings()
    queued = session.query(JobQueueItem).filter_by(status="queued").count()
    if queued >= settings.job_queue_max:
        session.add(
            ErrorEvent(
                category="VALIDATION_ERROR",
                message="Job queue full",
                detail=f"max={settings.job_queue_max}",
            )
        )
        return None
    item = JobQueueItem(
        job_type=job_type,
        payload_json=json.dumps(payload),
        status="queued",
        max_attempts=max_attempts,
    )
    session.add(item)
    session.flush()
    return item


def list_jobs(session: Session, limit: int = 100) -> list[JobQueueItem]:
    return session.query(JobQueueItem).order_by(JobQueueItem.created_at.desc()).limit(limit).all()


def cancel_job(session: Session, job_id: int) -> bool:
    item = session.get(JobQueueItem, job_id)
    if not item or item.status not in {"queued", "running"}:
        return False
    item.status = "cancelled"
    item.updated_at = datetime.utcnow()
    return True


def mark_failed(session: Session, item: JobQueueItem, category: str, message: str) -> None:
    item.attempts += 1
    item.last_error = message
    item.updated_at = datetime.utcnow()
    if item.attempts >= item.max_attempts:
        item.status = "failed"
    else:
        item.status = "queued"
    session.add(ErrorEvent(category=category, message=message, detail=f"job={item.id}"))
