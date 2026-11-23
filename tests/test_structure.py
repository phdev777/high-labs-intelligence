import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class SkillStructureTests(unittest.TestCase):
    def test_valid_frontmatter(self):
        s=(ROOT/"SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(s.startswith("---\n"))
        fm=s.split("---",2)[1]
        name=re.search(r"^name:\s*(\S+)\s*$",fm,re.M).group(1)
        desc=re.search(r"^description:\s*(.+)$",fm,re.M).group(1)
        self.assertRegex(name,r"^[a-z0-9-]{1,64}$")
        self.assertTrue(1<=len(desc)<=1024)
    def test_references_exist(self):
        s=(ROOT/"SKILL.md").read_text(encoding="utf-8")
        for rel in re.findall(r"\]\((references/[^)]+|templates/[^)]+)\)",s):
            with self.subTest(rel=rel):
                self.assertTrue((ROOT/rel).is_file())
if __name__=="__main__":
    unittest.main()
