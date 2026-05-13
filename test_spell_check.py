from __future__ import annotations

import unittest

from novel_app.spell_check import detect_chinese_typos


class SpellCheckTests(unittest.TestCase):
    def test_detects_known_confusion_words(self) -> None:
        findings = detect_chinese_typos("他迫不急待地冲出去，仿佛已经跑到九宵云外。")
        pairs = {(item["wrong"], item["suggestion"]) for item in findings}
        self.assertIn(("迫不急待", "迫不及待"), pairs)
        self.assertIn(("九宵云外", "九霄云外"), pairs)
        self.assertTrue(any(item["pinyin_features"] for item in findings))

    def test_detects_contextual_pinyin_confusion(self) -> None:
        findings = detect_chinese_typos("她轻轻的推开门，悄悄的看向院子。")
        pairs = [(item["wrong"], item["suggestion"], item["rule"]) for item in findings]
        self.assertIn(("的", "地", "pinyin_context"), pairs)

    def test_does_not_flag_normal_pronouns_or_particles(self) -> None:
        findings = detect_chinese_typos("他看见她站在门口，于是再次确认那里没有人。")
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
