import json, base64, urllib.parse, urllib.request, urllib.error, os, sys

CLIENT_ID     = 'i08G1x34A1cjbUHfGHsmnH'
CLIENT_SECRET = 'eVwnzk01ACFBfcmkuGwokI'
MALL_ID       = 'ddaytrip89'
REDIRECT_URI  = 'https://example.com/callback'
API_VERSION   = '2024-06-01'

SCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cafe24', 'ddaytrip-detail.html')
MARKER     = '<!-- ddaytrip-detail-inject -->'
END_MARKER = '<!-- /ddaytrip-detail-inject -->'

# 저장된 토큰 읽기
token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
if os.path.exists(token_file):
    with open(token_file) as f:
        token = json.load(f)['access_token']
    print('저장된 토큰 사용: ' + token[:15] + '...')
else:
    print('token.json 없음. run.py 먼저 실행하세요.')
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
        return {'_err': e.code, '_msg': e.read().decode()[:500]}

print('')
print('=== API 탐색 (shop_no=1 포함) ===')
for ep in [
    '/scripttags?shop_no=1',
    '/shops',
    '/shops?shop_no=1',
    '/designs?shop_no=1',
    '/store?shop_no=1',
    '/themes?shop_no=1',
]:
    r = api('GET', ep)
    if '_err' in r:
        print('  ' + str(r['_err']) + ' ' + ep)
        if r['_err'] != 404:
            print('       ' + r['_msg'][:150])
    else:
        print('  OK  ' + ep + ' -> ' + str(list(r.keys())))

# scripttags 상세 오류 확인
print('')
print('=== scripttags 상세 오류 ===')
r = api('GET', '/scripttags')
print(r.get('_msg', str(r))[:300])

# scripttags POST 시도 (인젝션 코드 로드)
print('')
print('=== Script Tags POST 시도 ===')

with open(SCRIPT_FILE, 'r', encoding='utf-8') as f:
    script_content = f.read()

# CSS+JS를 JS로 변환해서 주입하는 부트스트랩 스크립트
bootstrap_js = """
(function(){
  var s = document.createElement('script');
  s.src = 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js';
  document.head.appendChild(s);
  var l = document.createElement('link');
  l.rel = 'stylesheet';
  l.href = 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css';
  document.head.appendChild(l);
})();
"""

r = api('POST', '/scripttags', {
    'request': {
        'shop_no': 1,
        'src': 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js',
        'display_location': ['all_pages'],
        'load_type': 'head'
    }
})
print('POST 결과: ' + str(r)[:300])
