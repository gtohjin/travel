import json, base64, urllib.parse, urllib.request, urllib.error, os, sys

CLIENT_ID     = 'i08G1x34A1cjbUHfGHsmnH'
CLIENT_SECRET = 'eVwnzk01ACFBfcmkuGwokI'
MALL_ID       = 'ddaytrip89'
REDIRECT_URI  = 'https://example.com/callback'
API_VERSION   = '2024-06-01'

SCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cafe24', 'ddaytrip-detail.html')
MARKER      = '<!-- ddaytrip-detail-inject -->'
END_MARKER  = '<!-- /ddaytrip-detail-inject -->'

AUTH_URL = (
    'https://' + MALL_ID + '.cafe24api.com/api/v2/oauth/authorize'
    '?response_type=code'
    '&client_id=' + CLIENT_ID +
    '&redirect_uri=' + urllib.parse.quote(REDIRECT_URI) +
    '&scope=mall.read_design%2Cmall.write_design'
    '&state=ddaytrip'
)

print('')
print('==============================================')
print('  ddaytrip Cafe24 Design Inject')
print('==============================================')
print('')
print('[Step 1] 아래 URL을 브라우저에 복사해서 열기:')
print('')
print(AUTH_URL)
print('')
print('[Step 2] 카페24 로그인 -> 동의 클릭')
print('[Step 3] example.com 주소창 URL 전체 복사')
print('[Step 4] 아래에 붙여넣기 후 엔터')
print('')

try:
    redirected = raw_input('URL: ')
except NameError:
    redirected = input('URL: ')

redirected = redirected.strip()
params = urllib.parse.parse_qs(urllib.parse.urlparse(redirected).query)
code = params.get('code', [None])[0]

if not code:
    print('ERROR: code 를 찾을 수 없습니다.')
    sys.exit(1)

print('code: ' + code[:10] + '...')

# 토큰 발급
print('토큰 발급 중...')
cred = base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode()).decode()
req = urllib.request.Request(
    'https://' + MALL_ID + '.cafe24api.com/api/v2/oauth/token',
    data=urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }).encode(),
    method='POST',
    headers={
        'Authorization': 'Basic ' + cred,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
)
try:
    with urllib.request.urlopen(req) as r:
        token_data = json.loads(r.read().decode())
        token = token_data['access_token']
        print('토큰 OK: ' + token[:15] + '...')
        with open('token.json', 'w') as f:
            json.dump(token_data, f)
except urllib.error.HTTPError as e:
    print('토큰 오류: ' + e.read().decode())
    sys.exit(1)

def api(method, endpoint, data=None):
    url = 'https://' + MALL_ID + '.cafe24api.com/api/v2/admin' + endpoint
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': API_VERSION,
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {'_err': e.code, '_msg': e.read().decode()[:300]}

# 사용 가능한 API 탐색
print('')
print('API 탐색...')
for ep in ['/designs', '/scripttags', '/shops/1', '/themes', '/store']:
    r = api('GET', ep)
    if '_err' in r:
        print('  ' + str(r['_err']) + ' ' + ep)
    else:
        print('  OK ' + ep + ' -> ' + str(list(r.keys())))

print('')
print('완료. 위 결과를 Claude 에게 알려주세요.')
