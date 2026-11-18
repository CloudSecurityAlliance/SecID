"""Offline regression gate for release membership and generated CWE references."""
import copy
import importlib.util
import json
import re
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("sync_cwe", Path(__file__).with_name("sync-cwe.py"))
cwe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cwe)


class CweDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(cwe.MANIFEST.read_text())
        cls.source = json.loads(cwe.REGISTRY.read_text())["match_nodes"][0]

    def test_registry_is_reproducible(self):
        versions, children = cwe.generated(self.manifest)
        self.assertEqual(self.source["data"]["versions_available"], versions)
        self.assertEqual(self.source["children"], children)

    def test_archive_counts_and_category_to_grouping_transition(self):
        expected = {"4.19": (969, 420, 58), "4.19.1": (969, 420, 58),
                    "4.20": (969, 422, 59), "4.21": (984, 431, 62), "5.0": (984, 431, 62)}
        self.assertEqual({r["version"] for r in self.manifest["releases"]}, set(expected))
        for release in self.manifest["releases"]:
            ids = release["ids"]
            grouping = "Groupings" if release["version"] == "5.0" else "Categories"
            self.assertEqual(set(ids), {"Weaknesses", grouping, "Views"})
            self.assertEqual(tuple(len(ids[k]) for k in ["Weaknesses", grouping, "Views"]), expected[release["version"]])
            self.assertIn(79, ids["Weaknesses"])
            self.assertIn(1425, ids["Views"])
            self.assertEqual(1448 in ids["Views"], release["version"] in {"4.20", "4.21", "5.0"})

    def test_every_id_matches_only_its_release_kind(self):
        for release in self.manifest["releases"]:
            version = release["version"]
            branch = next(c for c in self.source["children"] if c.get("children") and re.fullmatch(c["patterns"][0], version))
            branches = branch["children"]
            for number in range(0, 2101):
                for prefix in ["CWE", "cwe", "CwE"]:
                    hits = [i for i, c in enumerate(branches) if re.fullmatch(c["patterns"][0], f"{prefix}-{number}")]
                    expected = [i for i, ids in enumerate(release["ids"].values()) if number in ids]
                    self.assertEqual(hits, expected, (version, prefix, number))
            for child in branches:
                self.assertEqual(child["data"]["url"], release["url"])
                self.assertEqual(child["data"]["content_type"], "application/zip")
                self.assertIn("@ID", child["data"]["parsing_instructions"])

    def test_bad_ids_and_duplicate_kinds_are_rejected(self):
        for child in self.source["children"]:
            if "children" in child:
                continue
            for invalid in ["CWE-0", "CWE-999999", "CWE-079", "CWE-79x", "CWE-79/unknown"]:
                self.assertFalse(any(re.fullmatch(p, invalid) for p in child["patterns"]), invalid)
        broken = copy.deepcopy(self.manifest)
        broken["releases"][0]["ids"]["Views"].append(79)
        with self.assertRaises(ValueError):
            cwe.generated(broken)


if __name__ == "__main__":
    unittest.main()
