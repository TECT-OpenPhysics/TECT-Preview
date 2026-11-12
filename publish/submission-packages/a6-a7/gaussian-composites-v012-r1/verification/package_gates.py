"""Fail-closed PDF and all-page visual-receipt gates; no proof certification."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate_pdf_qa(qa):
    require(qa.get('schema') == 'tect/a6-a7-paper-pdf-qa/1.0' and qa.get('status') == 'PASS', 'PDF QA schema/status')
    count = qa.get('page_count')
    require(type(count) is int and count > 0, 'PDF page count')
    pages = qa.get('pages')
    require(isinstance(pages, list) and len(pages) == count, 'PDF QA page inventory')
    require(all(type(row.get('page')) is int for row in pages), 'PDF QA integer page')
    require([row['page'] for row in pages] == list(range(1, count + 1)), 'PDF QA page order')


def png_info(path):
    data = path.read_bytes()
    require(data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR' and len(data) >= 24, 'PNG header')
    width, height = struct.unpack('>II', data[16:24])
    require(width > 0 and height > 0, 'PNG dimensions')
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'width': width, 'height': height}


def validate_output_paths(paper, destination, extracted, report):
    source = Path(paper).resolve()
    outputs = [Path(p).resolve() for p in (destination, Path(destination).with_suffix('.zip'), extracted, report)]
    require(all(not p.exists() for p in outputs), 'Issued output already exists')
    paths = [source, *outputs]
    for i, left in enumerate(paths):
        for right in paths[i+1:]:
            require(left != right and not left.is_relative_to(right) and not right.is_relative_to(left), 'Overlapping source/output paths')


def validate_visual(review, qa, paper):
    validate_pdf_qa(qa)
    require(review.get('schema') == 'tect/a6-a7-paper-render-review/1.1', 'Visual review schema')
    require(review.get('status') == 'PASS' and review.get('defects') == [], 'Visual review status/defects')
    require(review.get('external_review') == 'NOT_PERFORMED', 'False external-review status')
    for key in ('pdf_sha256', 'tex_sha256'):
        require(review.get(key) == qa.get(key), 'Visual review source identity: ' + key)
    pages = list(range(1, qa['page_count'] + 1))
    require(review.get('pages_reviewed') == pages and all(type(p) is int for p in review['pages_reviewed']), 'Visual page list')
    require(set(review.get('page_findings', {})) == {str(p) for p in pages}, 'Missing page findings')
    require(all(isinstance(x, str) and x.strip() for x in review['page_findings'].values()), 'Empty page finding')
    rows = review.get('rendered_pages')
    require(isinstance(rows, list) and len(rows) == len(pages), 'Rendered page inventory')
    require(all(type(row.get('page')) is int for row in rows) and [r['page'] for r in rows] == pages, 'Rendered page order')
    root = Path(paper).resolve()
    directory = root / 'verification/rendered-v012'
    require(directory.is_dir() and not directory.is_symlink(), 'Render directory')
    require({p.name for p in directory.iterdir()} == {f'page-{p}.png' for p in pages}, 'Missing or extra render')
    for row in rows:
        name = f"verification/rendered-v012/page-{row['page']}.png"
        require(row.get('path') == name, 'Rendered page path')
        path = root / name
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root), 'Unsafe render')
        for key, value in png_info(path).items():
            require(row.get(key) == value, 'Rendered identity: ' + key)


def self_test():
    # INPUT: minimal PNG header fixture; tests byte/identity gates, not image decoding.
    png = b'\x89PNG\r\n\x1a\n' + struct.pack('>I', 13) + b'IHDR' + struct.pack('>II', 1, 1) + b'fixture'
    rejected = []
    with tempfile.TemporaryDirectory(prefix='a6a7-visual-gate-') as temp:
        root = Path(temp); directory = root / 'verification/rendered-v012'
        directory.mkdir(parents=True)
        image = directory / 'page-1.png'; image.write_bytes(png)
        qa = {'schema': 'tect/a6-a7-paper-pdf-qa/1.0', 'status': 'PASS',
              'page_count': 1, 'pages': [{'page': 1}], 'pdf_sha256': 'pdf', 'tex_sha256': 'tex'}
        review = {'schema': 'tect/a6-a7-paper-render-review/1.1', 'status': 'PASS',
                  'defects': [], 'external_review': 'NOT_PERFORMED', 'pdf_sha256': 'pdf',
                  'tex_sha256': 'tex', 'pages_reviewed': [1], 'page_findings': {'1': 'fixture'},
                  'rendered_pages': [{'page': 1, 'path': 'verification/rendered-v012/page-1.png', **png_info(image)}]}
        validate_visual(review, qa, root)

        def reject(name, changed, changed_qa=None):
            try:
                validate_visual(changed, changed_qa or qa, root)
            except (ValueError, KeyError, TypeError):
                rejected.append(name)
            else:
                raise ValueError('Accepted hostile visual receipt: ' + name)

        for key, value in [('schema', 'INVALID'), ('status', 'FAIL'), ('defects', ['clipped equation']),
                           ('external_review', 'PASS'), ('pdf_sha256', 'stale'), ('tex_sha256', 'stale'),
                           ('pages_reviewed', []), ('pages_reviewed', [1, 1]), ('pages_reviewed', [True]),
                           ('page_findings', {}), ('rendered_pages', [])]:
            changed = copy.deepcopy(review); changed[key] = value
            reject(key + ':' + repr(value), changed)
        for key, value in [('path', '../escape.png'), ('path', 'verification/rendered-v012/page-2.png'),
                           ('sha256', 'changed'), ('bytes', 0), ('width', 2), ('height', 2), ('page', True)]:
            changed = copy.deepcopy(review); changed['rendered_pages'][0][key] = value
            reject('render:' + key + ':' + repr(value), changed)
        for key, value in [('schema', 'INVALID'), ('status', 'FAIL'), ('page_count', True), ('pages', [{'page': True}])]:
            changed = copy.deepcopy(qa); changed[key] = value
            reject('qa:' + key, review, changed)
        image.unlink(); reject('missing PNG', review)
        image.write_bytes(png + b'changed'); reject('altered PNG', review)
        image.write_bytes(png)
        extra = directory / 'page-2.png'; extra.write_bytes(png)
        reject('extra PNG', review); extra.unlink()
        # Duplicate actual paths or swapped receipts cannot satisfy the exact page/path map.
        changed = copy.deepcopy(review); changed['rendered_pages'] *= 2
        reject('duplicate render row', changed)
        dest, extracted, report = root/'delivery', root/'extracted', root/'report.json'
        validate_output_paths(directory, dest, extracted, report)
        hostile_paths = [
            ('report inside destination',dest,extracted,dest/'report.json'),
            ('extraction inside destination',dest,dest/'unpacked',report),
            ('destination inside extraction',extracted/'delivery',extracted,report),
            ('destination inside source',directory/'delivery',extracted,report),
            ('source inside destination',root/'verification',extracted,report),
            ('report equals archive',dest,extracted,dest.with_suffix('.zip')),
            ('report inside extraction',dest,extracted,extracted/'report.json'),
            ('archive inside extraction',extracted/'name',extracted,report),
            ('destination equals extraction',dest,dest,report)]
        for label,destination,extraction,output in hostile_paths:
            try: validate_output_paths(directory,destination,extraction,output)
            except ValueError: rejected.append(label)
            else: raise ValueError('Accepted output mutation: '+label)
    return {'status': 'PASS', 'rejected_mutations': rejected, 'count': len(rejected)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--write-new', type=Path)
    args = parser.parse_args()
    require(args.self_test, 'Use --self-test')
    result = self_test()
    if args.write_new:
        args.write_new.parent.mkdir(parents=True, exist_ok=True)
        with args.write_new.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    print('PACKAGE VISUAL GATES: PASS', result['count'], 'hostile mutations rejected')
