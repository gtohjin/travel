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

SCOPES = 'mall.read_application,mall.write_application,mall.read_product,mall.write_product'

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
        print('토큰 오류: ' + e.read().decode())
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
        print('  오류 ' + str(e.code) + ': ' + e.read().decode()[:300])
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

token_resp = get_token(code)
token = token_resp.get('access_token')
if not token:
    print('토큰 실패: ' + str(token_resp))
    sys.exit(1)

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json'), 'w') as f:
    json.dump(token_resp, f)
print('토큰 저장 완료')

# 예약 상품 목록 조회 테스트
print()
print('=== 예약 상품 목록 ===')
r = api('GET', '/products?product_type=R&limit=50', token)
if r:
    prods = r.get('products', [])
    print('상품 수: ' + str(len(prods)))
    for p in prods:
        print('  no=' + str(p.get('product_no')) + ' name=' + str(p.get('product_name', ''))[:40])
else:
    print('조회 실패 - 일반 상품으로 재시도')
    r = api('GET', '/products?limit=50', token)
    if r:
        prods = r.get('products', [])
        print('상품 수: ' + str(len(prods)))
        for p in prods:
            print('  no=' + str(p.get('product_no')) + ' name=' + str(p.get('product_name', ''))[:40])
