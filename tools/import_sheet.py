"""구글 시트(엑셀로 내려받은 파일) → data/content.json 갱신.

사용: python tools/import_sheet.py 시트파일.xlsx
구글 시트에서 [파일 > 다운로드 > Microsoft Excel]로 받은 파일을 넣으면,
사이트가 시트를 읽는 방식과 똑같이 content.json을 다시 만듭니다.
(시트가 정본일 때, 코드 작업 전에 content.json을 시트와 맞추는 용도)
설명 그림(art)처럼 시트에 없는 값은 기존 content.json 값을 유지합니다.
"""
import json
import shutil
import sys
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
CJ = ROOT / 'data' / 'content.json'


def rows(wb, name):
    if name not in wb.sheetnames:
        return []
    it = wb[name].iter_rows(values_only=True)
    head = [str(h or '').strip() for h in next(it, [])]
    out = []
    for r in it:
        vals = ['' if v is None else str(v).strip() for v in r]
        if any(vals):
            out.append(dict(zip(head, vals + [''] * (len(head) - len(vals)))))
    return out


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def step_no(v):
    v = str(v)
    return v[:-2] if v.endswith('.0') else v


def main(path):
    old = json.loads(CJ.read_text(encoding='utf-8'))
    wb = load_workbook(path, read_only=True)
    cm, pg, st, it, ph, ce, tp, sy, fq = (rows(wb, n) for n in ('큰 메뉴', '페이지', '단계', '항목', '사진', '센터', '주제', '검색어', '자주 묻는 질문'))
    if not pg or not it:
        raise SystemExit('페이지/항목 탭을 찾지 못했습니다. 탭 이름을 확인하세요.')

    def art(pid, n):
        p = next((x for x in old['pages'] if x['id'] == pid), None)
        s = p and next((x for x in p['steps'] if str(x['n']) == n), None)
        return s.get('art', '') if s else ''

    items = {}
    for r in it:
        iid, ref = r.get('항목ID'), r.get('같은 내용 가져오기')
        if not iid or ref == iid:
            continue
        if ref:
            items[iid] = {'ref': ref}
            continue
        items[iid] = {'text': r.get('문장', ''), 'rid': r.get('규칙번호', ''), 'tag': r.get('표시', ''), 'why': r.get('이유', ''),
                      'exc': r.get('예외·주의', ''), 'act': r.get('확인·대응', ''),
                      'table': [[c.strip() for c in l.split('|')] for l in r.get('표', '').split('\n') if l.strip()],
                      'source': r.get('근거', ''), 'nophoto': r.get('사진 없이 글로 충분', '').lower().startswith('y'),
                      'todo': r.get('필요한 사진', ''), 'media': [], 'topic': r.get('주제', '')}
        if r.get('사진 모두 표시', '').lower().startswith('y'):
            items[iid]['grid'] = True
        if r.get('정상 2장 세트', '').lower().startswith('y'):
            items[iid]['okpair'] = True
        if r.get('숨김', '').lower().startswith('y'):
            items[iid]['hide'] = True
        if r.get('설명 그림 안 씀', '').lower().startswith('y'):
            items[iid]['nodraw'] = True
    seen = set()
    for r in sorted(ph, key=lambda r: num(r.get('순서'))):
        x, k = items.get(r.get('항목ID')), (r.get('항목ID'), r.get('파일'))
        if x and 'media' in x and k not in seen:
            seen.add(k)
            x['media'].append([r.get('종류', ''), r.get('파일', ''), r.get('설명', '')])

    pages = []
    for r in sorted(pg, key=lambda r: num(r.get('순서'))):
        pid = r['페이지ID']
        steps = sorted(({'n': step_no(x['단계']), 't': x.get('단계 제목', ''), **({'hide': True} if x.get('숨김', '').lower().startswith('y') else {})} for x in st if x.get('페이지ID') == pid), key=lambda s: num(s['n']))
        for s in steps:
            s['art'] = art(pid, s['n'])
            s['items'] = [x['항목ID'] for x in sorted((x for x in it if x.get('페이지ID') == pid and step_no(x.get('단계')) == s['n']),
                                                      key=lambda x: num(x.get('순서')))]
        pages.append({'cat': r.get('큰 메뉴', ''), 'id': pid, 'sub': r.get('작은 메뉴', ''), 'title': r.get('페이지 제목', ''),
                      'desc': r.get('한 줄 설명', ''), 'en': r.get('영문 라벨', ''), 'layout': r.get('모양') or '기본', 'steps': steps,
                      **({'topic': r['자동 모음 주제']} if r.get('자동 모음 주제') else {})})

    M = {'cats': [{'name': r['큰 메뉴'], 'en': r.get('영문 라벨', ''), 'desc': r.get('첫 화면 설명', ''), 'img': r.get('첫 화면 사진', '')}
                  for r in sorted(cm, key=lambda r: num(r.get('순서')))],
         'pages': pages, 'items': items,
         'centers': [{'id': r.get('센터ID', ''), 'name': r.get('센터 이름', ''), 'addr': r.get('도로명 주소', ''), 'jibun': r.get('지번 주소', ''),
                      'map': r.get('지도 링크', ''), 'kinds': r.get('입고 가능 복종', '')} for r in ce],
         'synonyms': [r['같은 뜻 낱말'] for r in sy if r.get('같은 뜻 낱말')] or old.get('synonyms', []),
         'faq': [{'q': r['질문'], 'to': r['연결']} for r in sorted(fq, key=lambda r: num(r.get('순서'))) if r.get('질문') and r.get('연결')] or old.get('faq', []),
         'topics': [r['주제'] for r in sorted(tp, key=lambda r: num(r.get('순서'))) if r.get('주제')] or old.get('topics', [])}
    shutil.copy(CJ, CJ.with_suffix('.json.bak'))
    CJ.write_text(json.dumps(M, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'content.json 갱신: 페이지 {len(pages)}개, 항목 {len(items)}개 (이전 파일은 content.json.bak)')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    try:
        main(sys.argv[1])
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print('실패:', e)
        sys.exit(1)
