import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from reading_health import reading_health
from delivery_policy import delivery_action


class ReadingHealthTests(unittest.TestCase):
    def at(self, clock):
        return datetime.fromisoformat("2026-10-29T" + clock + "+08:00")

    def recorded_stall(self):
        return dict(report_date="2026-10-29", phase="reading",
                    announcement_status="confirmed_no_updates", backlog_authorized=True,
                    report_ready=False, reading_started_at="2026-10-29T05:38:54Z",
                    last_progress_at="2026-10-29T05:47:43Z",
                    last_mail_check_at="2026-10-29T07:15:17Z")

    def failed_run(self):
        return dict(status="failed", run_id="f51b8b63-53f8-832a-8bb6-0c0cd8e8f26c",
                    started_at="2026-10-29T05:26:54.171Z",
                    finished_at="2026-10-29T05:51:57.261Z")

    def test_real_1515_incident_mail_check_does_not_refresh_reading(self):
        run = self.recorded_stall()
        self.assertEqual(reading_health(run, self.at("15:15:17")), "stale")
        self.assertEqual(delivery_action(run, self.at("15:15:17")), "send_failure")

    def test_platform_failure_overrides_recent_commit_at_14(self):
        run = self.recorded_stall()
        run["platform_last_run"] = self.failed_run()
        self.assertEqual(reading_health(run, self.at("14:00:55")), "failed")
        self.assertEqual(delivery_action(run, self.at("14:00:55")), "send_failure")

    def test_recovery_worker_supersedes_old_failure(self):
        run = self.recorded_stall()
        run["platform_last_run"] = self.failed_run()
        run["reading_worker"] = dict(owner="recovery", started_at="2026-10-29T15:25:00+08:00",
                                     heartbeat_at="2026-10-29T15:30:00+08:00",
                                     lease_expires_at="2026-10-29T16:00:00+08:00")
        self.assertEqual(reading_health(run, self.at("15:35:00")), "active_worker")

    def test_expired_lease_cannot_claim_active_even_with_new_mail_event(self):
        run = self.recorded_stall()
        run["reading_worker"] = dict(owner="old", started_at="2026-10-29T13:00:00+08:00",
                                     heartbeat_at="2026-10-29T13:47:43+08:00",
                                     lease_expires_at="2026-10-29T14:10:00+08:00")
        self.assertEqual(reading_health(run, self.at("15:15:00")), "stale")

    def test_recent_platform_observation_not_stored_running_label(self):
        run = self.recorded_stall()
        run["platform_last_run"] = dict(status="in_progress", started_at="2026-10-29T13:00:00+08:00",
                                        observed_at="2026-10-29T15:14:00+08:00")
        self.assertEqual(reading_health(run, self.at("15:15:00")), "active_platform")
        self.assertEqual(reading_health(run, self.at("15:25:00")), "stale")

    def test_checkpoint_wait_requires_real_upcoming_schedule(self):
        run = self.recorded_stall()
        run["reading_worker"] = dict(owner="batch", started_at="2026-10-29T13:00:00+08:00",
                                     ended_at="2026-10-29T13:20:00+08:00", end_reason="checkpoint")
        run.update(next_resume_at="2026-10-29T14:00:00+08:00", resume_schedule_verified=True)
        self.assertEqual(reading_health(run, self.at("14:00:00")), "awaiting_resume")
        self.assertEqual(reading_health(run, self.at("14:11:00")), "stale")

    def test_future_or_naive_progress_is_not_liveness(self):
        for stamp in ("2026-10-29T16:00:00+08:00", "2026-10-29T15:14:00", "not-a-time"):
            run = self.recorded_stall()
            run["last_progress_at"] = stamp
            self.assertEqual(reading_health(run, self.at("15:15:00")), "stale")

    def test_unfinished_stalled_reading_still_yields_partial_at_deadline(self):
        self.assertEqual(delivery_action(self.recorded_stall(), self.at("16:30:00")), "send_partial")


if __name__ == "__main__":
    unittest.main()
