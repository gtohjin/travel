# -*- coding: utf-8 -*-
import os, sys, json
import urllib.request, urllib.error

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

MALL_ID     = 'ddaytrip89'
API_VERSION = '2026-03-01'
CONFIG_TAG  = 'ddaytrip-config'

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
        print('  오류 ' + str(e.code) + ': ' + e.read().decode()[:400])
        return None

print()
print('=' * 50)
print('  디데이트립 - 상품 설정 관리')
print('=' * 50)

# 상품 목록 조회
print('\n상품 목록 조회 중...')
r = api('GET', '/products?limit=100&product_type=R')
products = r.get('products', []) if r else []
if not products:
    r = api('GET', '/products?limit=100')
    products = r.get('products', []) if r else []

print(f'\n상품 목록:')
for p in products:
    no = p.get('product_no')
    name = p.get('product_name', '')[:50]
    print(f'  [{no}] {name}')

print()
product_no = input('설정할 상품번호 입력: ').strip()

# 현재 상품 상세 조회
r = api('GET', f'/products/{product_no}?shop_no=1')
if not r:
    print('상품 조회 실패')
    sys.exit(1)

product = r.get('product', {})
current_detail = product.get('detail_image_html', '') or product.get('description', '') or ''
print(f'\n현재 상품: {product.get("product_name", "")}')

print()
print('설정값 입력 (엔터 = 기본값 유지)')

min_people = input('최소인원 (예: 2인): ').strip() or '2인'
transport  = input('교통편 (예: 항공 포함): ').strip() or '항공 포함'
departure  = input('출발지 표시 (예: 인천 / 김해): ').strip() or '인천'

print('출발지 옵션 입력 (쉼표로 구분, 예: 인천 출발,김해 출발,대구 출발)')
dep_opts_str = input('출발지 옵션: ').strip()
dep_opts = [o.strip() for o in dep_opts_str.split(',') if o.strip()] or ['인천 출발']

config = {
    'minPeople': min_people,
    'transport': transport,
    'departure': departure,
    'departureOptions': dep_opts,
}

config_html = (
    f'\n<script type="application/json" id="{CONFIG_TAG}">\n'
    + json.dumps(config, ensure_ascii=False, indent=2)
    + f'\n</script>\n'
)

# 기존 config 태그 제거 후 새로 추가
import re
clean_detail = re.sub(
    r'\s*<script[^>]+id=["\']' + CONFIG_TAG + r'["\'][^>]*>[\s\S]*?</script>\s*',
    '',
    current_detail
)
new_detail = config_html + clean_detail

print()
print('저장 중...')
r = api('PUT', f'/products/{product_no}', {
    'request': {
        'shop_no': 1,
        'product_no': int(product_no),
        'description': new_detail,
    }
})

if r:
    print()
    print('=' * 50)
    print(f'  상품 [{product_no}] 설정 저장 완료!')
    print(f'  최소인원: {min_people}')
    print(f'  교통편: {transport}')
    print(f'  출발지: {departure}')
    print(f'  옵션: {dep_opts}')
    print('=' * 50)
else:
    print('저장 실패')
