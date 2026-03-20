import json, base64, urllib.parse, urllib.request, urllib.error, os, sys

CLIENT_ID     = 'i08G1x34A1cjbUHfGHsmnH'
CLIENT_SECRET = 'eVwnzk01ACFBfcmkuGwokI'
MALL_ID       = 'ddaytrip89'
REDIRECT_URI  = 'https://example.com/callback'
API_VERSION   = '2026-03-01'   # 수정됨

SCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cafe24', 'ddaytrip-detail.html')
MARKER     = '<!-- ddaytrip-detail-inject -->'
END_MARKER = '<!-- /ddaytrip-detail-inject -->'

# 저장된 토큰 읽기
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')) as f:
    token = json.load(f)['access_token']
print('토큰: ' + token[:15] + '...')

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
print('=== 스킨 목록 조회 ===')
r = api('GET', '/designs?shop_no=1')
if '_err' in r:
    print('오류: ' + r['_msg'])
    sys.exit(1)

designs = r.get('designs', [])
print('디자인 수: ' + str(len(designs)))
skin_no = None
for d in designs:
    rep = d.get('is_represent','')
    print('  skin_no=' + str(d.get('skin_no')) + ' name=' + str(d.get('skin_name')) + ' represent=' + rep)
    if rep == 'T':
        skin_no = d.get('skin_no')

if not skin_no and designs:
    skin_no = designs[0]['skin_no']

print('사용 스킨: ' + str(skin_no))

print('')
print('=== 디자인 파일 목록 ===')
r = api('GET', '/designs/' + str(skin_no) + '/files?shop_no=1&limit=200')
if '_err' in r:
    print('오류: ' + r['_msg'])
    sys.exit(1)

files = r.get('files', [])
print('파일 수: ' + str(len(files)))
html_files = [f['path'] for f in files if f.get('path','').endswith('.html')]
print('HTML 파일:')
for p in html_files:
    print('  ' + p)

# 레이아웃 파일 찾기
layout = None
for candidate in ['html/layout/basic.html','html/layout/layout.html','layout/basic.html','basic.html']:
    if candidate in html_files:
        layout = candidate
        break
if not layout and html_files:
    for p in html_files:
        if 'layout' in p.lower() or 'basic' in p.lower():
            layout = p
            break

print('')
print('레이아웃 파일: ' + str(layout))

if not layout:
    print('레이아웃 파일을 찾지 못했습니다. 위 목록에서 경로를 직접 입력:')
    try:
        layout = raw_input('경로: ').strip()
    except NameError:
        layout = input('경로: ').strip()

# 파일 읽기
print('')
print('파일 읽기...')
encoded = urllib.parse.quote(layout, safe='')
r = api('GET', '/designs/' + str(skin_no) + '/files?shop_no=1&path=' + encoded)
if '_err' in r:
    print('오류: ' + r['_msg'])
    sys.exit(1)

files_data = r.get('files', [])
if not files_data:
    print('파일 내용 없음')
    sys.exit(1)

html_content = files_data[0].get('content', '')
print('파일 크기: ' + str(len(html_content)) + ' bytes')

# 인젝션 코드 준비
with open(SCRIPT_FILE, 'r', encoding='utf-8') as f:
    inject_code = '\n' + MARKER + '\n' + f.read() + '\n' + END_MARKER + '\n'

# 기존 인젝션 제거
if MARKER in html_content:
    s = html_content.find(MARKER)
    e = html_content.find(END_MARKER)
    if e != -1:
        html_content = html_content[:s] + html_content[e + len(END_MARKER):]
        print('기존 인젝션 제거됨')

# </head> 앞에 삽입
if '</head>' in html_content:
    new_content = html_content.replace('</head>', inject_code + '</head>', 1)
elif '</HEAD>' in html_content:
    new_content = html_content.replace('</HEAD>', inject_code + '</HEAD>', 1)
else:
    new_content = inject_code + html_content

print('삽입 완료: ' + str(len(new_content)) + ' bytes')

# 파일 저장
print('저장 중...')
r = api('PUT', '/designs/' + str(skin_no) + '/files', {
    'request': {
        'shop_no': 1,
        'path': layout,
        'content': new_content,
    }
})

if '_err' in r:
    print('저장 오류: ' + r['_msg'])
    sys.exit(1)

print('')
print('============================================')
print('  적용 완료!')
print('  https://d-daytrip.co.kr/reservation/')
print('  detail.html?product_no=133 확인해주세요')
print('============================================')
