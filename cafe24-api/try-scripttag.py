# -*- coding: utf-8 -*-
import os, sys, json
import urllib.request, urllib.error

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CLIENT_ID     = 'i08G1x34A1cjbUHfGHsmnH'
MALL_ID       = 'ddaytrip89'
API_VERSION   = '2026-03-01'
INJECT_JS_URL = 'https://ddaytrip89.cafe24.com/web/upload/ddaytrip-inject.js'

token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
with open(token_file) as f:
    token = json.load(f)['access_token']
print('토큰: ' + token[:15] + '...')

def api(method, endpoint, data=None):
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
        print(f'  오류 {e.code}: {err[:400]}')
        return None

print()
print('=== 기존 Script Tags 확인 ===')
r = api('GET', '/scripttags?shop_no=1')
print(str(r)[:300])

print()
print('=== Script Tag 등록 시도 ===')
r = api('POST', '/scripttags', {
    'request': {
        'shop_no': 1,
        'src': INJECT_JS_URL,
        'display_location': ['all_pages'],
        'load_type': 'body',
    }
})
print(str(r)[:400])
