from __future__ import annotations

import unittest
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

from novel_app.database import Database


class DatabaseExtensionTests(unittest.TestCase):
    def test_relationships_ai_spans_and_events_roundtrip(self) -> None:
        with TemporaryDirectory() as tmp:
            db = Database(Path(tmp) / "novels.db")
            db.initialize()
            book_id = db.create_book("测试书")
            source_id = db.create_character(book_id, "甲")
            target_id = db.create_character(book_id, "乙")
            db.update_character_position(source_id, 12.5, -8.0)
            relationship_id = db.create_relationship(book_id, source_id, target_id, "师徒", "旧识")
            chapter_id = db.create_chapter(book_id, "第一章")
            source_ref_id = db.create_reference_source("参考", source_path=str(Path(tmp) / "ref.txt"))
            db.replace_skills_for_source(
                source_ref_id,
                [
                    {
                        "name": "全局风格",
                        "category": "style",
                        "summary": "summary",
                        "instruction": "instruction",
                    }
                ],
            )
            skill_id = int(db.list_skills(source_ref_id)[0]["id"])
            db.bind_skill_to_global(skill_id)
            db.bind_skill_to_book(book_id, skill_id)
            db.bind_skill_to_chapter(chapter_id, skill_id)
            snapshot_id = db.create_snapshot(chapter_id, "before review", "old outline", "old content")
            span_id = db.add_chapter_ai_span(chapter_id, 2, 9, "job-1")
            event_id = db.create_chapter_event(book_id, chapter_id, "相遇", "甲乙初见")

            relationship = db.get_relationship(relationship_id)
            self.assertIsNotNone(relationship)
            self.assertEqual(relationship["relationship_type"], "师徒")
            self.assertEqual(len(db.list_relationships_by_character(source_id)), 1)
            db.replace_book_relationships(
                book_id,
                [
                    {
                        "source_character_id": target_id,
                        "target_character_id": source_id,
                        "relationship_type": "同盟",
                        "description": "AI 分析刷新",
                    }
                ],
            )
            replaced_relationships = db.list_relationships(book_id)
            self.assertEqual(len(replaced_relationships), 1)
            self.assertEqual(replaced_relationships[0]["relationship_type"], "同盟")
            self.assertEqual(replaced_relationships[0]["description"], "AI 分析刷新")
            self.assertEqual(len(db.list_bound_skills_for_global()), 1)
            self.assertEqual(len(db.list_bound_skills_for_book(book_id)), 1)
            self.assertEqual(len(db.list_bound_skills_for_chapter(chapter_id)), 1)
            db.unbind_skill_from_global(skill_id)
            self.assertEqual(db.list_bound_skills_for_global(), [])

            character = db.get_character(source_id)
            self.assertIsNotNone(character)
            self.assertEqual(float(character["graph_x"]), 12.5)
            self.assertEqual(float(character["graph_y"]), -8.0)

            spans = db.list_chapter_ai_spans(chapter_id)
            self.assertEqual(len(spans), 1)
            self.assertEqual(int(spans[0]["id"]), span_id)

            events = db.list_chapter_events(book_id)
            self.assertEqual(len(events), 1)
            self.assertEqual(int(events[0]["id"]), event_id)

            run_id = db.create_review_run(
                book_id=book_id,
                chapter_id=chapter_id,
                scope_type="chapter",
                status="applied",
                truth_snapshot="truth",
                summary="summary",
                overall_score=86,
                snapshot_id=snapshot_id,
                revised_content="content",
                revised_outline="outline",
                final_verdict="approve",
                risk_notes="risk",
                template_comparison="template delta",
                applied=True,
            )
            db.replace_review_findings(
                run_id,
                [
                    {
                        "agent": "plot_auditor",
                        "severity": "high",
                        "category": "plot",
                        "location_hint": "chapter",
                        "quote": "quote",
                        "issue": "issue",
                        "suggestion": "suggestion",
                    }
                ],
            )
            runs = db.list_review_runs(book_id, chapter_id)
            self.assertEqual(len(runs), 1)
            self.assertEqual(int(runs[0]["id"]), run_id)
            self.assertEqual(int(runs[0]["snapshot_id"]), snapshot_id)
            self.assertEqual(runs[0]["template_comparison"], "template delta")
            self.assertTrue(runs[0]["applied_at"])
            stored_run = db.get_review_run(run_id)
            self.assertIsNotNone(stored_run)
            self.assertEqual(int(stored_run["snapshot_id"]), snapshot_id)
            self.assertEqual(stored_run["template_comparison"], "template delta")
            findings = db.list_review_findings(run_id)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["severity"], "high")
            db.close()

    def test_review_run_migration_adds_snapshot_columns(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "novels.db"
            connection = sqlite3.connect(path)
            connection.executescript(
                """
                CREATE TABLE review_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    chapter_id INTEGER,
                    scope_type TEXT NOT NULL DEFAULT 'chapter',
                    status TEXT NOT NULL DEFAULT 'completed',
                    truth_snapshot TEXT NOT NULL DEFAULT '',
                    summary TEXT NOT NULL DEFAULT '',
                    overall_score INTEGER NOT NULL DEFAULT 0,
                    revised_content TEXT NOT NULL DEFAULT '',
                    revised_outline TEXT NOT NULL DEFAULT '',
                    final_verdict TEXT NOT NULL DEFAULT '',
                    risk_notes TEXT NOT NULL DEFAULT '',
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            connection.close()

            db = Database(path)
            db.initialize()
            columns = {row["name"] for row in db.connection.execute("PRAGMA table_info(review_runs)").fetchall()}
            self.assertIn("snapshot_id", columns)
            self.assertIn("applied_at", columns)
            self.assertIn("template_comparison", columns)
            tag_columns = {row["name"] for row in db.connection.execute("PRAGMA table_info(chapter_tags)").fetchall()}
            self.assertEqual({"chapter_id", "tag", "created_at"}, tag_columns)
            db.close()

    def test_chapter_template_tags_roundtrip(self) -> None:
        with TemporaryDirectory() as tmp:
            db = Database(Path(tmp) / "novels.db")
            db.initialize()
            book_id = db.create_book("Template Book")
            volume_id = db.create_volume(book_id, "Volume")
            first_id = db.create_chapter(book_id, "Template A", volume_id=volume_id)
            second_id = db.create_chapter(book_id, "Normal B", volume_id=volume_id)
            db.update_chapter(first_id, "outline", '“hi” scene')
            db.update_chapter(second_id, "", "body")

            self.assertFalse(db.has_chapter_tag(first_id, "template"))
            db.set_chapter_tag(first_id, "template")
            self.assertTrue(db.has_chapter_tag(first_id, "template"))
            templates = db.list_template_chapters(book_id)
            self.assertEqual([int(row["id"]) for row in templates], [first_id])
            self.assertEqual(templates[0]["volume_title"], "Volume")

            chapters = db.list_chapters(book_id)
            by_id = {int(row["id"]): row for row in chapters}
            self.assertEqual(int(by_id[first_id]["is_template"]), 1)
            self.assertEqual(int(by_id[second_id]["is_template"]), 0)
            self.assertGreater(int(by_id[first_id]["word_count"]), 0)

            db.remove_chapter_tag(first_id, "template")
            self.assertFalse(db.has_chapter_tag(first_id, "template"))
            self.assertEqual(db.list_template_chapters(book_id), [])
            db.close()

    def test_media_path_normalization_keeps_data_dir_relative(self) -> None:
        with TemporaryDirectory() as tmp:
            db = Database(Path(tmp) / "novels.db")
            db.initialize()
            image = db.book_covers_dir / "cover.png"
            image.write_bytes(b"not-a-real-image")
            stored = db.normalize_media_path(image)
            self.assertEqual(stored, "media/book_covers/cover.png")
            self.assertEqual(db.resolve_media_path(stored), image)
            db.close()


if __name__ == "__main__":
    unittest.main()
