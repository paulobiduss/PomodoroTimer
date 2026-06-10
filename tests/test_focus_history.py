import unittest
from datetime import date

from core.focus_history import FocusHistory


class FakeStore:
    def __init__(self):
        self.values = {}

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value


class FocusHistoryTest(unittest.TestCase):
    def test_records_focus_minutes_for_today(self):
        store = FakeStore()
        history = FocusHistory(store, today_provider=lambda: date(2026, 5, 12))

        history.add_focus_minutes(25)
        history.add_focus_minutes(15)

        self.assertEqual(40, history.minutes_for(date(2026, 5, 12)))

    def test_compares_today_with_yesterday_using_direct_delta(self):
        store = FakeStore()
        history = FocusHistory(store, today_provider=lambda: date(2026, 5, 12))

        history.add_focus_minutes(30, date(2026, 5, 11))
        history.add_focus_minutes(55, date(2026, 5, 12))

        self.assertIn("Ontem: +25min", history.compact_summary_text())

    def test_compares_negative_delta_against_yesterday(self):
        store = FakeStore()
        history = FocusHistory(store, today_provider=lambda: date(2026, 5, 12))

        history.add_focus_minutes(90, date(2026, 5, 11))
        history.add_focus_minutes(45, date(2026, 5, 12))

        self.assertIn("Ontem: -45min", history.compact_summary_text())

    def test_compares_equal_days_with_neutral_text(self):
        store = FakeStore()
        history = FocusHistory(store, today_provider=lambda: date(2026, 5, 12))

        history.add_focus_minutes(25, date(2026, 5, 11))
        history.add_focus_minutes(25, date(2026, 5, 12))

        self.assertIn("Ontem: igual a ontem", history.compact_summary_text())

    def test_weekly_total_uses_monday_to_sunday_window(self):
        store = FakeStore()
        history = FocusHistory(store, today_provider=lambda: date(2026, 5, 13))

        history.add_focus_minutes(100, date(2026, 5, 10))
        history.add_focus_minutes(30, date(2026, 5, 11))
        history.add_focus_minutes(45, date(2026, 5, 13))
        history.add_focus_minutes(60, date(2026, 5, 17))
        history.add_focus_minutes(120, date(2026, 5, 18))

        self.assertEqual(135, history.weekly_minutes())

    def test_migrates_legacy_focus_today_only_once(self):
        store = FakeStore()
        store.setValue("history/focus_minutes_today", 50)
        history = FocusHistory(store, today_provider=lambda: date(2026, 5, 12))

        history.migrate_legacy_today()
        history.migrate_legacy_today()

        self.assertEqual(50, history.minutes_for(date(2026, 5, 12)))
        self.assertTrue(store.value("history/daily_migration_done"))


if __name__ == "__main__":
    unittest.main()
