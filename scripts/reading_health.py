"""Assess execution evidence; a partial report alone is not a live worker."""
from datetime import datetime, timedelta


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result if result.tzinfo is not None else None
    except ValueError:
        return None


def recent(value, now, minutes):
    point = timestamp(value)
    return point is not None and timedelta(0) <= now - point <= timedelta(minutes=minutes)


def reading_health(run, now):
    if now.tzinfo is None:
        raise ValueError("An explicit timezone is required")
    worker = run.get("reading_worker") or {}
    platform = run.get("platform_last_run") or {}
    worker_start = timestamp(worker.get("started_at"))
    failed_at = timestamp(platform.get("finished_at"))
    if (platform.get("status") in {"failed", "cancelled", "canceled"}
            and failed_at is not None and failed_at <= now
            and (worker_start is None or failed_at >= worker_start)):
        return "failed"
    platform_start = timestamp(platform.get("started_at"))
    if (platform.get("status") == "in_progress"
            and recent(platform.get("observed_at"), now, 5)
            and platform_start is not None and platform_start <= now
            and (worker_start is None or platform_start >= worker_start)):
        return "active_platform"
    if worker:
        heartbeat = timestamp(worker.get("heartbeat_at"))
        expiry = timestamp(worker.get("lease_expires_at"))
        if (worker.get("owner") and worker_start is not None and heartbeat is not None
                and worker_start <= heartbeat <= now and not worker.get("ended_at")
                and recent(worker.get("heartbeat_at"), now, 20)
                and expiry is not None and now < expiry <= heartbeat + timedelta(minutes=30)):
            return "active_worker"
        ended = timestamp(worker.get("ended_at"))
        resume = timestamp(run.get("next_resume_at"))
        if (worker.get("end_reason") == "checkpoint" and ended is not None
                and worker_start is not None and worker_start <= ended <= now
                and resume is not None and ended < resume
                and run.get("resume_schedule_verified") is True
                and -timedelta(minutes=10) <= resume - now <= timedelta(minutes=60)):
            return "awaiting_resume"
        return "stale"
    if recent(run.get("last_progress_at"), now, 20):
        return "recent_progress_unverified"
    return "stale"
