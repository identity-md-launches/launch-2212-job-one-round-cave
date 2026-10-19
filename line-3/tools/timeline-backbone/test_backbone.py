import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backbone
import replay


class BackboneTests(unittest.TestCase):
    def make_timeline(self, logs, bound=0):
        pack = replay.make_pack(logs, clock_uncertainty_ms=bound)
        replay.verify_pack(pack)
        return pack["timeline"]

    def test_definite_order_and_overlap_counts(self):
        timeline = self.make_timeline([
            ("a", b"2026-10-18T10:00:00Z a\n"),
            ("b", b"2026-10-18T10:00:01Z b\n"),
            ("c", b"2026-10-18T10:00:04Z c\n"),
        ], 250)
        result = backbone.summarize(timeline)
        self.assertEqual((result["pairs"], result["definitely_ordered_pairs"],
                          result["unresolved_pairs"]), (3, 2, 1))
        by_source = {item["source"]: item for item in result["citations"]}
        self.assertEqual(by_source["a"]["unresolved_pairs"], 1)
        self.assertEqual(by_source["b"]["definitely_after"], 1)
        self.assertEqual(by_source["c"]["definitely_before"], 2)

    def test_half_open_touch_is_ordered(self):
        timeline = self.make_timeline([
            ("a", b"2026-10-18T10:00:00Z a\n"),
            ("b", b"2026-10-18T10:00:01Z b\n"),
        ])
        result = backbone.summarize(timeline)
        self.assertEqual(result["definitely_ordered_pairs"], 1)
        self.assertEqual(result["unresolved_pairs"], 0)

    def test_identical_interval_is_unresolved(self):
        timeline = self.make_timeline([
            ("a", b"2026-10-18T10:00:00Z a\n"),
            ("b", b"2026-10-18T10:00:00Z b\n"),
        ])
        result = backbone.summarize(timeline)
        self.assertEqual(result["unresolved_pairs"], 1)
        self.assertTrue(all(item["unresolved_pairs"] == 1 for item in result["citations"]))

    def test_empty_and_display_limit(self):
        self.assertEqual(backbone.summarize({"events": []}, 0)["pairs"], 0)
        timeline = self.make_timeline([
            ("a", b"2026-10-18T10:00:00Z a\n"),
            ("b", b"2026-10-18T10:00:02Z b\n"),
            ("c", b"2026-10-18T10:00:04Z c\n"),
        ])
        result = backbone.summarize(timeline, 1)
        self.assertEqual(len(result["citations"]), 1)
        self.assertEqual(result["omitted_citations"], 2)
        self.assertEqual(result["definitely_ordered_pairs"], 3)

    def test_limit_is_bounded(self):
        with self.assertRaises(ValueError):
            backbone.summarize({"events": []}, 201)
        with self.assertRaises(ValueError):
            backbone.summarize({"events": []}, True)

    def test_demo_is_replay_verified(self):
        result = backbone.demo()
        self.assertTrue(result["replay"]["verified"])
        self.assertEqual(result["definitely_ordered_pairs"], 2)
        self.assertEqual(result["unresolved_pairs"], 1)


if __name__ == "__main__":
    unittest.main()
