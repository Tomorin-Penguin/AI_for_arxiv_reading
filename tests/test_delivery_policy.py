import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from delivery_policy import delivery_action


class DeliveryPolicyTests(unittest.TestCase):
    def run_state(self, **changes):
        state = dict(report_date="2026-10-30", phase="reading",
                     announcement_status="confirmed_new", reading_started_at="2026-10-30T11:05:00+08:00",
                     report_ready=False, backlog_authorized=False)
        state.update(changes)
        return state

    def at(self, clock):
        return datetime.fromisoformat("2026-10-30T" + clock + ":00+08:00")

    def test_never_send_before_window_even_if_failed(self):
        self.assertEqual(delivery_action(None, self.at("13:59")), "wait_window")

    def test_missing_run_or_waiting_source_notifies_at_14(self):
        self.assertEqual(delivery_action(None, self.at("14:00")), "send_failure")
        state = self.run_state(phase="waiting_source", announcement_status="unverified", reading_started_at=None)
        self.assertEqual(delivery_action(state, self.at("14:00")), "send_failure")

    def test_explicit_execution_failure_is_not_normal_slow_reading(self):
        self.assertEqual(delivery_action(self.run_state(phase="blocked"), self.at("14:00")), "send_failure")
        self.assertEqual(delivery_action(self.run_state(), self.at("14:00")), "wait_reading")

    def test_verified_no_update_can_send_without_reading(self):
        state = self.run_state(phase="no_updates", announcement_status="confirmed_no_updates", reading_started_at=None)
        self.assertEqual(delivery_action(state, self.at("14:00")), "send_no_updates")

    def test_authorized_backlog_waits_despite_no_new_announcements(self):
        state = self.run_state(announcement_status="confirmed_no_updates", backlog_authorized=True)
        self.assertEqual(delivery_action(state, self.at("14:00")), "wait_reading")
        self.assertEqual(delivery_action(state, self.at("16:30")), "send_partial")

    def test_completion_is_not_enough_without_validated_report(self):
        state = self.run_state(phase="complete")
        self.assertEqual(delivery_action(state, self.at("15:15")), "wait_reading")
        state["report_ready"] = True
        self.assertEqual(delivery_action(state, self.at("15:15")), "send_digest")

    def test_last_checkpoint_sends_partial(self):
        self.assertEqual(delivery_action(self.run_state(), self.at("16:30")), "send_partial")

    def test_late_runs_do_not_silently_mail_outside_window(self):
        state = self.run_state(phase="complete", report_ready=True)
        self.assertEqual(delivery_action(state, self.at("16:31")), "missed_window")

    def test_successful_failure_notice_also_prevents_duplicates(self):
        for clock in ("14:00", "15:15", "16:30"):
            self.assertEqual(delivery_action(self.run_state(), self.at(clock), already_sent=True), "already_sent")

    def test_previous_report_is_not_current_execution(self):
        self.assertEqual(delivery_action(self.run_state(report_date="2026-10-29"), self.at("14:00")), "send_failure")

    def test_convert_timezone_and_require_explicit_zone(self):
        state = self.run_state(phase="complete", report_ready=True)
        self.assertEqual(delivery_action(state, datetime.fromisoformat("2026-10-30T07:15:00+00:00")), "send_digest")
        with self.assertRaises(ValueError):
            delivery_action(state, datetime(2026, 10, 30, 15, 15))

    def test_reject_truthy_strings_for_authorization(self):
        with self.assertRaises(ValueError):
            delivery_action(self.run_state(backlog_authorized="false"), self.at("14:00"))


if __name__ == "__main__":
    unittest.main()
