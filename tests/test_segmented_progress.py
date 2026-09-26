import unittest

from ui.components.segmented_progress import (
    SEGMENT_CURRENT,
    SEGMENT_DONE,
    SEGMENT_PENDING,
    segment_states,
)


class SegmentStatesTest(unittest.TestCase):
    def test_marks_done_current_and_pending(self):
        self.assertEqual(
            [SEGMENT_DONE, SEGMENT_CURRENT, SEGMENT_PENDING],
            segment_states(3, 1),
        )

    def test_first_block_is_current_at_plan_start(self):
        self.assertEqual([SEGMENT_CURRENT, SEGMENT_PENDING], segment_states(2, 0))

    def test_all_done_when_plan_finished(self):
        self.assertEqual([SEGMENT_DONE] * 4, segment_states(4, 4))

    def test_empty_plan_has_no_segments(self):
        self.assertEqual([], segment_states(0, 0))

    def test_rejects_negative_values(self):
        with self.assertRaisesRegex(ValueError, "done=-1"):
            segment_states(3, -1)


if __name__ == "__main__":
    unittest.main()
