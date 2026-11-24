"""K2 협력사 납품가이드 빌드 스크립트

사용법
  python build.py            -> index.html 생성 (사진은 images/ 폴더를 참조, GitHub Pages용)
  python build.py --single   -> dist/K2_협력사_납품가이드.html 생성 (사진까지 한 파일에 포함, 메일·메신저 전달용)

수정 위치
  - 화면 디자인·동작 : template.html
  - 기준 문구·메뉴·사진 연결 : data/content.json
  - 사진 파일 : images/  (같은 이름으로 바꿔 넣으면 됨, 목록은 IMAGES.md)
"""
import base64
import json
import logging
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHEET_ID = '1hsSNc5iBJeCsj9Mdn8Vs0wCJmt4wxNxQpPsxU8csOZg'  # K2 협력사 납품가이드 · 사이트 내용 (사이트 연결)
log = logging.getLogger('build')


def data_uri(path: Path) -> str:
    mt = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    if path.suffix == '.woff2':
        mt = 'font/woff2'
    if path.suffix == '.webp':
        mt = 'image/webp'
    return f'data:{mt};base64,' + base64.b64encode(path.read_bytes()).decode()


def build(single: bool) -> Path:
    model = json.loads((ROOT / 'data' / 'content.json').read_text(encoding='utf-8'))
    images = sorted(p for p in (ROOT / 'images').iterdir() if p.is_file())

    # 사이트가 참조하는 이미지 이름 -> 경로(또는 data URI)
    imgf = {p.name: (data_uri(p) if single else f'images/{p.name}') for p in images}

    # 사진 연결이 끊긴 항목 점검 (빌드는 계속하고 경고만)
    missing = sorted({m[1] for it in model['items'].values() if 'ref' not in it for m in it.get('media', []) if m[1] not in imgf})
    for name in missing:
        log.warning('images/ 에 없는 사진: %s', name)

    if single:  # 단계 그림(SVG) 안의 images/ 참조도 한 파일로
        for page in model['pages']:
            for step in page['steps']:
                step['art'] = re.sub(r'images/([\w.\-]+)', lambda m: imgf.get(m.group(1), m.group(0)), step.get('art', ''))

    tpl = (ROOT / 'template.html').read_text(encoding='utf-8')
    font = data_uri(ROOT / 'assets' / 'pt-sub.woff2') if single else 'assets/pt-sub.woff2'
    logo_d = data_uri(ROOT / 'assets' / 'logo_dark.png') if single else 'assets/logo_dark.png'
    logo_w = data_uri(ROOT / 'assets' / 'logo_white.png') if single else 'assets/logo_white.png'
    html = (tpl.replace('__MODEL__', json.dumps(model, ensure_ascii=False))
               .replace('__IMGF__', json.dumps(imgf, ensure_ascii=False))
               .replace('__SHEET_ID__', SHEET_ID)
               .replace('__PTFONT__', font)
               .replace('__LOGO_D__', logo_d)
               .replace('__LOGO_W__', logo_w))
    for ph in ('__MODEL__', '__IMGF__', '__SHEET_ID__', '__PTFONT__', '__LOGO_D__', '__LOGO_W__'):
        if ph in html:
            raise RuntimeError(f'치환되지 않은 자리표시자: {ph}')

    out = ROOT / 'dist' / 'K2_협력사_납품가이드.html' if single else ROOT / 'index.html'
    out.parent.mkdir(exist_ok=True)
    tmp = out.with_suffix('.tmp')
    tmp.write_text(html, encoding='utf-8')
    tmp.replace(out)  # 중간에 실패해도 기존 파일이 깨지지 않게
    log.info('%s  %.2f MB  (사진 %d개, 끊긴 연결 %d개)', out.relative_to(ROOT), out.stat().st_size / 1e6, len(images), len(missing))
    return out


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    try:
        build(single='--single' in sys.argv)
    except Exception:
        log.exception('빌드 실패')
        sys.exit(1)
