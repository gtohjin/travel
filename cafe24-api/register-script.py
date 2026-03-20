# -*- coding: utf-8 -*-
import os, sys, json, base64, webbrowser
import urllib.parse, urllib.request, urllib.error

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CLIENT_ID     = 'i08G1x34A1cjbUHfGHsmnH'
CLIENT_SECRET = 'eVwnzk01ACFBfcmkuGwokI'
MALL_ID       = 'ddaytrip89'
REDIRECT_URI  = 'https://example.com/callback'
API_VERSION   = '2026-03-01'
SCOPES        = 'mall.read_design,mall.write_design,mall.read_script,mall.write_script'

INJECT_JS_URL = 'https://ddaytrip89.cafe24.com/web/upload/ddaytrip-inject.js'

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
        print(f'    API 오류 [{method} {endpoint}] {e.code}: {err[:400]}')
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
        print(f'    Token error: {e.read().decode()}')
        sys.exit(1)

def main():
    print()
    print('=' * 56)
    print('  ddaytrip - Script Tags 등록')
    print('=' * 56)

    auth_url = (
        f'https://{MALL_ID}.cafe24api.com/api/v2/oauth/authorize'
        f'?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={urllib.parse.quote(REDIRECT_URI)}'
        f'&scope={urllib.parse.quote(SCOPES)}'
        f'&state=ddaytrip'
    )

    print()
    print('  [1] 아래 URL을 브라우저에서 열어주세요:')
    print()
    print(f'  {auth_url}')
    print()
    print('  [2] 카페24 로그인 -> 동의 클릭')
    print('  [3] example.com 주소창 URL 전체 복사')
    print('  [4] 아래에 붙여넣기')
    print()

    try:
        webbrowser.open(auth_url)
    except:
        pass

    redirected_url = input('  리디렉션 URL: ').strip()
    params = urllib.parse.parse_qs(urllib.parse.urlparse(redirected_url).query)
    code = params.get('code', [None])[0]

    if not code:
        print('  [오류] URL에서 code를 찾을 수 없습니다.')
        sys.exit(1)

    print('  [OK] 인증 코드 추출')

    token_resp = get_token(code)
    token = token_resp.get('access_token')
    if not token:
        print('  [오류] 토큰 발급 실패:', token_resp)
        sys.exit(1)
    print('  [OK] 토큰 발급 완료')

    # 기존 스크립트 태그 확인
    print()
    print('  기존 Script Tags 확인 중...')
    existing = api('GET', '/scripttags?shop_no=1', token)
    if existing:
        tags = existing.get('scripttags', [])
        print(f'  기존 태그 수: {len(tags)}')
        for t in tags:
            print(f'    no={t.get("no")} src={t.get("src")}')

        # 같은 URL이 이미 있으면 삭제
        for t in tags:
            if INJECT_JS_URL in t.get('src', ''):
                no = t.get('no')
                print(f'  기존 동일 태그 삭제 중 (no={no})...')
                api('DELETE', f'/scripttags/{no}?shop_no=1', token)
                print('  [OK] 삭제 완료')

    # Script Tag 등록
    print()
    print(f'  Script Tag 등록 중...')
    print(f'  URL: {INJECT_JS_URL}')
    result = api('POST', '/scripttags', token, {
        'request': {
            'shop_no': 1,
            'src': INJECT_JS_URL,
            'display_location': ['all_pages'],
            'load_type': 'body',
        }
    })

    if result:
        tag = result.get('scripttag', result)
        print()
        print('  ============================================')
        print('    Script Tag 등록 완료!')
        print(f'    no: {tag.get("no", "?")}')
        print(f'    src: {tag.get("src", INJECT_JS_URL)}')
        print()
        print('    아래 URL에서 확인:')
        print('    https://d-daytrip.co.kr/reservation/')
        print('    detail.html?product_no=133')
        print('  ============================================')
    else:
        print()
        print('  [오류] 등록 실패.')
        print('  카페24 개발자 센터에서 앱 권한에')
        print('  mall.read_script / mall.write_script 가 있는지 확인하세요.')

if __name__ == '__main__':
    main()
