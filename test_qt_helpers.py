import unittest
from threading import Event

from novel_app.qt.helpers import (
    AI_PROBABILITY_META,
    DEFAULT_AI_PROBABILITY_META,
    compute_template_stats,
    count_text_characters,
    format_chapter_tree_title,
    format_chapter_tree_display_title,
    normalize_ai_color_config,
    normalize_ai_probability_pair,
    row_to_dict,
    set_ai_probability_meta,
)

try:
    from novel_app.qt_app import DRAWER_TAB_SEQUENCE
    from novel_app.qt.workers import FunctionWorker
except Exception:  # noqa: BLE001
    DRAWER_TAB_SEQUENCE = ()
    FunctionWorker = None


class QtHelperTests(unittest.TestCase):
    def test_row_to_dict_handles_empty_row(self) -> None:
        self.assertEqual(row_to_dict(None), {})
        self.assertEqual(row_to_dict({"id": 1, "title": "书"}), {"id": 1, "title": "书"})

    def test_ai_probability_normalizes_thresholds(self) -> None:
        self.assertEqual(normalize_ai_probability_pair("none", 0), (0, "none"))
        self.assertEqual(normalize_ai_probability_pair("low", 18), (18, "low"))
        self.assertEqual(normalize_ai_probability_pair("medium", 42), (42, "medium"))
        self.assertEqual(normalize_ai_probability_pair("high", 68), (68, "high"))
        self.assertEqual(normalize_ai_probability_pair("certain", 92), (100, "certain"))

    def test_ai_probability_ignores_inconsistent_or_unknown_level(self) -> None:
        self.assertEqual(normalize_ai_probability_pair("high", 0), (0, "none"))
        self.assertEqual(normalize_ai_probability_pair("unknown", 77), (77, "high"))
        self.assertEqual(normalize_ai_probability_pair("low", 150), (100, "certain"))
        self.assertEqual(normalize_ai_probability_pair("medium", -5), (0, "none"))
        self.assertIn("tree", AI_PROBABILITY_META["high"])

    def test_ai_color_config_merges_user_overrides(self) -> None:
        merged = normalize_ai_color_config(
            {
                "high": {"fg": "112233", "bg": "#445566", "tree": "bad"},
                "ghost": {"fg": "#FFFFFF"},
            }
        )
        self.assertEqual(merged["high"]["fg"], "#112233")
        self.assertEqual(merged["high"]["bg"], "#445566")
        self.assertEqual(merged["high"]["tree"], DEFAULT_AI_PROBABILITY_META["high"]["tree"])
        self.assertNotIn("ghost", merged)

    def test_set_ai_probability_meta_updates_shared_mapping(self) -> None:
        try:
            set_ai_probability_meta({"low": {"tree": "#123456"}})
            self.assertEqual(AI_PROBABILITY_META["low"]["tree"], "#123456")
        finally:
            set_ai_probability_meta({})

    def test_format_chapter_tree_title_preserves_known_titles(self) -> None:
        self.assertEqual(format_chapter_tree_title(1, "第一章 风起"), "第一章 风起")
        self.assertEqual(format_chapter_tree_title(2, "序章"), "序章")
        self.assertEqual(format_chapter_tree_title(3, "番外 旧梦"), "番外 旧梦")
        self.assertEqual(format_chapter_tree_title(4, "| 4 | 雨夜"), "| 4 | 雨夜")

    def test_format_chapter_tree_title_adds_sort_order_for_plain_title(self) -> None:
        self.assertEqual(format_chapter_tree_title(5, "抵达港口"), "第5章 抵达港口")
        self.assertEqual(format_chapter_tree_title("三", "  新线索  "), "第三章 新线索")

    def test_template_stats_and_display_title(self) -> None:
        content = 'alpha beta\n“spoken line”\nmore text'
        stats = compute_template_stats(content)
        self.assertEqual(stats["word_count"], count_text_characters(content))
        self.assertGreater(stats["dialogue_density"], 0)
        self.assertIn("123字", format_chapter_tree_display_title(2, "Plain", word_count=123))
        self.assertTrue(format_chapter_tree_display_title(2, "Plain", is_template=True).startswith("⭐"))

    @unittest.skipUnless(DRAWER_TAB_SEQUENCE, "PyQt6 is not available")
    def test_drawer_tab_sequence_uses_named_review_tab(self) -> None:
        self.assertEqual(len(DRAWER_TAB_SEQUENCE), len(set(DRAWER_TAB_SEQUENCE)))
        self.assertIn("tasks", DRAWER_TAB_SEQUENCE)
        self.assertIn("review", DRAWER_TAB_SEQUENCE)
        self.assertLess(DRAWER_TAB_SEQUENCE.index("review"), DRAWER_TAB_SEQUENCE.index("tasks"))

    @unittest.skipUnless(FunctionWorker, "PyQt6 is not available")
    def test_function_worker_can_deliver_cancelled_payload(self) -> None:
        cancel_event = Event()
        done_payloads = []
        cancelled_messages = []

        def callback(event: Event) -> dict[str, bool]:
            event.set()
            return {"cancelled": True}

        worker = FunctionWorker(
            callback,
            pass_cancel=True,
            cancel_event=cancel_event,
            deliver_result_on_cancel=True,
        )
        worker.done.connect(done_payloads.append)
        worker.cancelled.connect(cancelled_messages.append)
        worker.run()

        self.assertEqual(done_payloads, [{"cancelled": True}])
        self.assertEqual(cancelled_messages, [])


if __name__ == "__main__":
    unittest.main()
