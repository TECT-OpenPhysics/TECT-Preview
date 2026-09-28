"""The existing exact-byte hydration must precede fresh-checkout evidence gates."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class EvidenceBootstrapOrder(unittest.TestCase):
    def test_both_workflows_restore_before_any_evidence_consumer(self):
        command = 'python -X utf8 verification/scripts/portable_evidence.py --restore'
        for name, consumer in (('pages.yml', 'Verify tracked publication snapshot'),
                               ('verify.yml', 'Lint claim ledger')):
            with self.subTest(workflow=name):
                text = (ROOT/'.github/workflows'/name).read_text(encoding='utf-8')
                self.assertEqual(text.count(command), 1)
                self.assertLess(text.index(command), text.index(consumer))
                self.assertLess(text.index('actions/setup-python'), text.index(command))
                self.assertIn('fetch-depth: 0', text)
                self.assertIn('verification/scripts/release_check.py', text)


if __name__ == '__main__':
    unittest.main()
