# -*- coding: utf-8 -*-
import os, sys, json
import urllib.request, urllib.error

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

MALL_ID       = 'ddaytrip89'
API_VERSION   = '2026-03-01'
INJECT_JS_URL = 'https://ddaytrip89.cafe24.com/web/upload/ddaytrip-inject.js'

token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
with open(token_file) as f:
    token = json.load(f)['access_token']

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
        print('  오류 ' + str(e.code) + ': ' + e.read().decode()[:300])
        return None

# 기존 태그 조회
r = api('GET', '/scripttags?shop_no=1')
tags = r.get('scripttags', []) if r else []

# 기존 ddaytrip 태그 삭제
for t in tags:
    if 'ddaytrip-inject' in t.get('src', ''):
        script_no = t.get('script_no') or t.get('no')
        if script_no:
            print('기존 태그 삭제: ' + str(script_no))
            api('DELETE', '/scripttags/' + str(script_no) + '?shop_no=1')
        else:
            # script_no 키 탐색
            for k, v in t.items():
                if v and str(v).replace('.','').isdigit() and k != 'shop_no':
                    print('삭제: ' + k + '=' + str(v))
                    api('DELETE', '/scripttags/' + str(v) + '?shop_no=1')
                    break

# 새로 등록
print('새로 등록 중...')
r = api('POST', '/scripttags', {'request': {
    'shop_no': 1,
    'src': INJECT_JS_URL,
    'display_location': ['all'],
    'load_type': 'body',
}})
if r:
    print('완료: ' + str(r)[:200])
else:
    print('실패')
