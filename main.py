# ─────────────────────────────────────────────
# main.py  –  매일 실행하는 자동화 파이프라인
#
# 사용법:
#   python main.py                   # 오늘 시즌 기준, 블로그 상위 5개 키워드 생성
#   python main.py --top 10          # 상위 10개 키워드로 생성
#   python main.py --type 인스타그램  # 콘텐츠 타입 지정
#   python main.py --keyword "오키나와 골프 봄"  # 키워드 직접 지정
#   python main.py --season 여름     # 시즌 지정
# ─────────────────────────────────────────────

import argparse
import datetime
import json
from pathlib import Path

from keywords    import run_keyword_collection, get_current_season
from content_gen import generate_batch, print_content, generate_content, save_content

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def run(top: int = 5, content_type: str = "블로그", season: str | None = None,
        direct_keyword: str | None = None):

    today  = datetime.date.today().strftime("%Y-%m-%d")
    season = season or get_current_season()

    print(f"\n{'='*60}")
    print(f"  블로그 데이터랩 자동화 파이프라인")
    print(f"  날짜: {today}  |  시즌: {season}  |  타입: {content_type}")
    print(f"{'='*60}")

    # ── Step 1: 키워드 수집 ──────────────────────────
    if direct_keyword:
        keywords = [direct_keyword]
        print(f"\n[Step 1] 직접 입력 키워드: {direct_keyword}")
    else:
        print("\n[Step 1] 키워드 수집 중...")
        kw_stats = run_keyword_collection(season=season)

        # 검색량 기준 상위 N개 추출
        keywords = [k["keyword"] for k in kw_stats[:top]]
        print(f"\n  → 콘텐츠 생성 대상 키워드 ({len(keywords)}개):")
        for i, kw in enumerate(keywords, 1):
            stat = kw_stats[i-1]
            print(f"    {i:2}. {kw}  (검색량: {int(stat['total_cnt']):,}  트렌드: {stat['trend_score']})")

    # ── Step 2: 콘텐츠 생성 ──────────────────────────
    print(f"\n[Step 2] 콘텐츠 생성 중 ({content_type})...")
    results = generate_batch(keywords, content_type)

    # ── Step 3: 요약 리포트 ──────────────────────────
    print(f"\n[Step 3] 오늘의 콘텐츠 요약")
    print(f"{'='*60}")

    summary = []
    for r in results:
        best_title = r["titles"][0]
        summary.append({
            "keyword":    r["keyword"],
            "best_title": best_title,
            "thumbnail":  r["thumbnail"],
            "cta":        r["cta"],
            "hashtags":   r["hashtags"][:5],
        })
        print(f"\n  키워드: {r['keyword']}")
        print(f"  추천 제목: {best_title}")
        print(f"  썸네일: {r['thumbnail']}")

    # 요약 JSON 저장
    summary_path = OUTPUT_DIR / f"summary_{today.replace('-','')}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"  완료! 생성된 콘텐츠: {len(results)}개")
    print(f"  요약 파일: {summary_path}")
    print(f"  상세 파일: output/ 폴더 확인")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="블로그 콘텐츠 자동화 파이프라인")
    parser.add_argument("--top",     type=int, default=5,      help="키워드 상위 N개 (기본: 5)")
    parser.add_argument("--type",    type=str, default="블로그", help="콘텐츠 타입: 블로그|인스타그램|스레드")
    parser.add_argument("--season",  type=str, default=None,   help="시즌: 봄|여름|가을|겨울 (기본: 현재 시즌)")
    parser.add_argument("--keyword", type=str, default=None,   help="직접 키워드 입력 (지정 시 API 수집 생략)")
    args = parser.parse_args()

    run(
        top=args.top,
        content_type=args.type,
        season=args.season,
        direct_keyword=args.keyword,
    )
