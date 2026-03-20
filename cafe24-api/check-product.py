# -*- coding: utf-8 -*-
import os, sys, json
import urllib.request, urllib.error

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

MALL_ID     = 'ddaytrip89'
API_VERSION = '2026-03-01'

token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
with open(token_file) as f:
    token = json.load(f)['access_token']

def api(endpoint):
    url = f'https://{MALL_ID}.cafe24api.com/api/v2/admin{endpoint}'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': API_VERSION,
    })
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('오류 ' + str(e.code) + ': ' + e.read().decode()[:300])
        return None

r = api('/products/133?shop_no=1')
product = r.get('product', {}) if r else {}

# description 필드에 ddaytrip-config 있는지 확인
desc = product.get('description', '') or ''
detail = product.get('detail_image_html', '') or ''
mobile = product.get('mobile_description', '') or ''

print('=== description 필드 ===')
print('ddaytrip-config 포함:', 'ddaytrip-config' in desc)
print('내용 앞 200자:', desc[:200])
print()
print('=== detail_image_html 필드 ===')
print('ddaytrip-config 포함:', 'ddaytrip-config' in detail)
print('내용 앞 200자:', detail[:200])
print()
print('=== 사용 가능한 필드 목록 ===')
for k, v in product.items():
    if isinstance(v, str) and len(v) > 10:
        print(f'  {k}: {v[:80]}')
    elif v and not isinstance(v, str):
        print(f'  {k}: {str(v)[:60]}')
