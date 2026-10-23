"""Audit selected SLAKE CT CSVs against original split metadata; print aggregates only."""
from __future__ import annotations
import argparse
import csv
import io
import json
import zipfile
from pathlib import Path

REGIONS = ['Abdomen', 'Brain_Face', 'Neck']

def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream: return list(csv.DictReader(stream))

def audit(data_root, original_zip=None):
    original = {}
    if original_zip:
        with zipfile.ZipFile(original_zip) as archive:
            for split, source in [('train','train'),('val','validation'),('test','test')]:
                original[split] = list(csv.DictReader(io.StringIO(archive.read(f'slake_metadata_{source}.csv').decode('utf-8-sig'))))
    result = {'scope':'English CT questions in Abdomen, Brain_Face, and Neck',
              'original_metadata_checked':bool(original),'regions':{},'errors':[]}
    for region in REGIONS:
        splits = {}; image_sets = {}
        for split in ['train','val','test']:
            splits[split] = {}; image_sets[split] = set()
            for kind in ['open','closed']:
                rows = read_rows(data_root / region / 'CT' / split / (kind+'.csv'))
                required = {'qid','img_id','q_lang','modality','location','answer_type','answer'}
                if rows and not required <= set(rows[0]): raise ValueError('Missing required metadata columns')
                ids = {r['qid'] for r in rows}
                if len(ids) != len(rows):result['errors'].append(f'{region}/{split}/{kind}: duplicate question IDs')
                if any(r['q_lang']!='en' or r['modality']!='CT' or r['location']!=region or r['answer_type']!=kind.upper() for r in rows):
                    result['errors'].append(f'{region}/{split}/{kind}: unexpected language, modality, region, or type')
                entry = {'rows':len(rows),'yes_no_rows':sum(r['answer'].strip().lower() in {'yes','no'} for r in rows)}
                if original:
                    expected = {r['qid'] for r in original[split] if r['q_lang']=='en' and r['modality']=='CT' and r['location']==region and r['answer_type']==kind.upper()}
                    entry['matches_original_question_ids'] = ids == expected
                    if ids != expected:result['errors'].append(f'{region}/{split}/{kind}: original split membership differs')
                splits[split][kind] = entry
                image_sets[split].update(r['img_id'] for r in rows)
        overlaps = {a+'_'+b:len(image_sets[a]&image_sets[b]) for a,b in [('train','val'),('train','test'),('val','test')]}
        if any(overlaps.values()):result['errors'].append(f'{region}: shared image IDs across splits')
        result['regions'][region] = {'splits':splits,'image_id_overlap_counts':overlaps}
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--original-zip', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.data_root,args.original_zip)
    text = json.dumps(result,indent=2)+'\n'
    if args.output: args.output.write_text(text,encoding='utf-8',newline='\n')
    print(text)
    return 1 if result['errors'] else 0

if __name__ == '__main__': raise SystemExit(main())
