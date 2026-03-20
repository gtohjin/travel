# -*- coding: utf-8 -*-
# 카페24 상품 목록을 CSV로 내보내기 (엑셀에서 편집 후 apply-configs.py 실행)
import os, sys, json, csv
import urllib.request, urllib.error

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

MALL_ID     = 'ddaytrip89'
API_VERSION = '2026-03-01'
CSV_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product-config.csv')

token_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
with open(token_file) as f:
    token = json.load(f)['access_token']

def api(method, endpoint):
    url = f'https://{MALL_ID}.cafe24api.com/api/v2/admin{endpoint}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-Cafe24-Api-Version': API_VERSION,
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('오류 ' + str(e.code))
        return None

print('상품 목록 조회 중...')
all_products = []
offset = 0
while True:
    r = api('GET', f'/products?limit=100&offset={offset}')
    if not r:
        break
    prods = r.get('products', [])
    if not prods:
        break
    all_products.extend(prods)
    if len(prods) < 100:
        break
    offset += 100

# 개인결제창 제외
filtered = [p for p in all_products if '개인결제' not in p.get('product_name', '')]
print(f'상품 {len(filtered)}개 (개인결제창 제외)')

def guess_config(name):
    name_lower = name.lower()
    # 출발지 자동 감지
    if '부산출발' in name or '부산 출발' in name or '김해' in name:
        departure = '김해'
        dep_opts  = '김해 출발'
    elif '청주출발' in name or '청주 출발' in name:
        departure = '청주'
        dep_opts  = '청주 출발|인천 출발'
    elif '대구출발' in name or '대구 출발' in name:
        departure = '대구'
        dep_opts  = '대구 출발|인천 출발'
    else:
        departure = '인천'
        dep_opts  = '인천 출발|김해 출발'
    return departure, dep_opts

with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['상품번호', '상품명', '최소인원', '교통편', '출발지', '출발지옵션'])
    writer.writeheader()
    for p in filtered:
        name = p.get('product_name', '')
        departure, dep_opts = guess_config(name)
        writer.writerow({
            '상품번호': p.get('product_no', ''),
            '상품명': name,
            '최소인원': '2인',
            '교통편': '항공 포함',
            '출발지': departure,
            '출발지옵션': dep_opts,
        })

print(f'저장 완료: {CSV_FILE}')
print()
print('엑셀로 열어서 각 상품의 값을 수정한 후')
print('python apply-configs.py 실행하면 일괄 적용됩니다.')
print()
print('출발지옵션은 | 로 구분하세요. 예: 인천 출발|김해 출발|대구 출발')
