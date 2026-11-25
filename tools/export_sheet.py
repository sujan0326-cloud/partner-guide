"""data/content.json → 구글 시트용 엑셀(.xlsx) 만들기.

사용: python tools/export_sheet.py [저장할 파일 경로]
만든 파일을 구글 드라이브에 올려 구글 시트로 열면, 사이트가 읽는 시트 구조와 똑같습니다.
(시트 내용을 content.json 기준으로 새로 채울 때 사용)
"""
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'dist' / 'K2_납품가이드_사이트내용.xlsx'
TAGS = '반송,입고 거부,입고 불가,시정요구,필수'
KINDS = '정상,불량,참고,문제,보완,설명 그림 · 정상,설명 그림 · 불량'

GUIDE = [
    'K2 협력사 납품가이드 · 사이트 내용', '',
    '이 시트를 고치면 사이트에 바로 반영됩니다(사이트 새로고침). 깃허브 작업은 필요 없습니다.',
    '사이트가 읽으려면 시트가 "링크가 있는 모든 사용자 · 뷰어"로 공유되어 있어야 합니다. 편집 권한은 주지 마세요.', '',
    '자주 하는 수정',
    '· 규칙 제목: [항목] 탭 "문장" 칸',
    '· 전체 규칙 묶음(주제): [항목] 탭 "주제" 칸 — 목록에서 고르거나 새 이름을 직접 입력(새 주제는 맨 뒤에 붙음)',
    '· 패킹 주의사항은 [페이지] 탭 "자동 모음 주제"에 적힌 주제의 기준이 패킹 유형 페이지에서 자동으로 모입니다. 기준을 주의사항에 넣으려면 [항목] 탭 "주제"만 맞추면 됩니다',
    '· 주제 이름·순서: [주제] 탭. 이름을 바꾸면 [항목] 탭의 같은 이름도 Ctrl+H(찾기·바꾸기)로 같이 바꾸세요',
    '· 반송/입고 거부 표시: [항목] 탭 "표시" 칸',
    '· 정상 사진이 없을 때 자동으로 들어가는 설명 그림을 빼려면: [항목] 탭 "설명 그림 안 씀" 칸에 Y',
    '· 이유·안내·대응: [항목] 탭 "이유", "예외·주의", "확인·대응" 칸',
    '· 사진 설명·순서·정상/불량: [사진] 탭 (사진 파일 자체는 깃허브 images 폴더에 있어야 함)',
    '· 센터 주소·입고 가능 복종: [센터] 탭',
    '· 검색 비슷한 말: [검색어] 탭. 한 줄에 같은 뜻으로 찾을 낱말을 쉼표로 나열 (예: 무게, 중량, kg). 한 낱말로 찾으면 같은 줄 낱말도 함께 찾습니다',
    '· 검색창 "자주 묻는 질문": [자주 묻는 질문] 탭. 연결 칸에 항목ID(예: s3b07) 또는 페이지ID(예: rfix)', '',
    '새 규칙 추가',
    '[항목] 탭 맨 아래 줄에 페이지ID·단계·순서·항목ID(새 이름, 예: s5a)·주제·문장을 채웁니다. 사진은 [사진] 탭에 같은 항목ID로 추가.', '',
    '주의',
    '· 탭 이름과 1행 제목은 바꾸지 마세요. 사이트가 이 이름으로 읽습니다.',
    '· 기존 페이지ID·항목ID는 바꾸지 마세요(주소·사진 연결용).',
    '· "같은 내용 가져오기"가 채워진 줄은 내용을 쓰지 않습니다. 원본 항목ID 줄(회색 아닌 줄)을 고치세요.',
    '  같은 항목ID를 넣은 줄은 "같은 규칙을 이 페이지에도 보여주기"라는 뜻입니다.',
    '· 표 칸: 줄바꿈(Alt+Enter)으로 행을, | 로 칸을 나눕니다.',
    '· 시트를 못 읽으면 사이트는 깃허브의 content.json 내용으로 보입니다.',
]


def main():
    M = json.loads((ROOT / 'data' / 'content.json').read_text(encoding='utf-8'))
    items = M['items']
    wb = Workbook()
    s = lambda v: '' if v is None else str(v)
    navy = PatternFill('solid', fgColor='162036')
    key = PatternFill('solid', fgColor='E8ECF3')
    gray = Font(color='9AA1AD')

    def sheet(name, head, rows, widths, wrap=()):
        ws = wb.create_sheet(name)
        ws.append(head)
        for r in rows:
            ws.append([s(v) for v in r])
        for c in ws[1]:
            c.font = Font(bold=True, color='FFFFFF')
            c.fill = navy
        for i, w in enumerate(widths):
            ws.column_dimensions[chr(65 + i)].width = w
        for row in ws.iter_rows(min_row=2, max_row=len(rows) + 300, max_col=len(head)):
            for c in row:
                c.number_format = '@'  # 모두 글자로 저장 (숫자/날짜 자동 변환 방지)
                c.alignment = Alignment(vertical='top', wrap_text=head[c.column - 1] in wrap)
        ws.freeze_panes = 'A2'
        return ws

    def listv(ws, col, formula, last):
        d = DataValidation(type='list', formula1=formula, allow_blank=True, showErrorMessage=False)
        ws.add_data_validation(d)
        d.add(f'{col}2:{col}{last}')

    g = wb.active
    g.title = '읽어주세요'
    for line in GUIDE:
        g.append([line])
    g['A1'].font = Font(bold=True, size=14)
    g.column_dimensions['A'].width = 120
    for r, line in enumerate(GUIDE, 1):
        if line in ('자주 하는 수정', '새 규칙 추가', '주의'):
            g.cell(r, 1).font = Font(bold=True)

    sheet('큰 메뉴', ['순서', '큰 메뉴', '영문 라벨', '첫 화면 설명', '첫 화면 사진'],
          [[i + 1, c['name'], c.get('en'), c.get('desc'), c.get('img')] for i, c in enumerate(M['cats'])],
          [6, 16, 18, 60, 28], ('첫 화면 설명',))
    sheet('페이지', ['순서', '큰 메뉴', '작은 메뉴', '페이지ID', '페이지 제목', '한 줄 설명', '영문 라벨', '모양', '자동 모음 주제'],
          [[i + 1, p['cat'], p.get('sub'), p['id'], p['title'], p.get('desc'), p.get('en'), p.get('layout'), p.get('topic', '')] for i, p in enumerate(M['pages'])],
          [6, 14, 18, 12, 24, 50, 20, 10, 18], ('한 줄 설명',))
    sheet('단계', ['페이지ID', '단계', '단계 제목', '숨김'],
          [[p['id'], st['n'], st['t'], 'Y' if st.get('hide') else ''] for p in M['pages'] for st in p['steps']], [12, 6, 40, 8])

    rows, photos, seen, placed = [], [], set(), []
    for p in M['pages']:
        for st in p['steps']:
            for k, iid in enumerate(st['items']):
                x = items[iid]
                base = [p['id'], st['n'], k + 1, iid]
                if x.get('ref') or iid in seen:  # 다른 항목 내용 사용 / 같은 규칙을 다른 페이지에도 표시
                    rows.append(base + [''] * 11 + [x.get('ref') or iid, '', ''])
                    placed.append(len(rows) + 1)
                    continue
                seen.add(iid)
                rows.append(base + [x.get('topic'), x.get('text'), x.get('tag'), x.get('rid'), x.get('why'), x.get('exc'), x.get('act'),
                                    x.get('source'), '\n'.join(' | '.join(map(s, r)) for r in x.get('table') or []),
                                    'Y' if x.get('nophoto') else '', x.get('todo'), '', 'Y' if x.get('nodraw') else '', 'Y' if x.get('hide') else ''])
                for j, m in enumerate(x.get('media') or []):
                    photos.append([iid, j + 1, m[0], m[1], m[2] if len(m) > 2 else ''])
    head = ['페이지ID', '단계', '순서', '항목ID', '주제', '문장', '표시', '규칙번호', '이유', '예외·주의', '확인·대응', '근거', '표',
            '사진 없이 글로 충분', '필요한 사진', '같은 내용 가져오기', '설명 그림 안 씀', '숨김']
    ws = sheet('항목', head, rows, [10, 6, 6, 9, 18, 46, 10, 10, 40, 40, 40, 24, 30, 10, 24, 14, 12, 8],
               ('문장', '이유', '예외·주의', '확인·대응', '근거', '표', '필요한 사진'))
    ws.freeze_panes = 'G2'
    for r in range(2, len(rows) + 2):
        if r in placed:
            for c in ws[r]:
                c.font = gray
        else:
            ws.cell(r, 5).fill = key
            ws.cell(r, 6).fill = key
    last = len(rows) + 300
    listv(ws, 'E', "'주제'!$B$2:$B$60", last)
    listv(ws, 'G', f'"{TAGS}"', last)
    listv(ws, 'N', '"Y"', last)
    listv(ws, 'Q', '"Y"', last)
    listv(ws, 'R', '"Y"', last)

    sheet('주제', ['순서', '주제'], [[i + 1, t] for i, t in enumerate(M.get('topics', []))], [6, 28])
    ws = sheet('사진', ['항목ID', '순서', '종류', '파일', '설명'], photos, [9, 6, 18, 30, 50], ('설명',))
    listv(ws, 'C', f'"{KINDS}"', len(photos) + 300)
    sheet('검색어', ['같은 뜻 낱말'], [[g] for g in M.get('synonyms', [])], [80])
    ws = sheet('자주 묻는 질문', ['순서', '질문', '연결'], [[i + 1, f['q'], f['to']] for i, f in enumerate(M.get('faq', []))], [6, 50, 14])
    sheet('센터', ['센터ID', '센터 이름', '도로명 주소', '지번 주소', '입고 가능 복종', '지도 링크'],
          [[c['id'], c['name'], c.get('addr'), c.get('jibun'), c.get('kinds'), c.get('map')] for c in M['centers']],
          [10, 16, 36, 36, 36, 40])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f'저장: {OUT}  (항목 줄 {len(rows)}개, 사진 {len(photos)}개)')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print('실패:', e)
        sys.exit(1)
