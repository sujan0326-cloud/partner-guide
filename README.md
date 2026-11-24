# K2 협력사 납품가이드

여주 물류센터 협력사용 납품 기준 사이트입니다.

## 바로 보기
- 웹: GitHub Pages 주소 (Settings → Pages → Source: GitHub Actions)
- 파일 하나로 전달: `python build.py --single` → `dist/K2_협력사_납품가이드.html`

## 고치는 법
| 하고 싶은 것 | 고칠 곳 |
|---|---|
| 문구·메뉴 | `data/content.json` (또는 구글 시트) |
| 사진 교체 | `images/` 같은 이름으로 덮어쓰기 (목록: `IMAGES.md`) |
| 디자인·기능 | `template.html` |

고친 뒤 `python build.py` (외부 패키지 필요 없음, Python 3.9+). main에 push하면 자동 배포됩니다.

AI로 수정할 때는 먼저 `AGENTS.md`를 읽게 하세요.
