# -*- coding: utf-8 -*-
import os, sys, json, base64, webbrowser
import urllib.parse, urllib.request, urllib.error

# Windows 터미널 UTF-8 출력 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ============================================================
# 설정
# ============================================================
CLIENT_ID     = 'i08G1x34A1cjbUHfGHsmnH'
CLIENT_SECRET = 'eVwnzk01ACFBfcmkuGwokI'
MALL_ID       = 'ddaytrip89'
REDIRECT_URI  = 'https://example.com/callback'
SCOPES        = 'mall.read_design,mall.write_design'
# ============================================================

SCRIPT_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cafe24', 'ddaytrip-detail.html')
INJECT_MARKER = '<!-- ddaytrip-detail-inject -->'
END_MARKER    = '<!-- /ddaytrip-detail-inject -->'
API_VERSION   = '2024-06-01'

# ─────────────────────────────────────────
# API 헬퍼
# ─────────────────────────────────────────
def api(method, endpoint, token, data=None):
    url = f'https://{MALL_ID}.cafe24api.com/api/v2/admin{endpoint}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': API_VERSION,
    }
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')
        print(f'    API 오류 [{method} {endpoint}] {e.code}: {err[:300]}')
        return None

def get_token(code):
    cred = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
    url  = f'https://{MALL_ID}.cafe24api.com/api/v2/oauth/token'
    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST', headers={
        'Authorization': f'Basic {cred}',
        'Content-Type': 'application/x-www-form-urlencoded',
    })
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f'    토큰 오류: {e.read().decode()}')
        sys.exit(1)

# ─────────────────────────────────────────
# 디자인 파일 API
# ─────────────────────────────────────────
def get_active_skin(token):
    result = api('GET', '/designs?limit=100', token)
    if not result:
        return None
    designs = result.get('designs', [])
    for d in designs:
        if d.get('is_represent') == 'T':
            return d.get('skin_no')
    return designs[0]['skin_no'] if designs else None

def list_design_files(token, skin_no):
    result = api('GET', f'/designs/{skin_no}/files?limit=500', token)
    return result.get('files', []) if result else []

def read_design_file(token, skin_no, path):
    encoded = urllib.parse.quote(path, safe='')
    result = api('GET', f'/designs/{skin_no}/files?path={encoded}', token)
    if result and 'files' in result and result['files']:
        return result['files'][0].get('content', '')
    return None

def write_design_file(token, skin_no, path, content):
    data = {'request': {'path': path, 'content': content}}
    result = api('PUT', f'/designs/{skin_no}/files', token, data)
    return result is not None

def find_layout_file(files):
    candidates = [
        'html/layout/basic.html',
        'html/layout/layout.html',
        'html/layout/default.html',
        'layout/basic.html',
        'basic.html',
        'head.html',
        'html/head.html',
    ]
    file_paths = {f['path'] for f in files}
    for c in candidates:
        if c in file_paths:
            return c
    for f in files:
        p = f.get('path', '')
        if p.endswith('.html') and ('layout' in p.lower() or 'basic' in p.lower()):
            return p
    return None

# ─────────────────────────────────────────
# 인젝션 코드 준비
# ─────────────────────────────────────────
def load_injection_code():
    path = os.path.abspath(SCRIPT_FILE)
    if not os.path.exists(path):
        print(f'    오류: 파일 없음: {path}')
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return f'\n{INJECT_MARKER}\n{content}\n{END_MARKER}\n'

def inject_into_html(html_content, injection_code):
    # 기존 인젝션 제거 후 교체
    if INJECT_MARKER in html_content:
        start = html_content.find(INJECT_MARKER)
        end   = html_content.find(END_MARKER)
        if end != -1:
            html_content = html_content[:start] + html_content[end + len(END_MARKER):]
            print('    기존 인젝션 코드 제거됨')

    # </head> 앞에 삽입
    for tag in ['</head>', '</HEAD>']:
        if tag in html_content:
            return html_content.replace(tag, injection_code + tag, 1)

    return injection_code + html_content

# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    print()
    print('=' * 56)
    print('  ddaytrip - Cafe24 Design API 자동 주입')
    print('=' * 56)

    # 인젝션 코드 로드
    injection_code = load_injection_code()
    print(f'\n  [OK] 인젝션 코드 로드 완료 ({len(injection_code):,} bytes)')

    # OAuth2 인증 URL
    auth_url = (
        f'https://{MALL_ID}.cafe24api.com/api/v2/oauth/authorize'
        f'?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={urllib.parse.quote(REDIRECT_URI)}'
        f'&scope={urllib.parse.quote(SCOPES)}'
        f'&state=ddaytrip'
    )

    print(f"""
  ─────────────────────────────────────────────
  [1] 아래 URL을 브라우저에서 열어주세요
      (자동으로 열립니다)

  {auth_url}

  [2] 카페24 로그인 후 [동의] 클릭
  [3] example.com 페이지로 이동됩니다
      (페이지 오류 무시 - 주소창 URL만 복사)
  [4] 주소창 URL 전체를 아래에 붙여넣기
  ─────────────────────────────────────────────
""")
    webbrowser.open(auth_url)

    redirected_url = input('  리디렉션 URL 붙여넣기: ').strip()
    params = urllib.parse.parse_qs(urllib.parse.urlparse(redirected_url).query)
    code = params.get('code', [None])[0]

    if not code:
        print('\n  [오류] URL에서 code 를 찾을 수 없습니다.')
        print('  예: https://example.com/callback?code=AbCdEf12&state=ddaytrip')
        sys.exit(1)

    print('  [OK] 인증 코드 추출 완료')

    # 토큰 발급
    print('  토큰 발급 중...')
    token_resp = get_token(code)
    token = token_resp.get('access_token')
    if not token:
        print('  [오류] 토큰 발급 실패:', token_resp)
        sys.exit(1)
    print('  [OK] 토큰 발급 완료')

    # 활성 스킨
    print('\n  활성 디자인 스킨 확인 중...')
    skin_no = get_active_skin(token)
    if not skin_no:
        print('  [오류] 활성 스킨을 찾을 수 없습니다.')
        sys.exit(1)
    print(f'  [OK] 스킨 번호: {skin_no}')

    # 파일 목록
    print('  디자인 파일 목록 조회 중...')
    files = list_design_files(token, skin_no)
    print(f'  [OK] 파일 {len(files)}개 확인')

    # 레이아웃 파일 탐색
    layout_path = find_layout_file(files)

    if not layout_path:
        print('\n  [주의] 레이아웃 파일을 자동으로 찾지 못했습니다.')
        print('  HTML 파일 목록:')
        for f in files:
            if f.get('path', '').endswith('.html'):
                print(f"    - {f['path']}")
        layout_path = input('\n  파일 경로 직접 입력 (예: html/layout/basic.html): ').strip()

    print(f'\n  레이아웃 파일: {layout_path}')

    # 파일 읽기
    print('  파일 읽는 중...')
    html_content = read_design_file(token, skin_no, layout_path)
    if html_content is None:
        print('  [오류] 파일 읽기 실패')
        sys.exit(1)
    print(f'  [OK] 파일 읽기 완료 ({len(html_content):,} bytes)')

    if INJECT_MARKER in html_content:
        print('  [정보] 기존 인젝션 발견 - 최신 버전으로 교체합니다')

    # 코드 삽입
    new_content = inject_into_html(html_content, injection_code)
    print(f'  [OK] 코드 삽입 완료 ({len(new_content):,} bytes)')

    # 저장
    print('  저장 중...')
    success = write_design_file(token, skin_no, layout_path, new_content)

    if success:
        print("""
  ============================================
    적용 완료!

    아래 URL에서 결과 확인:
    https://d-daytrip.co.kr/reservation/
    detail.html?product_no=133
  ============================================
""")
    else:
        print('\n  [오류] 저장 실패. mall.write_design 권한을 확인해주세요.')
        sys.exit(1)

if __name__ == '__main__':
    main()
