# ─────────────────────────────────────────────
# content_gen.py  –  Claude API로 콘텐츠 자동 생성
#   입력: 키워드 하나
#   출력: 제목 × 10, 본문 초안, CTA, 썸네일 문구, 해시태그
# ─────────────────────────────────────────────

import json
import random
import datetime
import anthropic
from pathlib import Path
from config import ANTHROPIC_API_KEY, BUSINESS

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL  = "claude-sonnet-4-6"

# ── 랜덤 변수 풀 ──────────────────────────────
_PERSPECTIVES = [
    "처음 일본 골프를 고민하는 초보자 시선",
    "이미 여러 번 다녀온 골프 마니아 시선",
    "골프를 빌미로 여행을 즐기는 여행자 시선",
    "비용 대비 가성비를 따지는 현실적인 직장인 시선",
    "특별한 기념일 선물로 골프여행을 준비하는 시선",
    "혼자 떠나는 솔로 골프 여행자 시선",
    "2~4인 모임으로 떠나는 골프 동반자 시선",
]

_OPENING_STYLES = [
    "질문으로 시작 — 독자에게 직접 묻는 방식",
    "충격적인 사실로 시작 — 예상 못한 통계나 수치 제시",
    "공감 일화로 시작 — 독자가 겪었을 법한 상황 묘사",
    "반전 선언으로 시작 — 통념을 뒤집는 첫 문장",
    "시간 배경으로 시작 — 특정 계절·시간대 풍경 묘사",
    "대화체로 시작 — 친한 지인에게 말하듯 시작",
]

_FORBIDDEN_WORDS = [
    ["추천드립니다", "안내드립니다", "소개드립니다"],
    ["최고의", "최상의", "최적의"],
    ["다양한", "여러가지", "많은"],
    ["진행됩니다", "제공됩니다", "구성됩니다"],
    ["정말", "매우", "굉장히"],
    ["특별한", "특별하게", "특별함"],
]

_TITLE_FORMATS = [
    "숫자 포함 (예: TOP3, 5가지, 2박3일)",
    "질문형 (예: ~하셨나요? ~인가요?)",
    "대비형 (예: A vs B, 전 vs 후)",
    "비밀/노하우형 (예: 아무도 안 알려준, 현지인만 아는)",
    "감성형 (예: 잊지 못할, 평생 기억할)",
    "긴급형 (예: 지금 아니면, 마감 임박)",
    "공감형 (예: 혹시 나만 이래?, 이런 경험 있으신가요)",
]


# ────────────────────────────────────────────
# 핵심 생성 함수
# ────────────────────────────────────────────
def generate_content(keyword: str, content_type: str = "블로그") -> dict:
    """
    keyword:      메인 키워드 (예: "북해도 골프 여름")
    content_type: "블로그" | "인스타그램" | "스레드"
    반환: {titles, body, cta, thumbnail, hashtags, keyword, type, created_at}
    """

    brand    = BUSINESS["brand"]
    cta_url  = BUSINESS["cta_url"]
    tone     = BUSINESS["tone"]
    product  = BUSINESS["product"]

    # ── 매 호출마다 다른 결과를 위한 랜덤 변수 ──
    perspective    = random.choice(_PERSPECTIVES)
    opening_style  = random.choice(_OPENING_STYLES)
    forbidden      = random.choice(_FORBIDDEN_WORDS)
    title_format   = random.choice(_TITLE_FORMATS)
    # 제목 순서도 매번 다르게 셔플
    title_slots = [
        "클릭 유도형", "숫자 포함형", "질문형", "감성형", "실용 정보형",
        "후기 스타일", "시즌 한정형", "비교형", "리스트형", "궁금증 유발형",
    ]
    random.shuffle(title_slots)

    if content_type == "블로그":
        format_instruction = f"""
다음 구조로 SEO 최적화 블로그 글을 작성하세요.

■ 대상 독자
40~60대 골프 마니아, 회사 대표·임원, 해외골프여행 경험자 또는 입문 희망자.
이들은 바쁘고 정보에 민감하며, 신뢰할 수 있는 전문가의 조언을 원합니다.

■ 어조 & 스타일
- 존댓말 사용 (반말 절대 금지)
- 친근하고 대화체, 호기심 어린 어조
- 클릭베이트 아닌 정보가 풍부하고 위트 있는 글
- 전문 용어 사용 시 반드시 괄호로 쉽게 설명
- 스토리텔링 또는 실제 사례/비유 활용
- 단락은 짧고 흥미롭게 (3~4문장 이내)
- 굵은 글씨(**) 와 불릿(-)으로 스캔 가능성 높이기
- 혼잣말·자기소개("이 글에서는~", "작성하겠습니다" 등) 절대 금지

■ 글 구조
1. 제목 — 주요 키워드 포함, 클릭 욕구 자극
2. 소개 훅 — 독자가 계속 읽고 싶게 만드는 첫 문단 (스타일: {opening_style})
3. 본문 섹션 3~5개 — ## 소제목 사용, 각 섹션 핵심 포인트 1개씩
4. 핵심 요약 — 독자가 기억·행동할 내용 2~3문장
5. SEO 메타 설명 — 최대 155자, 키워드 포함
6. SEO 키워드 목록 — 본문에 자연스럽게 녹아든 키워드 5개

■ 이번 생성 변수 (매번 다른 결과)
- 독자 시선: {perspective}
- 금지어: {', '.join(forbidden)}

■ 분량: 1000~1400자
"""
    elif content_type == "인스타그램":
        format_instruction = f"""
인스타그램 캡션 형식으로 작성하세요:
- 존댓말 사용 (반말 절대 금지)
- 200~300자
- 줄바꿈 자주 활용
- 이모지 3~5개 자연스럽게 삽입
- 첫 줄: {opening_style}
- 독자 시선: {perspective}
- 금지어: {', '.join(forbidden)}
"""
    else:  # 스레드
        format_instruction = f"""
스레드(Threads) 캡션 형식으로 작성하세요:
- 존댓말 사용 (반말 절대 금지)
- 300~500자
- 친근한 대화체
- 첫 문장: {opening_style}
- 독자 시선: {perspective}
- 금지어: {', '.join(forbidden)}
"""

    prompt = f"""
당신은 {brand}의 {product} 전문 콘텐츠 마케터입니다.

메인 키워드: **{keyword}**
콘텐츠 타입: {content_type}
이번 제목 1번 형식: {title_format}

{format_instruction.strip()}

다음 JSON 형식으로만 응답하세요. JSON 외 다른 텍스트는 절대 포함하지 마세요.

{{
  "titles": [
    "제목1 ({title_slots[0]}, 키워드 포함, 30자 이내)",
    "제목2 ({title_slots[1]})",
    "제목3 ({title_slots[2]})",
    "제목4 ({title_slots[3]})",
    "제목5 ({title_slots[4]})",
    "제목6 ({title_slots[5]})",
    "제목7 ({title_slots[6]})",
    "제목8 ({title_slots[7]})",
    "제목9 ({title_slots[8]})",
    "제목10 ({title_slots[9]})"
  ],
  "body": "완성된 본문 전체. 위 구조 그대로 작성.",
  "meta_description": "SEO 메타 설명 (155자 이내)",
  "seo_keywords": ["키워드1","키워드2","키워드3","키워드4","키워드5"],
  "cta": "CTA 문구 1~2문장 (URL: {cta_url})",
  "thumbnail": "썸네일 문구 (15자 이내, 강렬하게)",
  "hashtags": ["해시태그1","해시태그2","해시태그3","해시태그4","해시태그5","해시태그6","해시태그7","해시태그8","해시태그9","해시태그10"]
}}

해시태그는 # 없이 단어만 작성하세요.
"""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = resp.content[0].text.strip()

    # JSON만 추출 (```json ... ``` 감싸여 있는 경우 처리)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)
    result.update({
        "keyword":    keyword,
        "type":       content_type,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    return result


# ────────────────────────────────────────────
# 결과 저장
# ────────────────────────────────────────────
def save_content(content: dict) -> Path:
    now     = datetime.datetime.now()
    today   = now.strftime("%Y%m%d")
    safe_kw = content["keyword"].replace(" ", "_").replace("/", "-")
    fname   = OUTPUT_DIR / f"content_{today}_{safe_kw}_{content['type']}.json"
    try:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    except PermissionError:
        fname = OUTPUT_DIR / f"content_{today}_{now.strftime('%H%M%S')}_{safe_kw}_{content['type']}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    return fname


def print_content(content: dict):
    print(f"\n{'='*60}")
    print(f"키워드: {content['keyword']} | 타입: {content['type']}")
    print(f"{'='*60}")
    print("\n[제목 10개]")
    for i, t in enumerate(content["titles"], 1):
        print(f"  {i:2}. {t}")
    print(f"\n[썸네일 문구]\n  {content['thumbnail']}")
    print(f"\n[본문 초안]\n{content['body'][:300]}...")
    print(f"\n[CTA]\n  {content['cta']}")
    print(f"\n[해시태그]\n  #{'  #'.join(content['hashtags'])}")


# ────────────────────────────────────────────
# 배치 생성
# ────────────────────────────────────────────
def generate_batch(keywords: list[str], content_type: str = "블로그") -> list[dict]:
    results = []
    for kw in keywords:
        print(f"\n  생성 중: {kw} ...")
        try:
            content = generate_content(kw, content_type)
            path    = save_content(content)
            print(f"  저장: {path.name}")
            results.append(content)
        except Exception as e:
            print(f"  [ERROR] {kw}: {e}")
    return results


# ────────────────────────────────────────────
# 시즌 추천 TOP 5 + 후킹 메시지
# ────────────────────────────────────────────

# 현존 마케팅 기법 목록 (Claude가 선택해서 적용)
HOOK_TECHNIQUES = [
    "FOMO(마감 임박·한정 수량) — '지금 안 하면 놓친다'는 긴박감",
    "사회적 증거(Social Proof) — 실제 고객 후기·숫자로 신뢰 구축",
    "PAS(Problem-Agitation-Solution) — 고통 공감 → 긁어주기 → 해결책 제시",
    "호기심 갭(Curiosity Gap) — 답을 보여주되 핵심 하나만 숨기기",
    "숫자의 힘(Specificity) — 구체적 숫자로 신뢰도·클릭률 상승",
    "Before/After — 변화 전후를 대비시켜 욕망 자극",
    "공감 첫 문장(Empathy Hook) — '혹시 이런 경험 있으신가요?'",
    "시즌 한정(Seasonal Urgency) — 특정 시기에만 가능한 경험 강조",
]


def generate_season_recommendations(
    kw_stats: list[dict],
    season: str,
    extra_hints: list[str] | None = None,
) -> list[dict]:
    """
    수집된 키워드 중 현재 시즌에 맞는 TOP 5 추천 + 각각에 후킹 메시지 생성.
    kw_stats:     run_keyword_collection() 반환값
    season:       "봄" | "여름" | "가을" | "겨울"
    extra_hints:  UI에서 입력한 추가 힌트 키워드 (시즌과 조합해 후킹 생성에 활용)
    반환: [{keyword, search_vol, tier, technique, hook_title, hook_body, hook_cta}, ...]
    """
    from config import SEASON_MAP
    brand   = BUSINESS["brand"]
    product = BUSINESS["product"]
    cta_url = BUSINESS["cta_url"]

    season_words = SEASON_MAP[season]["keywords"]

    # ── TOP 5 선정: 시즌 롱테일 × 고볼륨 균형 믹스 ──
    # 시즌 롱테일: 검색의도 명확, 전환율 높음
    seasonal    = [s for s in kw_stats
                   if s.get("tier") == "시즌롱테일" and s["total_cnt"] > 0]
    seasonal.sort(key=lambda x: x["total_cnt"], reverse=True)

    # 고볼륨 핵심: 골프·여행·패키지 직접 관련만
    golf_volume = [s for s in kw_stats
                   if s.get("tier") == "고볼륨핵심"
                   and any(w in s["keyword"] for w in ["골프","라운딩","패키지","여행"])]
    golf_volume.sort(key=lambda x: x["total_cnt"], reverse=True)

    # 추가 힌트 키워드가 있으면 힌트가 포함된 키워드를 우선 편입
    hint_matched = []
    if extra_hints:
        for s in kw_stats:
            if any(h.replace(" ","") in s["keyword"] for h in extra_hints):
                hint_matched.append(s)
        hint_matched.sort(key=lambda x: x["total_cnt"], reverse=True)

    # 믹스 전략: 힌트매칭 1~2개 + 시즌롱테일 2개 + 고볼륨 1~2개
    pool = hint_matched[:2] + seasonal[:3] + golf_volume[:3]
    seen, top5 = set(), []
    for s in pool:
        if s["keyword"] not in seen:
            seen.add(s["keyword"])
            top5.append(s)
        if len(top5) == 5:
            break
    if len(top5) < 5:
        for s in kw_stats:
            if s["keyword"] not in seen:
                seen.add(s["keyword"])
                top5.append(s)
            if len(top5) == 5:
                break

    # ── 추가 힌트 + 시즌 조합 컨텍스트 ──
    extra_context = ""
    if extra_hints:
        combos = [f"{h} {sw}" for h in extra_hints for sw in season_words[:3]][:8]
        extra_context = f"""
■ 추가 힌트 키워드 조합 [반드시 제목·본문에 반영]
- 입력 힌트: {', '.join(extra_hints)}
- 시즌 조합: {', '.join(combos)}
→ 위 조합 중 1개 이상을 각 후킹 제목 또는 본문에 자연스럽게 삽입하세요.
"""

    # ── 매 호출마다 다른 결과 ──
    shuffled_techniques = random.sample(HOOK_TECHNIQUES, len(HOOK_TECHNIQUES))
    forbidden_hook      = random.choice(_FORBIDDEN_WORDS)
    hook_tone           = random.choice([
        "짧고 강렬하게 — 한 문장이 칼처럼 꽂히게",
        "감성적으로 — 읽는 순간 장면이 그려지게",
        "대화체로 — 친근하고 자연스럽게",
        "데이터 기반으로 — 숫자와 사실로 설득하게",
        "스토리텔링으로 — 짧은 1인칭 경험담 형식",
    ])

    kw_list = "\n".join([
        f"{i+1}. [{s.get('tier','일반')}] {s['keyword']}  월 {s['total_cnt']:,}건"
        for i, s in enumerate(top5)
    ])
    techniques_list = "\n".join([f"- {t}" for t in shuffled_techniques])

    prompt = f"""
당신은 {brand}({product}) 전문 카피라이터입니다.
현재 시즌: {season}

■ 절대 규칙
- 반말 사용 금지. 모든 문장은 존댓말(~습니다, ~세요, ~어요)로 작성
- 혼잣말·자기소개 문구 절대 금지
- 사용 금지 단어: {', '.join(forbidden_hook)}
- 5개 모두 서로 다른 마케팅 기법 사용

■ 대상 독자
40~60대 골프 마니아, 회사 대표·임원, 해외골프여행 경험자 또는 입문 희망자

■ 현존 마케팅 기법 (각 항목에 하나씩, 중복 금지)
{techniques_list}

■ 글 톤: {hook_tone}

{extra_context}

■ 추천 키워드 TOP 5 (시즌 롱테일 + 고볼륨 믹스)
{kw_list}

반드시 아래 JSON 배열 형식으로만 응답하세요. JSON 외 텍스트 없이.

[
  {{
    "keyword": "키워드 그대로",
    "technique": "사용한 기법 이름",
    "short_hook": "8자 이내 임팩트 문구 (예: '지금 아니면 없어요', '이건 좀 달라요')",
    "hook_title": "후킹 제목 (30자 이내, 시즌·키워드 포함)",
    "hook_body": "후킹 본문 2~3문장. 존댓말. 감정 자극 후 행동 유발.",
    "hook_cta": "행동 유도 1문장 + URL {cta_url}"
  }}
]

- {season} 시즌 감성 자연스럽게 반영
- 블로그·SNS 즉시 게시 가능한 완성도
- short_hook은 단독으로 썸네일·카드뉴스 문구로 쓸 수 있게 강렬하게
"""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    hooks = json.loads(raw)

    # kw_stats 검색량 정보 병합
    vol_map = {s["keyword"]: s["total_cnt"] for s in kw_stats}
    tier_map = {s["keyword"]: s.get("tier", "일반") for s in kw_stats}
    for h in hooks:
        h["search_vol"] = vol_map.get(h["keyword"], 0)
        h["tier"]       = tier_map.get(h["keyword"], "일반")

    return hooks


# ────────────────────────────────────────────
# 단독 실행 테스트
# ────────────────────────────────────────────
if __name__ == "__main__":
    test_keyword = "북해도 골프 여름"
    print(f"테스트 키워드: {test_keyword}")
    content = generate_content(test_keyword, "블로그")
    print_content(content)
    path = save_content(content)
    print(f"\n저장 완료: {path}")
