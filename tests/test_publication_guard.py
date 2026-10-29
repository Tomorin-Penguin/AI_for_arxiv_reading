import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from publication_guard import validate_publication


def tree(count=127):
    return {"truncated": False, "tree": [
        {"path": f"file-{i}.md", "mode": "100644", "type": "blob", "sha": "a" * 40}
        for i in range(count)
    ]}


class PublicationGuardTests(unittest.TestCase):
    def setUp(self):
        self.before = tree()
        self.after = copy.deepcopy(self.before)
        self.after["tree"][0]["sha"] = "b" * 40
        self.expected = {"file-0.md": "b" * 40}

    def test_safe_single_file_update(self):
        self.assertEqual(validate_publication(self.before, self.after, self.expected), ["file-0.md"])

    def test_accidental_base_tree_omission(self):
        self.after["tree"] = self.after["tree"][:1]
        with self.assertRaisesRegex(ValueError, "deleted paths"):
            validate_publication(self.before, self.after, self.expected)

    def test_unrelated_edit(self):
        self.after["tree"][1]["sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "unexpected changes"):
            validate_publication(self.before, self.after, self.expected)

    def test_wrong_content(self):
        with self.assertRaisesRegex(ValueError, "mismatch"):
            validate_publication(self.before, self.after, {"file-0.md": "c" * 40})

    def test_mode_change(self):
        self.after["tree"][0]["mode"] = "100755"
        with self.assertRaises(ValueError):
            validate_publication(self.before, self.after, self.expected)

    def test_truncated_either_tree(self):
        for position in (0, 1):
            snapshots = [copy.deepcopy(self.before), copy.deepcopy(self.after)]
            snapshots[position]["truncated"] = True
            with self.assertRaises(ValueError):
                validate_publication(*snapshots, self.expected)

    def test_duplicate_path(self):
        self.after["tree"].append(self.after["tree"][0])
        with self.assertRaises(ValueError):
            validate_publication(self.before, self.after, self.expected)

    def test_add_card(self):
        self.after["tree"].append({"path": "papers/new.md", "mode": "100644", "type": "blob", "sha": "c" * 40})
        self.expected["papers/new.md"] = "c" * 40
        self.assertEqual(len(validate_publication(self.before, self.after, self.expected)), 2)


if __name__ == "__main__":
    unittest.main()
