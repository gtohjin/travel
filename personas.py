# ─────────────────────────────────────────────
# personas.py  –  콘텐츠 생성에 적용할 페르소나 정의
# ─────────────────────────────────────────────

PERSONAS = {
    "골프_고수_김부장": {
        "name": "골프 고수 김부장",
        "age": "55세",
        "job": "중소기업 대표",
        "background": "일본 골프 여행 5회 이상 경험한 골프 마니아. 핸디캡 10 이하.",
        "pain_points": [
            "퀄리티 낮은 코스에 실망한 경험",
            "언어 장벽으로 인한 예약 불편",
            "비용 대비 만족도에 민감",
        ],
        "motivations": [
            "랭킹 상위 명문 코스 공략",
            "효율적인 2박3일~3박4일 일정",
            "믿을 수 있는 전문 가이드",
        ],
        "writing_style": (
            "전문적이고 신뢰감 있는 어조. "
            "구체적 수치와 코스 비교를 선호. "
            "이미 아는 사람처럼 깊이 있게 이야기. "
            "과장 표현 없이 팩트로 설득."
        ),
        "preferred_topics": ["코스 난이도", "클럽하우스 퀄리티", "페어웨이 상태", "항공·숙소 패키지 가성비"],
    },

    "골프_입문_박과장": {
        "name": "골프 입문 박과장",
        "age": "42세",
        "job": "대기업 과장",
        "background": "골프 시작 2년차. 해외 골프는 처음 고민 중. 직장 상사·거래처 접대 골프가 계기.",
        "pain_points": [
            "해외 골프 어디서부터 시작해야 할지 모름",
            "혼자 예약하기 막막함",
            "실력이 부족해 민폐 될까 걱정",
        ],
        "motivations": [
            "비교적 저렴한 일본에서 첫 해외 골프 경험",
            "패키지로 편하게 전부 해결",
            "주변에 자랑할 수 있는 경험",
        ],
        "writing_style": (
            "친근하고 쉬운 말투. "
            "전문 용어는 반드시 괄호로 설명. "
            "걱정을 공감하고 해결책을 제시하는 흐름. "
            "'저도 처음엔~' 같은 공감 어법 적극 활용."
        ),
        "preferred_topics": ["초보자 추천 코스", "패키지 포함 항목", "예산 가이드", "준비물 체크리스트"],
    },

    "여행_중심_이대리": {
        "name": "여행 중심 이대리",
        "age": "35세",
        "job": "스타트업 직원",
        "background": "골프보다 여행이 목적. 파트너나 친구들과 함께 골프+관광 조합으로 계획 중.",
        "pain_points": [
            "골프만 치고 오는 일정은 아쉬움",
            "동행자 모두 만족할 코스+관광 조합 찾기 어려움",
            "예산이 한정적",
        ],
        "motivations": [
            "골프 + 현지 맛집·문화 체험 동시에",
            "SNS에 올릴 만한 비주얼과 경험",
            "합리적인 가격",
        ],
        "writing_style": (
            "감성적이고 경험 중심의 스토리텔링. "
            "장소의 분위기와 감각적 묘사 적극 활용. "
            "이모지 1~2개 자연스럽게 포함 가능. "
            "읽으면 '나도 가고 싶다' 욕구 자극."
        ),
        "preferred_topics": ["골프+관광 조합 코스", "현지 맛집", "계절 풍경", "인생샷 포인트"],
    },

    "VIP_최회장": {
        "name": "VIP 최회장",
        "age": "62세",
        "job": "대기업 임원 출신 자산가",
        "background": "일본 골프 10회 이상. 퍼블릭보다 회원제 프라이빗 코스 선호. 비용보다 품격 중시.",
        "pain_points": [
            "일반 패키지 수준에 만족 못함",
            "개인 맞춤 서비스 부재",
            "동행자 수준(비즈니스 파트너)에 맞는 코스 필요",
        ],
        "motivations": [
            "일본 최고 명문 코스 경험",
            "비즈니스 파트너 접대·관계 강화",
            "완전 맞춤형 프라이빗 일정",
        ],
        "writing_style": (
            "격식 있고 품격 있는 어조. "
            "과장 없이 고급스러운 어휘 사용. "
            "희소성과 프리미엄 경험을 자연스럽게 강조. "
            "독자를 이미 성공한 사람으로 대우하며 서술."
        ),
        "preferred_topics": ["프라이빗 명문 코스", "전용 캐디 서비스", "비즈니스 접대 골프", "프리미엄 숙소"],
    },
}


import json
from pathlib import Path

_CUSTOM_PATH = Path(__file__).parent / "personas_custom.json"


def load_custom_personas() -> dict:
    """사용자가 추가한 커스텀 페르소나 로드"""
    if _CUSTOM_PATH.exists():
        try:
            return json.loads(_CUSTOM_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_custom_persona(key: str, data: dict):
    """커스텀 페르소나 저장"""
    custom = load_custom_personas()
    custom[key] = data
    _CUSTOM_PATH.write_text(json.dumps(custom, ensure_ascii=False, indent=2), encoding="utf-8")


def delete_custom_persona(key: str):
    """커스텀 페르소나 삭제"""
    custom = load_custom_personas()
    if key in custom:
        del custom[key]
        _CUSTOM_PATH.write_text(json.dumps(custom, ensure_ascii=False, indent=2), encoding="utf-8")


def all_personas() -> dict:
    """기본 + 커스텀 페르소나 합쳐서 반환"""
    return {**PERSONAS, **load_custom_personas()}


def get_persona_prompt(persona_key: str) -> str:
    """페르소나 정보를 프롬프트 삽입용 문자열로 변환"""
    personas = all_personas()
    if not persona_key or persona_key not in personas:
        return ""
    p = personas[persona_key]
    pain = "\n".join([f"  - {x}" for x in p["pain_points"]])
    motive = "\n".join([f"  - {x}" for x in p["motivations"]])
    topics = ", ".join(p["preferred_topics"])
    return f"""
■ 타깃 페르소나 [이 사람을 위해 콘텐츠를 작성하세요]
- 이름/나이/직업: {p['name']} / {p['age']} / {p['job']}
- 배경: {p['background']}
- 불편함(Pain Points):
{pain}
- 동기(Motivations):
{motive}
- 관심 주제: {topics}
- 글 톤&스타일: {p['writing_style']}
"""


def list_personas() -> dict[str, str]:
    """UI 선택용: {key: 표시명} 반환 (기본 + 커스텀)"""
    return {k: v["name"] for k, v in all_personas().items()}
