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
INJECT_JS_URL = 'https://ddaytrip89.cafe24.com/web/upload/ddaytrip-inject.js'

# scripttag 스코프로 시도
SCOPES = 'mall.read_application,mall.write_application'

def get_token(code):
    cred = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(
        f'https://{MALL_ID}.cafe24api.com/api/v2/oauth/token',
        data=data, method='POST',
        headers={
            'Authorization': f'Basic {cred}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('  토큰 오류: ' + e.read().decode())
        sys.exit(1)

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
        print('  오류 ' + str(e.code) + ': ' + e.read().decode()[:400])
        return None

auth_url = (
    f'https://{MALL_ID}.cafe24api.com/api/v2/oauth/authorize'
    f'?response_type=code'
    f'&client_id={CLIENT_ID}'
    f'&redirect_uri={urllib.parse.quote(REDIRECT_URI)}'
    f'&scope={urllib.parse.quote(SCOPES)}'
    f'&state=ddaytrip'
)

print()
print('아래 URL을 브라우저에서 열어주세요:')
print()
print(auth_url)
print()
print('로그인 -> 동의 -> example.com 주소창 URL 복사 -> 붙여넣기')
print()

try:
    webbrowser.open(auth_url)
except:
    pass

redirected_url = input('URL: ').strip()
params = urllib.parse.parse_qs(urllib.parse.urlparse(redirected_url).query)
code = params.get('code', [None])[0]

if not code:
    print('code를 찾을 수 없습니다.')
    sys.exit(1)

print('토큰 발급 중...')
token_resp = get_token(code)
token = token_resp.get('access_token')
if not token:
    print('토큰 실패: ' + str(token_resp))
    sys.exit(1)

# 토큰 저장
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json'), 'w') as f:
    json.dump(token_resp, f)
print('토큰 OK')

print()
print('=== 기존 Script Tags 확인 ===')
r = api('GET', '/scripttags?shop_no=1', token)
if r:
    tags = r.get('scripttags', [])
    print('기존 태그 수: ' + str(len(tags)))
    for t in tags:
        print('  no=' + str(t.get('no')) + ' src=' + str(t.get('src')))
        if INJECT_JS_URL in str(t.get('src', '')):
            print('  -> 기존 태그 삭제 중...')
            api('DELETE', '/scripttags/' + str(t['no']) + '?shop_no=1', token)
            print('  삭제 완료')

print()
print('=== Script Tag 등록 ===')
# display_location 없이 먼저 시도
r = api('POST', '/scripttags', token, {
    'request': {
        'shop_no': 1,
        'src': INJECT_JS_URL,
        'load_type': 'body',
    }
})
if not r:
    print('load_type body 실패, head로 재시도...')
    r = api('POST', '/scripttags', token, {
        'request': {
            'shop_no': 1,
            'src': INJECT_JS_URL,
            'load_type': 'head',
        }
    })
if r:
    tag = r.get('scripttag', r)
    print()
    print('============================================')
    print('  Script Tag 등록 완료!')
    print('  no: ' + str(tag.get('no', '?')))
    print('  https://d-daytrip.co.kr/reservation/')
    print('  detail.html?product_no=133 확인해주세요')
    print('============================================')
