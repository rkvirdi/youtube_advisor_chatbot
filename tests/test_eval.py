\
import os, sys, unittest
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from qa import answer

TRANSCRIPTS = os.path.join(os.path.dirname(__file__), "..", "transcripts")

class TestAdvisor(unittest.TestCase):
    def test_schema_citations_present(self):
        res = answer("How do I write a killer intro?", TRANSCRIPTS)
        self.assertTrue(res["citations"], "Every answer should include at least one citation")

    def test_grounding_story_points_to_video2(self):
        res = answer("How do I pace my story and build peaks and valleys?", TRANSCRIPTS)
        vids = {c['video'] for c in res.get("citations", [])}
        self.assertIn("video_2", vids, "Expected at least one citation to video_2 for storytelling question")

    def test_fallback_out_of_scope(self):
        res = answer("Best mirrorless camera under $500?")
        self.assertFalse(res["citations"], "Out-of-scope should not include citations")

if __name__ == "__main__":
    unittest.main()
