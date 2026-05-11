from __future__ import annotations

import unittest

from novel_app.text_importer import parse_long_text


class TextImporterTests(unittest.TestCase):
    def test_parse_explicit_volumes_and_chapters(self) -> None:
        sample = "\n".join(
            [
                "\u7b2c\u4e00\u5377 \u98ce\u8d77",
                "\u7b2c\u4e00\u7ae0 \u5f00\u7aef",
                "\u5c11\u5e74\u63a8\u5f00\u65e7\u95e8\u3002\u98ce\u4ece\u57ce\u5916\u6765\u3002",
                "\u7b2c\u4e8c\u7ae0 \u8ffd\u8e2a",
                "\u5979\u6cbf\u7740\u6cb3\u5cb8\u5bfb\u627e\u7ebf\u7d22\u3002",
                "\u7b2c\u4e8c\u5377 \u5f52\u6f6e",
                "\u7b2c\u4e09\u7ae0 \u91cd\u9022",
                "\u591a\u5e74\u540e\u4ed6\u4eec\u5728\u6e21\u53e3\u91cd\u9022\u3002",
            ]
        )

        parsed = parse_long_text("\u6d4b\u8bd5\u5bfc\u5165", sample)

        self.assertEqual(len(parsed.chapters), 3)
        self.assertEqual(len({chapter.volume_title for chapter in parsed.chapters if chapter.volume_title}), 2)
        self.assertIn("\u6d4b\u8bd5\u5bfc\u5165", parsed.outline)
        self.assertTrue(all(chapter.outline for chapter in parsed.chapters))

    def test_chunk_text_without_headings(self) -> None:
        paragraph = "\u8fd9\u662f\u4e00\u6bb5\u9700\u8981\u81ea\u52a8\u5206\u7ae0\u7684\u957f\u6587\u3002"
        raw_text = "\n\n".join([paragraph * 60 for _ in range(8)])

        parsed = parse_long_text("\u65e0\u6807\u9898\u6587\u672c", raw_text)

        self.assertGreater(len(parsed.chapters), 1)
        self.assertTrue(parsed.outline)
        self.assertTrue(all(chapter.content for chapter in parsed.chapters))

    def test_parse_decorated_prologue_and_acts(self) -> None:
        sample = "\n".join(
            [
                "====================楔子",
                "雨夜里，旧城忽然停电。",
                "第一幕·世界的王座",
                "|1|黑蛇",
                "它又来了，月光落在铁门上。",
                "第二幕：燃烧的海",
                "|1|余烬",
                "火光把海面照得发白。",
            ]
        )

        parsed = parse_long_text("装饰标题", sample)

        self.assertEqual([chapter.title for chapter in parsed.chapters], ["楔子", "|1|黑蛇", "|1|余烬"])
        self.assertEqual(parsed.chapters[1].volume_title, "第一幕·世界的王座")
        self.assertEqual(parsed.chapters[2].volume_title, "第二幕：燃烧的海")

    def test_parse_pipe_sections_when_no_formal_chapters(self) -> None:
        sample = "\n".join(
            [
                "|1|黑蛇",
                "它又来了，月光落在铁门上。",
                "|2|门后",
                "门后传来轻微的呼吸声。",
                "|3|回声",
                "走廊尽头响起了回声。",
            ]
        )

        parsed = parse_long_text("小节标题", sample)

        self.assertEqual(len(parsed.chapters), 3)
        self.assertEqual(parsed.chapters[0].title, "|1|黑蛇")

    def test_catalog_noise_is_not_imported_as_chapter(self) -> None:
        sample = "\n".join(
            [
                "目录",
                "第一章 开端",
                "第二章 追踪",
                "正文",
                "第一章 开端",
                "少年推开旧门。风从城外来。",
                "第二章 追踪",
                "她沿着河岸寻找线索。",
            ]
        )

        parsed = parse_long_text("目录清理", sample)

        self.assertEqual([chapter.title for chapter in parsed.chapters], ["第一章 开端", "第二章 追踪"])
        self.assertNotIn("目录", parsed.chapters[0].content)

    def test_acts_become_volumes_when_chapters_exist(self) -> None:
        sample = "\n".join(
            [
                "第一幕 世界的王座",
                "第1章 黑蛇",
                "它又来了，月光落在铁门上。",
                "第二幕 燃烧的海",
                "第2章 余烬",
                "火光把海面照得发白。",
            ]
        )

        parsed = parse_long_text("幕结构", sample)

        self.assertEqual([chapter.title for chapter in parsed.chapters], ["第1章 黑蛇", "第2章 余烬"])
        self.assertEqual(parsed.chapters[0].volume_title, "第一幕 世界的王座")
        self.assertEqual(parsed.chapters[1].volume_title, "第二幕 燃烧的海")


if __name__ == "__main__":
    unittest.main()
