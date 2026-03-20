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

print('=== 등록된 Script Tags ===')
r = api('GET', '/scripttags?shop_no=1')
if not r:
    print('조회 실패')
    sys.exit(1)

tags = r.get('scripttags', [])
print('총 ' + str(len(tags)) + '개')
for t in tags:
    print('  no=' + str(t.get('no')) + ' src=' + str(t.get('src', '')))

ddaytrip_tags = [t for t in tags if 'ddaytrip-inject' in t.get('src', '')]
if not ddaytrip_tags:
    print('ddaytrip-inject 태그 없음')
    sys.exit(0)

for t in ddaytrip_tags:
    print('태그 전체 데이터: ' + str(t))
    no = t.get('no') or t.get('script_no') or t.get('id')
    if not no:
        # 키 이름 중 숫자값 찾기
        for k, v in t.items():
            if v and str(v).isdigit():
                no = v
                print('키 발견: ' + k + '=' + str(v))
                break
    if not no:
        print('삭제 키를 찾지 못했습니다. 위 데이터를 확인하세요.')
        continue
    print('삭제 중: ' + str(no))
    api('DELETE', '/scripttags/' + str(no) + '?shop_no=1')
    print('삭제 완료')

print()
print('롤백 완료. 원래 페이지로 복구됐습니다.')
