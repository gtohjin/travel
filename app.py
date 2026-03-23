"""
블로그 데이터랩 - 웹 대시보드
실행: python -m streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
import datetime
from pathlib import Path

# ──────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────
def guess_season() -> str:
    month = datetime.date.today().month
    if month in [3, 4, 5]:   return "봄"
    if month in [6, 7, 8]:   return "여름"
    if month in [9, 10, 11]: return "가을"
    return "겨울"

# ──────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────
st.set_page_config(
    page_title="블로그 데이터랩",
    page_icon="⛳",
    layout="wide",
)

st.title("⛳ 블로그 데이터랩")
st.caption("키워드 자동 수집 → 콘텐츠 자동 생성 | 지토트래블")

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────
# 사이드바 — 페르소나 설정
# ──────────────────────────────────────────
from personas import (
    PERSONAS, all_personas, list_personas,
    save_custom_persona, delete_custom_persona, load_custom_personas,
)

with st.sidebar:
    st.header("타깃 페르소나")

    all_p = all_personas()
    persona_options = {"(기본 대상 독자)": None} | {v: k for k, v in list_personas().items()}
    selected_persona_label = st.selectbox(
        "콘텐츠를 쓸 대상을 선택하세요",
        options=list(persona_options.keys()),
    )
    selected_persona_key = persona_options[selected_persona_label]

    if selected_persona_key and selected_persona_key in all_p:
        p = all_p[selected_persona_key]
        st.markdown("---")
        st.markdown(f"**{p['name']}** ({p['age']}, {p['job']})")
        st.caption(p["background"])
        st.markdown("**Pain Points**")
        for pt in p["pain_points"]:
            st.caption(f"• {pt}")
        st.markdown("**동기**")
        for m in p["motivations"]:
            st.caption(f"• {m}")
        st.markdown("**글 스타일**")
        st.caption(p["writing_style"])
        # 커스텀 페르소나만 삭제 가능
        custom_keys = load_custom_personas().keys()
        if selected_persona_key in custom_keys:
            if st.button("🗑 이 페르소나 삭제", type="secondary"):
                delete_custom_persona(selected_persona_key)
                st.success("삭제됐습니다.")
                st.rerun()
    else:
        st.caption("기본: 40~60대 골프 마니아 / 대표·임원 대상 일반 어조")

    # ── 페르소나 추가 폼 ──────────────────────
    st.markdown("---")
    with st.expander("➕ 새 페르소나 추가"):
        with st.form("add_persona_form", clear_on_submit=True):
            p_name  = st.text_input("이름", placeholder="예: 골프 초보 김사원")
            p_age   = st.text_input("나이", placeholder="예: 32세")
            p_job   = st.text_input("직업", placeholder="예: 스타트업 마케터")
            p_bg    = st.text_area("배경 (한두 문장)", placeholder="예: 골프 시작 1년차, 첫 해외 골프 계획 중")
            p_pain  = st.text_area("Pain Points (줄바꿈으로 구분)", placeholder="예: 예산이 부족\n어디서 예약해야 할지 모름")
            p_motive= st.text_area("동기 (줄바꿈으로 구분)", placeholder="예: 친구들과 특별한 경험\nSNS에 올릴 컨텐츠")
            p_style = st.text_area("글 스타일", placeholder="예: 친근하고 유머 있는 어조. 짧은 문장 선호.")
            p_topics= st.text_input("관심 주제 (쉼표 구분)", placeholder="예: 저렴한 코스, 2박3일 코스, 초보 코스")
            submitted = st.form_submit_button("저장", type="primary")

            if submitted:
                if not p_name:
                    st.error("이름을 입력하세요.")
                else:
                    key = p_name.replace(" ", "_")
                    save_custom_persona(key, {
                        "name": p_name,
                        "age": p_age or "미입력",
                        "job": p_job or "미입력",
                        "background": p_bg or "",
                        "pain_points": [x.strip() for x in p_pain.splitlines() if x.strip()],
                        "motivations": [x.strip() for x in p_motive.splitlines() if x.strip()],
                        "writing_style": p_style or "",
                        "preferred_topics": [x.strip() for x in p_topics.split(",") if x.strip()],
                    })
                    st.success(f"'{p_name}' 페르소나가 저장됐습니다.")
                    st.rerun()

# ──────────────────────────────────────────
# 탭 구성
# ──────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["① 키워드 수집", "② 콘텐츠 생성", "③ 저장된 결과"])


# ══════════════════════════════════════════
# TAB 1 — 키워드 수집
# ══════════════════════════════════════════
with tab1:
    st.subheader("시즌별 키워드 자동 수집")

    col1, col2 = st.columns([1, 2])
    with col1:
        season_opts = ["봄", "여름", "가을", "겨울"]
        season = st.selectbox("시즌 선택", season_opts,
                              index=season_opts.index(guess_season()))
    with col2:
        extra_input = st.text_input("추가 힌트 키워드 (선택, 쉼표 구분)",
                                    placeholder="예: 삿포로골프, 교토골프")

    col_btn1, col_btn2 = st.columns([1, 3])
    run_kw   = col_btn1.button("🔍 키워드 수집 시작", type="primary")
    run_hook = col_btn2.button("⚡ 추천 TOP 5 + 후킹 메시지 생성",
                               disabled=("kw_stats" not in st.session_state))

    if run_kw:
        extra = [k.strip() for k in extra_input.split(",") if k.strip()] if extra_input else None
        with st.spinner("네이버 검색광고 API에서 수집 중... (약 30초)"):
            try:
                from keywords import run_keyword_collection
                stats = run_keyword_collection(season=season, extra_seeds=extra)
                st.session_state["kw_stats"]  = stats
                st.session_state["kw_season"] = season
                st.session_state["kw_extra"]  = extra or []   # 추가 힌트 저장
                st.session_state.pop("hooks", None)
                st.success(f"✅ 수집 완료: {len(stats)}개 키워드")
            except Exception as e:
                st.error(f"오류: {e}")

    if run_hook and "kw_stats" in st.session_state:
        cur_season = st.session_state.get("kw_season", guess_season())
        cur_extra  = st.session_state.get("kw_extra", [])
        with st.spinner("Claude가 후킹 메시지 작성 중..."):
            try:
                from content_gen import generate_season_recommendations
                hooks = generate_season_recommendations(
                    st.session_state["kw_stats"], cur_season,
                    extra_hints=cur_extra,
                    persona_key=selected_persona_key,
                )
                st.session_state["hooks"] = hooks
            except Exception as e:
                st.error(f"후킹 생성 오류: {e}")

    # ── 추천 TOP 5 카드 ──────────────────────────
    if "hooks" in st.session_state:
        hooks      = st.session_state["hooks"]
        cur_season = st.session_state.get("kw_season", guess_season())

        st.markdown("---")
        st.markdown(f"## 🎯 {cur_season} 시즌 추천 TOP 5")
        st.caption("현존 마케팅 기법을 적용한 후킹 메시지 — 바로 복사해서 쓰세요")

        TIER_BADGE = {"시즌롱테일": "🌸 시즌 롱테일", "고볼륨핵심": "🔥 고볼륨 핵심", "일반": "📌 일반"}
        TECH_COLOR = {
            "FOMO":          "#FF4B4B",
            "사회적 증거":    "#1E90FF",
            "PAS":           "#FF8C00",
            "호기심 갭":      "#9B59B6",
            "숫자의 힘":      "#2ECC71",
            "Before/After":  "#E67E22",
            "공감 첫 문장":   "#16A085",
            "시즌 한정":      "#C0392B",
        }

        for i, h in enumerate(hooks, 1):
            tech       = h.get("technique", "")
            color      = next((v for k, v in TECH_COLOR.items() if k in tech), "#555")
            badge      = TIER_BADGE.get(h.get("tier", "일반"), "📌 일반")
            vol        = h.get("search_vol", 0)
            short_hook = h.get("short_hook", "")

            with st.container(border=True):
                top_col1, top_col2 = st.columns([5, 1])
                with top_col1:
                    st.markdown(f"### {i}. {h['hook_title']}")
                with top_col2:
                    st.markdown(f"월 **{vol:,}**건")

                # 배지 행
                st.markdown(
                    f'<span style="background:{color};color:white;padding:2px 8px;'
                    f'border-radius:4px;font-size:12px;">🔑 {tech}</span>'
                    f'&nbsp;&nbsp;<span style="font-size:13px;">{badge}</span>'
                    f'&nbsp;&nbsp;<span style="color:#888;font-size:12px;">'
                    f'키워드: {h["keyword"]}</span>',
                    unsafe_allow_html=True,
                )

                # 8자 숏훅 강조 박스
                if short_hook:
                    st.markdown(
                        f'<div style="margin:10px 0;padding:8px 16px;'
                        f'background:#fff8e1;border-left:4px solid #FFC107;'
                        f'font-size:20px;font-weight:bold;letter-spacing:1px;">'
                        f'⚡ {short_hook}</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("")
                st.markdown(h["hook_body"])
                st.info(h["hook_cta"])

                # 복사용 텍스트박스
                with st.expander("📋 복사용 텍스트"):
                    copy_text = (
                        f"[숏훅] {short_hook}\n\n"
                        f"[제목] {h['hook_title']}\n\n"
                        f"{h['hook_body']}\n\n"
                        f"{h['hook_cta']}"
                    )
                    st.text_area("", copy_text, height=160, key=f"copy_{i}",
                                 label_visibility="collapsed")

        st.markdown("---")

    # ── 키워드 테이블 ────────────────────────────
    if "kw_stats" in st.session_state:
        stats  = st.session_state["kw_stats"]
        season = st.session_state.get("kw_season", "봄")

        df = pd.DataFrame(stats)
        if "tier" not in df.columns:
            df["tier"] = "일반"
        df = df[["tier", "keyword", "total_cnt", "pc_cnt", "mobile_cnt", "trend_score"]]
        df.columns = ["구분", "키워드", "총검색량", "PC", "모바일", "트렌드"]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 고볼륨 핵심 키워드")
            df_vol = df[df["구분"] == "고볼륨핵심"].head(20)
            st.dataframe(df_vol[["키워드", "총검색량", "트렌드"]],
                         width="stretch", hide_index=True)
        with c2:
            st.markdown(f"#### 시즌 롱테일 키워드 ({season})")
            df_sea = df[df["구분"] == "시즌롱테일"].head(20)
            st.dataframe(df_sea[["키워드", "총검색량", "트렌드"]],
                         width="stretch", hide_index=True)

        st.markdown("#### 전체 키워드 목록")
        st.dataframe(df, width="stretch", hide_index=True, height=400)

        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇ CSV 다운로드",
            data=csv_bytes,
            file_name=f"keywords_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════
# TAB 2 — 콘텐츠 생성
# ══════════════════════════════════════════
with tab2:
    st.subheader("콘텐츠 자동 생성")

    input_mode = st.radio("키워드 입력 방식", ["직접 입력", "수집된 키워드에서 선택"],
                          horizontal=True)

    keyword = ""
    if input_mode == "직접 입력":
        keyword = st.text_input("키워드 입력", placeholder="예: 북해도 골프 봄, 후쿠오카 골프 5월")
    else:
        if "kw_stats" in st.session_state:
            options = [s["keyword"] for s in st.session_state["kw_stats"][:50]]
            keyword = st.selectbox("키워드 선택", options)
        else:
            st.info("먼저 [① 키워드 수집] 탭에서 수집을 먼저 실행해 주세요.")

    col1, col2 = st.columns(2)
    with col1:
        content_type = st.selectbox("콘텐츠 타입", ["블로그", "인스타그램", "스레드"])
    with col2:
        num_gen = st.number_input("생성 개수", min_value=1, max_value=10, value=1,
                                  help="2개 이상이면 수집된 상위 키워드 순서대로 자동 선택")

    gen_btn = st.button("✍️ 콘텐츠 생성", type="primary", disabled=(not keyword))

    if gen_btn and keyword:
        if num_gen == 1:
            kws = [keyword]
        else:
            if "kw_stats" in st.session_state:
                kws = [s["keyword"] for s in st.session_state["kw_stats"][:num_gen]]
            else:
                kws = [keyword]

        results = []
        bar = st.progress(0)
        for i, kw in enumerate(kws):
            st.write(f"생성 중: **{kw}** ({i+1}/{len(kws)})")
            try:
                from content_gen import generate_content, save_content
                content = generate_content(kw, content_type, persona_key=selected_persona_key)
                save_content(content)
                results.append(content)
            except Exception as e:
                st.error(f"{kw} 실패: {e}")
            bar.progress((i + 1) / len(kws))

        st.session_state["last_results"] = results
        bar.empty()
        st.success(f"✅ {len(results)}개 생성 완료!")

    # 결과 출력
    if "last_results" in st.session_state:
        for content in st.session_state["last_results"]:
            st.markdown("---")
            persona_label = ""
            if content.get("persona") and content["persona"] in all_p:
                persona_label = f" | 페르소나: {all_p[content['persona']]['name']}"
            st.markdown(f"### 📌 `{content['keyword']}` — {content['type']}{persona_label}")

            # 제목 10개
            with st.expander("📝 제목 10개", expanded=True):
                for i, t in enumerate(content["titles"], 1):
                    st.markdown(f"**{i}.** {t}")

            # 썸네일 + CTA
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**썸네일 문구**")
                st.info(content["thumbnail"])
            with c2:
                st.markdown("**CTA**")
                st.info(content["cta"])

            # SEO 메타 + 키워드 (블로그 전용)
            if content.get("meta_description") or content.get("seo_keywords"):
                with st.expander("🔍 SEO 정보", expanded=True):
                    if content.get("meta_description"):
                        st.markdown("**메타 설명** (검색엔진 노출 문구)")
                        st.info(content["meta_description"])
                    if content.get("seo_keywords"):
                        st.markdown("**SEO 키워드**")
                        st.markdown("  ".join([f"`{k}`" for k in content["seo_keywords"]]))

            # 본문
            with st.expander("📄 본문", expanded=True):
                st.markdown(content["body"])

            # 해시태그
            st.markdown("**해시태그**")
            st.markdown("  ".join([f"`#{t}`" for t in content["hashtags"]]))

            # 다운로드
            json_str = json.dumps(content, ensure_ascii=False, indent=2)
            st.download_button(
                "⬇ JSON 다운로드",
                data=json_str.encode("utf-8"),
                file_name=f"content_{content['keyword']}_{content['type']}.json",
                mime="application/json",
                key=f"dl_{content['keyword']}_{content['type']}",
            )


# ══════════════════════════════════════════
# TAB 3 — 저장된 결과
# ══════════════════════════════════════════
with tab3:
    st.subheader("저장된 결과 파일")

    col_refresh = st.columns([1, 4])[0]
    if col_refresh.button("🔄 새로고침"):
        st.rerun()

    csv_files  = sorted(OUTPUT_DIR.glob("keywords_*.csv"),  reverse=True)
    json_files = sorted(OUTPUT_DIR.glob("content_*.json"), reverse=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"**키워드 CSV** ({len(csv_files)}개)")
        for f in csv_files[:5]:
            df = pd.read_csv(f, encoding="utf-8-sig")
            with st.expander(f.name):
                st.dataframe(df, width="stretch", hide_index=True, height=300)
                st.download_button("⬇ 다운로드", df.to_csv(index=False).encode("utf-8-sig"),
                                   f.name, key=f"csv_{f.stem}")

    with c2:
        st.markdown(f"**콘텐츠** ({len(json_files)}개)")
        for f in json_files[:10]:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                label = f"{data['keyword']} | {data['type']} | {data.get('created_at','')}"
                with st.expander(label):
                    st.markdown(f"**추천 제목:** {data['titles'][0]}")
                    st.markdown(f"**썸네일:** `{data['thumbnail']}`")
                    st.markdown("**제목 전체:**")
                    for i, t in enumerate(data["titles"], 1):
                        st.markdown(f"{i}. {t}")
                    st.markdown("**본문:**")
                    st.markdown(data["body"])
                    st.markdown("**해시태그:** " + "  ".join([f"`#{t}`" for t in data["hashtags"]]))
                    json_str = json.dumps(data, ensure_ascii=False, indent=2)
                    st.download_button("⬇ JSON", json_str.encode(), f.name,
                                       key=f"json_{f.stem}")
            except Exception:
                st.warning(f"읽기 실패: {f.name}")
