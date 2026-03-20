# -*- coding: utf-8 -*-
import os, sys, json, csv, re
import urllib.request, urllib.error

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

MALL_ID     = 'ddaytrip89'
API_VERSION = '2026-03-01'
CONFIG_TAG  = 'ddaytrip-config'
CSV_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product-config.csv')

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

if not os.path.exists(CSV_FILE):
    print('product-config.csv 파일이 없습니다.')
    print('먼저 make-csv.py 를 실행해서 파일을 만들어주세요.')
    sys.exit(1)

with open(CSV_FILE, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print(f'총 {len(rows)}개 상품 설정 적용 시작...')
print()

ok, fail = 0, 0
for row in rows:
    product_no = row.get('상품번호', '').strip()
    if not product_no:
        continue

    min_people = row.get('최소인원', '2인').strip() or '2인'
    transport  = row.get('교통편', '항공 포함').strip() or '항공 포함'
    departure  = (row.get('출발지') or row.get('지') or '인천').strip() or '인천'
    # 출발지옵션 컬럼이 있으면 사용, 없으면 출발지를 / 로 분리해서 자동 생성
    dep_opts_raw = row.get('출발지옵션') or row.get('옵션') or ''
    if dep_opts_raw.strip():
        dep_opts = [o.strip() for o in dep_opts_raw.split('|') if o.strip()]
    else:
        # '인천 / 김해 / 청주' → ['인천 출발', '김해 출발', '청주 출발']
        cities = [c.strip() for c in departure.split('/') if c.strip()]
        dep_opts = [c + ' 출발' for c in cities] if cities else ['인천 출발']
    if not dep_opts:
        dep_opts = ['인천 출발']

    config = {
        'minPeople': min_people,
        'transport': transport,
        'departure': departure,
        'departureOptions': dep_opts,
    }
    config_html = (
        '\n<script type="application/json" id="' + CONFIG_TAG + '">\n'
        + json.dumps(config, ensure_ascii=False, indent=2)
        + '\n</script>\n'
    )

    # 현재 상품 상세 조회
    r = api('GET', f'/products/{product_no}?shop_no=1')
    if not r:
        print(f'  [{product_no}] 조회 실패')
        fail += 1
        continue

    current = r.get('product', {}).get('description', '') or ''
    clean = re.sub(
        r'\s*<script[^>]+id=["\']' + CONFIG_TAG + r'["\'][^>]*>[\s\S]*?</script>\s*',
        '', current
    )
    new_detail = config_html + clean

    r2 = api('PUT', f'/products/{product_no}', {
        'request': {
            'shop_no': 1,
            'product_no': int(product_no),
            'description': new_detail,
        }
    })
    if r2:
        print(f'  [{product_no}] {row.get("상품명","")[:30]} → 완료')
        ok += 1
    else:
        print(f'  [{product_no}] 저장 실패')
        fail += 1

print()
print(f'완료: {ok}개 성공 / {fail}개 실패')
