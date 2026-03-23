# ─────────────────────────────────────────────
# keywords.py  –  키워드 자동 수집
#   1. 시즌 + 목적지 조합으로 키워드 시드 생성
#   2. 네이버 검색광고 API로 연관 키워드 + 검색량 조회
#   3. 네이버 데이터랩 API로 트렌드 스코어 조회
#   4. 결과를 CSV로 저장
# ─────────────────────────────────────────────

import hashlib
import hmac
import base64
import time
import datetime
import itertools
import json
import csv
import requests
from pathlib import Path
from config import (
    NAVER_AD_API_KEY, NAVER_AD_SECRET_KEY, NAVER_AD_CUSTOMER_ID,
    NAVER_CLIENT_ID, NAVER_CLIENT_SECRET,
    SEASON_MAP, DESTINATIONS, BUSINESS,
)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ────────────────────────────────────────────
# 1. 시즌 키워드 시드 자동 생성
# ────────────────────────────────────────────
def get_current_season() -> str:
    month = datetime.date.today().month
    for season, info in SEASON_MAP.items():
        if month in info["months"]:
            return season
    return "봄"


# API 힌트용: 짧고 실제 검색되는 기본 키워드 (공백 없이)
# → 이 키워드로 API 호출하면 연관 키워드 수백 개를 돌려줌
BASE_HINT_KEYWORDS = [
    "북해도골프", "일본골프", "오키나와골프", "규슈골프",
    "후쿠오카골프", "오사카골프", "도쿄골프", "일본골프여행",
    "해외골프", "일본골프패키지",
]


def generate_seed_keywords(season: str | None = None, extra: list[str] | None = None) -> list[str]:
    """API 힌트용 짧은 시드 키워드 반환 (공백 없음)"""
    seeds = list(BASE_HINT_KEYWORDS)
    if extra:
        # 외부 추가 키워드도 공백 제거
        seeds.extend([kw.replace(" ", "") for kw in extra])
    return list(dict.fromkeys(seeds))


# ────────────────────────────────────────────
# 2. 네이버 검색광고 API – 연관 키워드 & 검색량
# ────────────────────────────────────────────
def _naver_ad_signature(secret_key: str, timestamp: str, method: str, path: str) -> str:
    message = f"{timestamp}.{method}.{path}"
    # Secret key는 문자열 그대로 encode() 후 HMAC 키로 사용
    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


def fetch_keyword_stats(keywords: list[str]) -> list[dict]:
    """
    네이버 검색광고 API로 PC/모바일 월간 검색량 조회.
    한 번에 최대 5개까지 가능 → 청크로 나눠서 호출.
    """
    if NAVER_AD_API_KEY == "YOUR_NAVER_AD_API_KEY":
        print("[SKIP] 네이버 검색광고 API 키 미설정 → 더미 데이터 반환")
        return [{"keyword": kw, "pc_cnt": 0, "mobile_cnt": 0} for kw in keywords]

    path = "/keywordstool"
    url  = f"https://api.searchad.naver.com{path}"
    timestamp = str(int(time.time() * 1000))
    sign = _naver_ad_signature(NAVER_AD_SECRET_KEY, timestamp, "GET", path)

    headers = {
        "X-Timestamp":   timestamp,
        "X-API-KEY":     NAVER_AD_API_KEY,
        "X-Customer":    NAVER_AD_CUSTOMER_ID,
        "X-Signature":   sign,
    }

    def parse_cnt(val):
        if isinstance(val, (int, float)):
            return int(val)
        try:
            return int(str(val).replace("<", "").replace(">", "").strip().split()[0])
        except Exception:
            return 0

    seen    = {}   # 중복 제거: keyword → 최대 검색량 유지
    for i in range(0, len(keywords), 5):
        chunk = keywords[i:i+5]
        clean_chunk = [kw.replace(" ", "") for kw in chunk]
        params = [("hintKeywords", kw) for kw in clean_chunk] + [("showDetail", 1)]
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            for item in resp.json().get("keywordList", []):
                kw  = item.get("relKeyword", "").strip()
                pc  = parse_cnt(item.get("monthlyPcQcCnt", 0))
                mob = parse_cnt(item.get("monthlyMobileQcCnt", 0))
                if kw and (kw not in seen or seen[kw]["pc_cnt"] + seen[kw]["mobile_cnt"] < pc + mob):
                    seen[kw] = {"keyword": kw, "pc_cnt": pc, "mobile_cnt": mob}
        except Exception as e:
            print(f"[ERROR] 검색광고 API: {e}")
        time.sleep(0.3)

    return list(seen.values())


# ────────────────────────────────────────────
# 3. 네이버 데이터랩 API – 검색 트렌드
# ────────────────────────────────────────────
def fetch_datalab_trend(keywords: list[str], period_days: int = 90) -> dict[str, float]:
    """
    데이터랩 검색어트렌드 API로 최근 period_days 동안의 평균 트렌드 스코어 반환.
    한 번에 최대 5개 그룹.
    """
    if NAVER_CLIENT_ID == "YOUR_NAVER_CLIENT_ID":
        print("[SKIP] 네이버 데이터랩 API 키 미설정 → 더미 스코어 반환")
        return {kw: 0.0 for kw in keywords}

    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
        "Content-Type":          "application/json",
    }

    end   = datetime.date.today()
    start = end - datetime.timedelta(days=period_days)
    scores = {}

    for i in range(0, len(keywords), 5):
        chunk = keywords[i:i+5]
        body = {
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate":   end.strftime("%Y-%m-%d"),
            "timeUnit":  "week",
            "keywordGroups": [
                {"groupName": kw, "keywords": [kw]} for kw in chunk
            ],
        }
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=10)
            resp.raise_for_status()
            for result in resp.json().get("results", []):
                name   = result["title"]
                ratios = [p["ratio"] for p in result.get("data", [])]
                scores[name] = round(sum(ratios) / len(ratios), 1) if ratios else 0.0
        except Exception as e:
            print(f"[ERROR] 데이터랩 API: {e}")
        time.sleep(0.3)

    return scores


# ────────────────────────────────────────────
# 4. 시즌 필터링
# ────────────────────────────────────────────
def filter_by_season(stats: list[dict], season: str) -> list[dict]:
    """
    우선순위 3단계:
      1순위: 시즌어 + 골프어 동시 포함 (예: "일본골프여름", "북해도골프5월")
      2순위: 골프어만 포함            (예: "일본골프여행", "규슈골프패키지")
      3순위: 시즌어만 포함            (예: "일본봄여행")
      제외: 골프·시즌 관련 없는 것     (예: "일본여행준비물", "비자")
    """
    season_words = SEASON_MAP[season]["keywords"]
    golf_words   = ["골프", "라운딩", "라운드", "코스", "그린", "패키지"]
    dest_words   = DESTINATIONS + ["홋카이도", "훗카이도", "오키나와"]

    tier1, tier2, tier3 = [], [], []
    for s in stats:
        kw = s["keyword"]
        has_season = any(sw in kw for sw in season_words)
        has_golf   = any(gw in kw for gw in golf_words)
        has_dest   = any(d  in kw for d  in dest_words)

        if has_golf and has_season:
            tier1.append(s)
        elif has_golf and (has_dest or "일본" in kw or "해외" in kw):
            tier2.append(s)
        elif has_golf:
            tier3.append(s)
        # 그 외는 제외

    return tier1 + tier2 + tier3


# ────────────────────────────────────────────
# 5. 통합 실행 + CSV 저장
# ────────────────────────────────────────────
def run_keyword_collection(season: str | None = None, extra_seeds: list[str] | None = None) -> list[dict]:
    today    = datetime.date.today().strftime("%Y%m%d")
    season   = season or get_current_season()

    print(f"\n=== 키워드 수집 시작 | 시즌: {season} | {today} ===")

    # 1) 힌트 시드 키워드 (짧고 검색량 있는 기본어)
    seeds = generate_seed_keywords(season, extra_seeds)
    print(f"  힌트 키워드: {len(seeds)}개 → API로 연관 키워드 수집 중...")

    # 2) API 호출 → 힌트당 수백 개 연관 키워드 수집
    raw_stats = fetch_keyword_stats(seeds)

    # 3) 시즌 필터링 → 시즌 관련 + 골프 관련만 추림
    filtered = filter_by_season(raw_stats, season)
    print(f"  수집된 연관 키워드: {len(raw_stats)}개 → 시즌 필터 후: {len(filtered)}개")

    # 4) 검색량 합산 & 정렬
    for s in filtered:
        s["total_cnt"]   = s["pc_cnt"] + s["mobile_cnt"]
        s["trend_score"] = 0.0
        s["season"]      = season

    filtered.sort(key=lambda x: x["total_cnt"], reverse=True)

    # 5) 데이터랩 트렌드 (상위 20개만)
    top_kws   = [s["keyword"] for s in filtered[:20]]
    trend_map = fetch_datalab_trend(top_kws)
    for s in filtered:
        s["trend_score"] = trend_map.get(s["keyword"], 0.0)

    stats = filtered if filtered else raw_stats

    # tier 태깅 (CSV에서 구분 가능하도록)
    season_words = SEASON_MAP[season]["keywords"]
    for s in stats:
        has_season = any(sw in s["keyword"] for sw in season_words)
        if has_season:
            s["tier"] = "시즌롱테일"
        elif s["total_cnt"] >= 1000:
            s["tier"] = "고볼륨핵심"
        else:
            s["tier"] = "일반"

    stats.sort(key=lambda x: x["total_cnt"], reverse=True)

    # 6) CSV 저장 (파일이 열려 있으면 시간 suffix 추가)
    now_str  = datetime.datetime.now().strftime("%H%M%S")
    csv_path = OUTPUT_DIR / f"keywords_{today}.csv"
    try:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["tier","keyword","season","pc_cnt","mobile_cnt","total_cnt","trend_score"])
            writer.writeheader()
            writer.writerows(stats)
    except PermissionError:
        csv_path = OUTPUT_DIR / f"keywords_{today}_{now_str}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["tier","keyword","season","pc_cnt","mobile_cnt","total_cnt","trend_score"])
            writer.writeheader()
            writer.writerows(stats)

    # 요약 출력
    seasonal_top = [s for s in stats if s["tier"] == "시즌롱테일"][:5]
    volume_top   = [s for s in stats if s["tier"] == "고볼륨핵심"][:5]

    print(f"  저장 완료: {csv_path}  (총 {len(stats)}개)")
    print(f"\n  [고볼륨 핵심 키워드 Top5]")
    for s in volume_top:
        print(f"    {s['keyword']:25s}  {s['total_cnt']:>6,}")
    print(f"\n  [시즌 롱테일 키워드 Top5] (시즌: {season})")
    for s in seasonal_top:
        print(f"    {s['keyword']:25s}  {s['total_cnt']:>6,}")

    return stats


if __name__ == "__main__":
    run_keyword_collection()
