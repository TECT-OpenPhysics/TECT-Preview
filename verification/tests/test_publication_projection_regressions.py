"""Publication regressions: bounded kind parts and adjacent authority anchors."""
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
from build_catalog import _kind_parts
from build_proof_evidence_map import parse_sections, redact_internal_file_references


class PublicationProjectionRegressions(unittest.TestCase):
    def test_split_is_byte_bounded_order_preserving_and_deterministic(self):
        entries = [{'path':str(i), 'value':'x'*30+'\u00e9'*8} for i in range(12)]
        budget = 400  # Test oracle tooling budget, deliberately small.
        parts = _kind_parts('test', entries, budget)
        self.assertGreater(len(parts),1)
        recovered = []
        for count,text in parts:
            payload = json.loads(text)
            self.assertLessEqual(len(text.encode('utf-8')),budget)
            self.assertEqual(count,len(payload['entries']))
            recovered.extend(payload['entries'])
        self.assertEqual(recovered,entries)
        self.assertEqual(parts,_kind_parts('test',entries,budget))
        with self.assertRaises(ValueError):
            _kind_parts('test',[{'value':'x'*budget}],budget)

    def test_next_inline_anchor_does_not_pollute_previous_result(self):
        source = '### R-375 -- First\n**Boundary:** Retain evidence.<a id="r-374"></a>\n### R-374 -- Second\n**Statement:** Separate result.\n'
        parsed = parse_sections(source,r'R-\d{3}')
        self.assertEqual(parsed['R-375']['fields']['boundary'],'Retain evidence.')
        self.assertEqual(parsed['R-374']['fields']['statement'],'Separate result.')
        separate = '### R-001 -- First\n**Scope:** Retained.\n<a id="r-002"></a>\n### R-002 -- Second\n**Scope:** Also retained.\n## Process-grade\nNot result evidence.\n'
        parsed = parse_sections(separate,r'R-\d{3}')
        self.assertEqual(parsed['R-001']['fields']['scope'],'Retained.')
        self.assertEqual(parsed['R-002']['fields']['scope'],'Also retained.')

    def test_public_redaction_does_not_mutate_authority(self):
        private_fixture = 'internal/' + 'private/data.json'  # TEST_ONLY, not an evidence pointer.
        raw = {'id':'EXP-000001','verdict':'inconclusive','path':private_fixture,
               'public_path':'strategy/clock/example.json','text':'Plain text','glyph':'\ucca0',
               'formal_refs':{'results':['R-001']}}
        public = redact_internal_file_references(raw)
        self.assertEqual(raw['path'],private_fixture)
        self.assertEqual(public['path'],'operator-managed ignored workspace file (not published)')
        self.assertEqual(public['glyph'],'\\ucca0')
        self.assertEqual(public['public_path'],raw['public_path'])
        self.assertEqual(public['text'],raw['text'])
        self.assertEqual(public['formal_refs'],raw['formal_refs'])
        self.assertEqual(public['id'],raw['id'])
        self.assertEqual(public['verdict'],raw['verdict'])


if __name__ == '__main__':
    unittest.main()
