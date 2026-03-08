import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- [공통] 데이터 저장 함수 ---
def save_survey(data):
    """설문 결과를 CSV 파일로 저장하는 함수. (컬럼 변경 대응)"""
    DATA_FILE = "survey_results.csv"
    data['제출시간'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_df = pd.DataFrame([data])
    
    if os.path.exists(DATA_FILE):
        try:
            old_df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
            combined_df = pd.concat([old_df, new_df], ignore_index=True)
            combined_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
        except pd.errors.ParserError:
            # 기존 파일 구조가 완전히 깨져서 읽을 수 없는 경우 백업하고 새로 생성
            backup_file = f"survey_results_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            os.rename(DATA_FILE, backup_file)
            new_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
    else:
        new_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# --- [공통] 폰트 크기 통일 설정 함수 (18px) ---
def apply_custom_font():
    """질문(라디오 레이블 등)과 답 선택지 옵션의 폰트 크기를 동일하게 강제 설정"""
    st.markdown("""
        <style>
        /* 기본 텍스트 폰트 크기 강제 */
        body, p, span, label, div {
            font-size: 18px !important;
        }
        
        /* 라디오 버튼 질문 (레이블) 크기 */
        div[data-testid="stMarkdownContainer"] p,
        .stRadio > label {
            font-size: 18px !important;
            font-weight: 600 !important;
            color: #31333F !important;
            margin-bottom: 8px !important;
        }

        /* 라디오 버튼 선택지 (옵션) 텍스트 크기 강제 */
        div[role="radiogroup"] label[data-baseweb="radio"] div {
            font-size: 16px !important;
        }
        
        /* 기기 폭에 맞춰 자연스럽게 줄바꿈이 일어나도록 수정 (잘림 방지) */
        div[role="radiogroup"] {
            flex-wrap: wrap !important;
            gap: 10px 15px !important; /* 위아래 10px, 좌우 15px 간격 */
            padding-bottom: 5px;
        }
        
        /* 특정 span에 직접 부여한 질문 클래스 (.survey-q) */
        .survey-q {
            font-size: 18px !important;
            font-weight: 600 !important;
            display: block;
            margin-bottom: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- [만 5세 - 만 7세 환자 본인용] ---
def show_instructions_5_7():
    st.info("💡 **인터뷰 진행자를 위한 지시사항**")
    st.markdown("""
    어린이들에게 문제가 될 수도 있는 것들에 대해 몇 가지 질문을 하겠습니다.
    - 😊 **전혀** 문제가 되지 않는다면, 웃는 얼굴을 가리키세요.
    - 😐 **가끔** 문제가 된다면, 가운데 얼굴을 가리키세요.
    - ☹️ **거의 항상** 문제가 된다면, 찡그린 얼굴을 가리키세요.
    """)
    with st.expander("✅ 연습 문항 진행하기 (필수)", expanded=True):
        st.write("**연습: 윙크하는 것이 어렵습니까?**")
        st.radio("아동의 응답을 선택하세요:", ["😊 전혀", "😐 가끔", "☹️ 거의 항상"], horizontal=True, key="practice_wink")

def peds_ql_5_7():
    apply_custom_font()
    responses = {}
    options = {"😊 전혀(0)": 0, "😐 가끔(2)": 2, "☹️ 거의 항상(4)": 4}
    st.subheader("📍 신체적 기능")
    p_items = ["걷기가 힘든가요?", "달리기가 힘든가요?", "스포츠나 운동을 하기 힘든가요?", "큰 물건을 들어올리기 힘든가요?", "목욕이나 샤워를 하는 것이 힘든가요?", "(장난감 정리 같은) 집안일을 하기가 힘든가요?", "아프거나 통증이 있나요?", "너무 피곤해서 놀지 못한 적이 있나요?"]
    for i, item in enumerate(p_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_p{i}", options.keys(), horizontal=True, key=f"p{i}", label_visibility="collapsed")
        responses[f"신체_{i}"] = options[res]
    st.divider()
    st.subheader("📍 정서적 기능")
    e_items = ["무서움을 느끼나요?", "슬픔을 느끼나요?", "화가 나나요?", "잠자는데 어려움이 있나요?", "걱정하나요?"]
    for i, item in enumerate(e_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_e{i}", options.keys(), horizontal=True, key=f"e{i}", label_visibility="collapsed")
        responses[f"정서_{i}"] = options[res]
    return responses

# --- [만 5세 - 만 7세 보호자용] ---
def show_instructions_parent():
    st.info("💡 **보호자(주양육자)를 위한 지시사항**")
    st.markdown("지난 한 달 동안 **귀하의 자녀**에게 다음 항목들이 얼마나 문제가 되었는지 정도를 선택해 주십시오.")

def peds_ql_parent_5_7():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}

    # 1. 신체적 기능
    st.subheader("📍 신체적 기능")
    p_items = [
        "단거리(100미터 이상) 걷기",
        "달리기",
        "활동적인 놀이나 운동에 참여하기",
        "무거운 것 들기",
        "혼자서 목욕이나 샤워하기",
        "장난감 정리 등 집안일",
        "아프거나 통증이 있음",
        "기운이 떨어짐"
    ]
    for i, item in enumerate(p_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_pp{i}", options.keys(), horizontal=True, key=f"parent_p{i}", label_visibility="collapsed")
        responses[f"보호자_신체_{i}"] = options[res]

    # 2. 정서적 기능
    st.subheader("📍 정서적 기능")
    e_items = [
        "두렵거나 무서워 함",
        "슬퍼함",
        "화를 냄",
        "잠자기 어려움",
        "자신에게 일어날 일에 대해 걱정함"
    ]
    for i, item in enumerate(e_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_pe{i}", options.keys(), horizontal=True, key=f"parent_e{i}", label_visibility="collapsed")
        responses[f"보호자_정서_{i}"] = options[res]

    # 3. 사회적 기능
    st.subheader("📍 사회적 기능")
    s_items = [
        "다른 아이들과 잘 지냄",
        "다른 아이들이 친구를 하려고 하지 않음",
        "다른 아이들에게 놀림 당함",
        "같은 연령대의 다른 아이들이 하는 것을 하지 못함",
        "다른 아이들과 놀 때 잘 따라감"
    ]
    for i, item in enumerate(s_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_ps{i}", options.keys(), horizontal=True, key=f"parent_s{i}", label_visibility="collapsed")
        responses[f"보호자_사회_{i}"] = options[res]

    # 4. 학교/어린이집에서의 생활/활동 능력
    st.subheader("📍 학교/어린이집에서의 생활/활동 능력")
    sch_items = [
        "수업 시간에 집중을 함",
        "건망증",
        "학교/어린이집 활동을 잘 따라감",
        "컨디션이 좋지 않아 학교/어린이집 결석",
        "의사의 진료를 받거나 병원에 가기 위해 학교/어린이집 결석"
    ]
    for i, item in enumerate(sch_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_psch{i}", options.keys(), horizontal=True, key=f"parent_sch{i}", label_visibility="collapsed")
        responses[f"보호자_학교_{i}"] = options[res]

    return responses

# --- [보호자용 추가 설문: CES-D] ---
def show_instructions_ces_d():
    """우울척도(CES-D) 지시사항"""
    st.info("💡 **추가 설문 지시사항 (CES-D)**")
    st.markdown("""
    **지난 1주 동안** 당신이 느끼고 행동한 것을 가장 잘 나타낸다고 생각되는 답변에 답해 주시기 바랍니다.
    """)
def ces_d_survey_20():
    """역학연구를 위한 우울척도(CES-D) 20문항"""
    responses = {}
    # 일반 문항 옵션 및 점수
    options = {"극히 드물게(1일 이하)": 0, "때로(1~2일)": 1, "상당히(3~4일)": 2, "대부분(5~7일)": 3}
    # 역채점 문항 옵션 (4, 8, 12, 16번)
    rev_options = {"극히 드물게(1일 이하)": 3, "때로(1~2일)": 2, "상당히(3~4일)": 1, "대부분(5~7일)": 0}
    st.subheader("📍 역학연구를 위한 우울척도 (CES-D)")
    questions = [
    "평소에는 성가시지 않았던 일이 성가시게 느껴졌다.", "별로 먹고 싶지 않았다. (입맛이 없었다.)",
    "가족이나 친구가 도와주더라도 울적한 기분을 떨칠 수 없었다.", "나도 다른 사람만큼 기분이 좋았다. (역채점)", # 4번
    "하고 있는 일에 마음을 집중하기 어려웠다.", "우울했다.", "하는 일마다 힘들게 느껴졌다.",
    "미래에 대해 희망적으로 느꼈다. (역채점)", # 8번
    "내 인생은 실패작이라고 생각했다.", "무서움을 느꼈다.", "잠을 설쳤다.",
    "행복했다. (역채점)", # 12번
    "평소보다 말을 적게 했다.", "외로움을 느꼈다.", "사람들이 불친절했다.",
    "인생이 즐거웠다. (역채점)", # 16번
    "울음을 터뜨린 적이 있었다.", "슬픔을 느꼈다.", "사람들이 나를 싫어한다고 느꼈다.",
    "일을 제대로 진척시킬 수 없었다."
    ]

    reverse_items = [4, 8, 12, 16]
    for i, q in enumerate(questions, 1):
        # 역채점 문항 번호에 해당하면 rev_options 사용
        current_options = rev_options if i in reverse_items else options
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_cesd_{i}", current_options.keys(), horizontal=True, key=f"cesd_{i}", label_visibility="collapsed")
        responses[f"CESD_{i}"] = current_options[res]

    return responses

# --- [보호자용 추가 설문 2: GAD-7] ---
def show_instructions_gad_7():
    """일반화된 불안장애 척도(GAD-7) 지시사항"""
    st.info("💡 **추가 설문 지시사항 (GAD-7)**")
    st.markdown("""
    **지난 2주 동안** 당신은 다음의 문제들로 인해서 얼마나 자주 방해를 받았습니까?
    """)
def gad_7_survey_7():
    """일반화된 불안장애 척도(GAD-7) 7문항"""
    responses = {}
    # 0~3점 척도 매핑
    options = {
    "전혀 방해받지 않았다(0)": 0,
    "며칠 동안 방해받았다(1)": 1,
    "자주 방해받았다(2)": 2,
    "거의 매일 방해받았다(3)": 3
    }
    st.subheader("📍 일반화된 불안장애 척도 (GAD-7)")
    questions = [
    "초조하거나 불안하거나 조마조마하게 느낀다.",
    "걱정하는 것을 멈추거나 조절할 수 없다.",
    "여러 가지 것들에 대해 걱정을 너무 많이 한다.",
    "편하게 있기가 어렵다.",
    "너무 안절부절못해서 가만히 있기가 힘들다.",
    "쉽게 짜증이 나거나 쉽게 성을 내게 된다.",
    "마치 끔찍한 일이 생길 것처럼 두렵게 느껴진다."
    ]
    for i, q in enumerate(questions, 1):
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_gad7_{i}", options.keys(), horizontal=True, key=f"gad7_{i}", label_visibility="collapsed")
        responses[f"GAD7_{i}"] = options[res]
    return responses

# --- [보호자용 추가 설문 3: FACE-IV (가족 관계)] ---
def show_instructions_face_iv():
    """가족 관계 척도(FACE-IV) 지시사항"""
    st.info("💡 **추가 설문 지시사항 (FACE-IV)**")
    st.markdown("""
    다음의 각 문항에서 **가족 분위기**에 대해 가장 잘 설명해주는 하나의 항목에 체크해 주십시오.
    """)
def face_iv_survey_20():
    """가족 관계 척도(FACE-IV) 20문항"""
    responses = {}
    # 1~5점 척도 매핑
    options = {"전혀 그렇지 않다(1)": 1, "거의 그렇지 않다(2)": 2, "때때로 그렇다(3)": 3, "자주 그렇다(4)": 4, "항상 그렇다(5)": 5}
    st.subheader("📍 가족 관계 척도 (FACE-IV)")
    questions = [
    "우리 가족은 서로 도움을 청한다.", "우리 가족은 문제를 해결할 때 자녀들의 의견을 존중한다.",
    "우리 가족은 각자의 친구들에 대해 인정해준다.", "우리 가족의 자녀들은 집안에서 지켜야할 규율에 대해 의견을 말할 수 있다.",
    "우리 가족은 우리 가족끼리만 일(여행, 외식, 집안 문제 결정 등)을 한다.", "우리 가족은 상황에 따라 식구 모두가 가장(지도자)의 역할을 한다.",
    "우리 가족은 가족 이외의 다른 사람보다 우리 가족 구성원에게 친근감을 느낀다.", "우리 가족은 문제를 해결하고자 할 때 여러 가지 방법을 함께 생각해본다.",
    "우리 가족은 여가시간을 가족구성원들과 함께 보내는 것을 좋아한다.", "우리 집에서 잘못한 일이 생겼을 때 부모와 자녀가 함께 모여 벌칙에 대해 토론한다.",
    "우리 가족은 서로 매우 친근감을 느낀다.", "우리 가족은 자녀들도 의사결정을 한다.",
    "우리 가족은 함께 할 활동(명절, 제사, 생일)이 있을 때 모두 참여한다.", "우리집에서는 정해놓은 규칙이 변하기도 한다.",
    "우리 가족은 가족 구성원이 함께 할 수 있는 일(취미, 오락)을 쉽게 생각해낸다.", "우리 가족은 집안일에 대해 교대로 책임을 맡긴다.",
    "우리 가족은 각자의 일을 결정할 때 식구들과 상의한다.", "우리 가족 중에서는 누가 가장인지 분간하기 어렵다.",
    "우리집에서는 가족이 함께 지낸다는 것이 매우 중요하다.", "우리집에서는 누가 집안일을 하는지 알기 어렵다."
    ]

    for i, q in enumerate(questions, 1):
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_face_{i}", options.keys(), horizontal=True, key=f"face_{i}", label_visibility="collapsed")
        responses[f"FACE_{i}"] = options[res]
    return responses
# --- [보호자용 추가 설문 4: PSOC (양육효능감)] ---
def show_instructions_psoc():
    """양육효능감(PSOC) 지시사항"""
    st.info("💡 **추가 설문 지시사항 (PSOC)**")
    st.markdown("""
    부모로서 어떻게 생각하는지 알고자 하는 질문입니다.
    부모(보호자)의 생각이나 느낌을 가장 잘 표현하는 칸을 선택해 주세요.
    """)
def psoc_survey_16():
    """양육효능감(PSOC) 16문항"""
    responses = {}
    # 1~5점 척도 매핑 (앞에서부터 1, 2, 3, 4, 5)
    options = {"전혀 아니다": 1, "조금 아니다": 2, "보통이다": 3, "그렇다": 4, "매우 그렇다": 5}
    # 역채점 문항 옵션 (4, 5, 6, 9, 10, 13, 16번) (역채점: 5, 4, 3, 2, 1)
    rev_options = {"전혀 아니다": 5, "조금 아니다": 4, "보통이다": 3, "그렇다": 2, "매우 그렇다": 1}
    st.subheader("📍 양육효능감 (PSOC)")
    questions = [
    "나는 나의 말과 행동이 아이에게 어떤 영향을 미치는지 알고 있다.", "나는 아이를 능숙하게 돌볼 수 있다고 생각한다.",
    "나는 아이가 어떤 부분에서 어려움을 보이는지 누구보다 잘 알고 있다.", "나는 아이가 현재 보이고 있는 행동이 발달과정상 그럴 수밖에 없다는 것을 알면서도 짜증이 난다. (역채점)",
    "내가 아이를 가르치고 이끌어 주려고 해도, 아이가 내 뜻대로 잘 따라오지 않아 좌절감을 느낀다. (역채점)", "나는 좋은 부모가 될 수 없을 것 같아 걱정이다. (역채점)",
    "나는 다른 사람들이 나로부터 좋은 부모역할을 배울 수 있는 괜찮은 모델이라고 생각한다.", "나는 아이와의 관계에서 생기는 문제를 잘 다룬다.",
    "나는 아이가 나를 좋은 부모라고 생각하는지 자신없다. (역채점)", "나는 부모로서 아이에게 해준 것이 없다고 느낀다. (역채점)",
    "나는 아이가 잘못했을 때, 아이 자신이 잘못한 점을 깨달을 수 있도록 잘 설명하고 지도한다.", "나는 부모로서 해야 할 일을 잘 하고 있다.",
    "나는 부모역할보다는 다른 분야에 더 흥미와 관심이 있다. (역채점)", "내가 좋은 부모가 되는 것에 조금이라도 더 흥미가 있다면, 나는 지금보다 좀 더 나은 부모가 될 수 있을 것이다.",
    "나는 좋은 부모가 되는 데 필요한 지식과 방법을 잘 알고 있다.", "부모로서 나는 긴장하고 있으며 불안하다. (역채점)"
    ]
    
    reverse_items = [4, 5, 6, 9, 10, 13, 16]
    for i, q in enumerate(questions, 1):
        # 역채점 문항 번호에 해당하면 rev_options 사용
        current_options = rev_options if i in reverse_items else options
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_psoc_{i}", current_options.keys(), horizontal=True, key=f"psoc_{i}", label_visibility="collapsed")
        responses[f"PSOC_{i}"] = current_options[res]
    return responses

# --- [만 8세 - 만 12세 환아 본인용] ---
import streamlit as st

def show_instructions_8_12():
    """만 8세 - 만 12세 환아 본인용 지시사항"""
    st.info("💡 **어린이(초등학생)를 위한 지시사항**")
    st.markdown("""
    다음 쪽에는 여러분에게 문제가 될 수 있는 일들이 나열되어 있습니다. 
    **지난 한 달 동안** 각각의 항목이 여러분에게 얼마나 문제가 되었는지 해당되는 숫자를 선택해 주세요.
    
    - **0**: 전혀 문제가 없다면
    - **1**: 거의 문제가 없다면
    - **2**: 가끔 문제가 있다면
    - **3**: 자주 문제가 있다면
    - **4**: 거의 항상 문제가 있다면
    """)

def peds_ql_8_12():
    """만 8세 - 만 12세 환아용 PedsQL 실제 문항 (질문 노출 수정본)"""
    responses = {}
    options = {
        "전혀 없음 (0)": 0, "거의 없음 (1)": 1, 
        "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4
    }

    # --- 1. 나의 건강 및 활동 (8문항) ---
    st.subheader("📍 1. 나의 건강 및 활동에 관하여")
    p_items = [
        "나는 100미터 이상 걷기 힘들다", "나는 달리는 것이 힘들다", 
        "나는 스포츠 활동이나 운동을 하기가 힘들다", "나는 무거운 것을 들기가 힘들다", 
        "나는 혼자서 목욕이나 샤워를 하기가 힘들다", "나는 집안일을 하는 것이 힘들다", 
        "나는 몸이 아프거나 통증이 있다", "나는 기운이 떨어진다"
    ]
    for i, item in enumerate(p_items, 1):
        # [수정] 질문 문항을 화면에 출력합니다.
        st.write(f"**{i}. {item}**") 
        res = st.radio(f"선택_{i}", options.keys(), horizontal=True, label_visibility="collapsed", key=f"child812_p{i}")
        responses[f"본인812_신체_{i}"] = options[res]

    # --- 2. 나의 기분에 관하여 (5문항) ---
    st.divider()
    st.subheader("📍 2. 나의 기분에 관하여")
    e_items = ["나는 두렵거나 무섭다", "나는 슬프다", "나는 화가 난다", "나는 잠자는데 어려움이 있다", "나는 나에게 무슨 일이 일어날지 걱정한다"]
    for i, item in enumerate(e_items, 1):
        # [수정] 질문 문항 출력
        st.write(f"**{i}. {item}**")
        res = st.radio(f"선택_e_{i}", options.keys(), horizontal=True, label_visibility="collapsed", key=f"child812_e{i}")
        responses[f"본인812_정서_{i}"] = options[res]

    # --- 3. 다른 사람들과 어울리기 (5문항) ---
    st.divider()
    st.subheader("📍 3. 다른 사람들과 어울리기")
    s_items = [
        "나는 다른 아이들과 어울리는 것이 어렵다", "다른 아이들이 나와 친구가 되고 싶어하지 않는다", 
        "다른 아이들이 나를 놀린다", "나와 같은 나이의 다른 아이들이 할 수 있는 것 중에 내가 하지 못하는 것이 있다", 
        "다른 아이들과 놀 때 잘 따라가기가 힘들다"
    ]
    for i, item in enumerate(s_items, 1):
        # [수정] 질문 문항 출력
        st.write(f"**{i}. {item}**")
        res = st.radio(f"선택_s_{i}", options.keys(), horizontal=True, label_visibility="collapsed", key=f"child812_s{i}")
        responses[f"본인812_사회_{i}"] = options[res]

    # --- 4. 학교에 관하여 (5문항) ---
    st.divider()
    st.subheader("📍 4. 학교에 관하여")
    sc_items = [
        "수업시간에 집중하기가 힘들다", "나는 무언가를 깜빡 잊어버린다", 
        "나는 학교 공부를 따라가기가 어렵다", "나는 몸이 좋지 않아 학교에 결석한다", 
        "나는 병원에 가느라 학교에 결석한다"
    ]
    for i, item in enumerate(sc_items, 1):
        # [수정] 질문 문항 출력
        st.write(f"**{i}. {item}**")
        res = st.radio(f"선택_sc_{i}", options.keys(), horizontal=True, label_visibility="collapsed", key=f"child812_sc{i}")
        responses[f"본인812_학교_{i}"] = options[res]

    return responses


# --- [어린이 우울척도 CES-DC] 20문항 ---
def show_instructions_ces_dc():
    """어린이용 CES-DC 지시사항"""
    st.subheader("어린이를 위한 역학연구 우울증 척도 (CES-DC)")
    st.info("💡 **어린이용 우울척도 지시사항**")
    st.markdown("""
    **지난 1주 동안** 자신이 느끼고 행동한 것을 가장 잘 나타낸다고 생각되는 숫자에 표시해 주시기 바랍니다.
    
    - **0**: 극히 드물게 (1일 이하)
    - **1**: 때로 (1~2일)
    - **2**: 상당히 (3~4일)
    - **3**: 대부분 (5~7일)
    """)

def ces_dc_survey_20():
    apply_custom_font()
    responses = {}
    options = {"극히 드물게(0)": 0, "때로(1)": 1, "상당히(2)": 2, "대부분(3)": 3}
    rev_options = {"극히 드물게(0)": 3, "때로(1)": 2, "상당히(2)": 1, "대부분(3)": 0}
    questions = [
        "평소에는 아무렇지도 않던 일들이 귀찮게 느껴졌다.", "먹고 싶지 않았다. 배가 고프지 않았다.",
        "내 기분이 나아지도록 가족과 친구들이 노력해도 즐겁지 않았다.", "나도 다른 아이들만큼 괜찮은 사람이라고 느꼈다. (역채점)", # 4번
        "내가 하는 일에 집중하기 어려웠다.", "기분이 울적하고 행복하지 않았다.", "무언가를 하기에 너무 피곤하게 느껴졌다.",
        "좋은 일이 일어날 것처럼 느껴졌다. (역채점)", # 8번
        "내가 예전에 했던 일이 잘 풀리지 않는다고 느껴졌다.",
        "무섭다고 느껴졌다.", "평소에 비해 잠을 잘 자지 못했다.", "행복했다. (역채점)", # 12번
        "나는 평소보다 조용했다.", "친구가 없는 듯 외롭게 느껴졌다.",
        "내가 아는 아이들이 친근하지 않거나 나랑 같이 있고 싶어하지 않는 것처럼 느꼈다.",
        "즐거웠다. (역채점)", # 16번
        "울고 싶은 마음이었다.", "슬펐다.", "사람들이 나를 좋아하지 않는 것처럼 느껴졌다.", "무언가를 시작하기가 어려웠다."
    ]
    st.subheader("📍 어린이 우울증 척도 (CES-DC)")
    
    reverse_items = [4, 8, 12, 16]
    for i, q in enumerate(questions, 1):
        current_options = rev_options if i in reverse_items else options
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_cesdc_{i}", current_options.keys(), horizontal=True, key=f"cesdc_{i}", label_visibility="collapsed")
        responses[f"CESDC_{i}"] = current_options[res]
    return responses



# --- [만 8세 - 만 12세 환아용: SCARED (불안)] ---
def show_instructions_scared():
    st.info("💡 **세 번째 설문 지시사항 (SCARED)**")
    st.markdown("**지난 3개월 동안** 여러분이 느끼는 감정에 대한 질문입니다. 자신에게 얼마나 해당되는지 판단해 주세요.")

def scared_survey_41():
    apply_custom_font()
    responses = {}
    options = {"전혀 그렇지 않다(0)": 0, "가끔 그렇다(1)": 1, "자주 그렇다(2)": 2}
    questions = [
        "겁이 나면 숨쉬기 어렵다", "학교에 가면 머리가 아프다", "잘 모르는 사람과 같이 있는 것이 싫다",
        "집을 떠나 자면 겁이 난다", "다른 사람이 나를 좋아하지 않을까 걱정한다", "겁이 나면 기절할 것 같다",
        "나는 늘 긴장된다", "부모님이 어딘가를 갈 때마다 따라가고 싶다", "사람들이 내가 긴장하고 있는 것처럼 보인다고 한다",
        "모르는 사람과 있으면 긴장된다", "학교에서 배가 아프다", "겁이 나면 미칠 것 같은 느낌이 든다",
        "나는 혼자 자는 것이 걱정된다", "다른 아이들만큼 잘할 수 있을지 걱정된다", "겁이 나면 세상이 비현실적으로 느껴진다",
        "부모님에게 안 좋은 일이 생길까 악몽을 꾼다", "학교에 가는 것이 걱정된다", "겁이 나면 심장이 빨리 뛴다",
        "몸이 떨린다", "나에게 안 좋은 일이 생기는 꿈을 꾼다", "일이 잘 안될까 걱정한다",
        "겁이 나면 땀이 난다", "나는 걱정이 많은 편이다", "특별한 이유 없이 겁이 날 때가 있다",
        "집에 혼자 있으면 무섭다", "모르는 사람과 이야기하는 것이 어렵다", "겁이 나면 숨을 쉴 수가 없다",
        "사람들이 나보고 걱정이 많다고 한다", "가족과 떨어지는 것이 싫다", "불안 발작이 올까 두렵다",
        "부모님에게 나쁜 일이 생길까 걱정한다", "모르는 사람 앞에서 부끄럽다", "미래에 무슨 일이 생길까 걱정된다",
        "겁이 나면 토할 것 같다", "내가 얼마나 잘하는지 걱정된다", "학교에 가는 것이 두렵다",
        "이미 지나간 일들이 계속 걱정된다", "겁이 나면 어지럽다", "많은 사람 앞에서 무언가를 해야 하면 긴장된다",
        "파티, 행사, 모르는 친구들이 있는 곳에 가면 긴장된다", "나는 수줍음이 많은 편이다"
    ]
    st.subheader("📍 아동 불안 관련 장애 척도 (SCARED)")
    for i, q in enumerate(questions, 1):
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_{i}", options.keys(), horizontal=True, key=f"scared_{i}", label_visibility="collapsed")
        responses[f"SCARED_{i}"] = options[res]
    return responses

# --- [만 8세 - 만 12세 환아용: RS-Y (회복탄력성)] ---
def show_instructions_rs_y():
    st.info("💡 **네 번째 설문 지시사항 (RS-Y)**")
    st.markdown("자신과 가장 가깝다고 생각되는 번호를 선택해 주세요.")

def rs_y_survey_17():
    apply_custom_font()
    responses = {}
    options = {"전혀 그렇지 않다(1)": 1, "그렇지 않다(2)": 2, "보통이다(3)": 3, "그렇다(4)": 4, "매우 그렇다(5)": 5}
    questions = [
        "나는 끈기가 있다는 말을 많이 듣는다", "내 주변 사람들은 내 기분을 잘 이해한다",
        "나는 친구와 의견이 부딪혀도 내 감정을 잘 조절할 수 있다", "나는 어떤 일을 시작할 때 결과를 미리 생각해본다",
        "나는 힘든 일도 끝까지 하는 편이다", "다른 사람들의 문제에 대해 쉽게 마음 아파한다",
        "문제가 생겼을 때 피하지 않고 그 문제를 해결하려고 한다", "서로 마음을 터놓고 편하게 얘기할 수 있는 친구가 많이 있다",
        "상대방이 화를 내더라도 내 기분대로 하기보다는 그 사람의 말을 먼저 들으려고 한다",
        "문제가 발생하면 해결방법에는 어떤 것들이 있을지 두루 살펴본다", "새로운 문제에 부딪혀도 나는 잘 처리해 나갈 수 있다",
        "나는 도움이 필요할 때 도움을 요청할 사람이 있다", "나는 문제가 생기면 나의 편이 되어줄 친구가 있다",
        "열심히 하면 언제나 보답이 있으리라고 생각한다", "문제가 생기면 그 이유를 파악하기 위해 과거에 일어났던 비슷한 일들을 생각해본다",
        "예상하지 못한 상황이 있어도 쉽게 포기하지 않는다", "나는 친구와 다른 생각을 가지고 있을 때 친구의 입장에서 생각해 보고 더 잘 이해하려고 노력한다",
        "나는 어려운 상황을 이겨낼 수 있는 능력이 있다", "나는 어려운 일이 닥쳤을 때 내 감정을 통제할 수 있다",
        "어려운 일이 생기면 그 원인이 무엇인지 신중하게 생각한다", "내 주변 사람들은 대부분 나를 좋아하는 편이다",
        "누군가에게 화가 날 때 잠시나마 그 사람의 입장이 되려고 노력한다", "나는 내 미래에 대한 희망을 가지고 있다",
        "나는 내 주변 사람들로부터 사랑과 관심을 받고 있다", "나에게는 항상 기회가 있다고 느낀다",
        "나는 목표가 정해지면 시간이 오래 걸려도 꾸준히 한다", "나는 대부분의 상황에 잘 대응할 수 있다",
        "나는 화가 날 때도 참을 수 있다", "어려움이 많더라도 언젠가는 반드시 내 꿈을 이룰 것이다",
        "나는 내 자신을 믿는다", "남을 비난하기 전에 내가 만일 그 사람의 입장이었다면 어땠을까 생각해본다",
        "친구가 억울한 일을 당하면 나도 속이 상한다", "나는 한번 시작한 일은 끝까지 해낸다",
        "나는 방해를 받아도 하고 있는 일에 계속 집중할 수 있다", "나는 기분이 나빠도 내 기분을 잘 드러내지 않는다",
        "어떤 결정을 내리기 전에 다른 의견을 가진 사람의 입장에서 생각하려고 노력한다", "나는 힘든 일이 생겨도 앞으로 잘 될 것이라고 생각한다"]
    st.subheader("📍 아동청소년 회복탄력성 척도 (RS-Y)")
    for i, q in enumerate(questions, 1):
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_{i}", options.keys(), horizontal=True, key=f"rsy_{i}", label_visibility="collapsed")
        responses[f"RSY_{i}"] = options[res]
    return responses

# --- [만 8세 - 만 12세 보호자용: PedsQL] ---
def show_instructions_parent_8_12():
    st.info("💡 **보호자용 설문 지시사항**")
    st.markdown("지난 한 달 동안 **아이의 건강과 활동**에 있어 다음의 항목들이 얼마나 문제가 되었는지 선택해 주세요. (0: 전혀 문제없음 ~ 4: 거의 항상 문제임)")

def peds_ql_parent_8_12():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}

    st.markdown("### 지난 한 달 동안 다음 항목이 귀하의 자녀에게 얼마나 문제가 되었습니까?")

    # 1. 신체적 기능
    st.subheader("📍 신체적 기능")
    p_items = [
        "단거리(100미터 이상) 걷기",
        "달리기",
        "활동적인 놀이나 운동에 참여하기",
        "무거운 것 들기",
        "혼자서 목욕이나 샤워하기",
        "집안일 하기",
        "아프거나 통증이 있음",
        "기운이 떨어짐"
    ]
    for i, item in enumerate(p_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_8p{i}", options.keys(), horizontal=True, key=f"parent8_p{i}", label_visibility="collapsed")
        responses[f"보호자812_신체_{i}"] = options[res]

    # 2. 정서적 기능
    st.subheader("📍 정서적 기능")
    e_items = [
        "두렵거나 무서워 함",
        "슬퍼함",
        "화를 냄",
        "잠자기 어려움",
        "자신에게 일어날 일에 대해 걱정함"
    ]
    for i, item in enumerate(e_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_8e{i}", options.keys(), horizontal=True, key=f"parent8_e{i}", label_visibility="collapsed")
        responses[f"보호자812_정서_{i}"] = options[res]

    # 3. 사회적 기능
    st.subheader("📍 사회적 기능")
    s_items = [
        "다른 아이들과 잘 지냄",
        "다른 아이들이 친구를 하려고 하지 않음",
        "다른 아이들에게 놀림 당함",
        "같은 연령대의 다른 아이들이 하는 것을 하지 못함",
        "다른 아이들과 놀 때 잘 따라감"
    ]
    for i, item in enumerate(s_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_8s{i}", options.keys(), horizontal=True, key=f"parent8_s{i}", label_visibility="collapsed")
        responses[f"보호자812_사회_{i}"] = options[res]

    # 4. 학교에서의 생활/활동 능력
    st.subheader("📍 학교에서의 생활/활동 능력")
    sch_items = [
        "수업 시간에 집중을 함",
        "건망증",
        "학교 활동을 잘 따라감",
        "컨디션이 좋지 않아 학교 결석",
        "의사의 진료를 받거나 병원에 가기 위해 학교 결석"
    ]
    for i, item in enumerate(sch_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_8sch{i}", options.keys(), horizontal=True, key=f"parent8_sch{i}", label_visibility="collapsed")
        responses[f"보호자812_학교_{i}"] = options[res]

    return responses


# --- [만 13세 - 만 18세 환아 본인용: PedsQL] ---

def show_instructions_13_18():
    """만 13세 - 만 18세 환아 본인용 지시사항"""
    st.info("💡 **환아 본인를 위한 지시사항**")
    st.markdown("다음은 여러분에게 문제가 될 수 있는 일들이 나열되어 있습니다. **지난 한 달 동안** 각각의 항목이 여러분에게 얼마나 문제가 되었는지 해당되는 숫자를 선택해 주세요.")

def peds_ql_13_18():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}
    sections = {
        "신체적 기능": ["100미터 이상 걷기", "달리기", "스포츠 활동이나 운동", "무거운 것 들기", "혼자서 목욕이나 샤워하기", "집안일 하기", "몸의 통증", "기운이 없음"],
        "정서적 기능": ["두렵거나 무섭다", "슬프다", "화가 난다", "잠자는데 어려움이 있다", "나에게 무슨 일이 일어날지 걱정한다"],
        "사회적 기능": ["다른 십대 아이들과 어울리는 것이 어렵다", "다른 십대 아이들이 나와 친구가 되고 싶어하지 않는다", "다른 십대 아이들이 나를 놀린다", "또래의 십대 아이들이 보통 할 수 있는 일을 하지 못한다", "보통의 또래들을 잘 따라가지 못한다"]
    }
    for section, items in sections.items():
        st.subheader(f"📍 {section}")
        for i, item in enumerate(items, 1):
            st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
            res = st.radio(f"q_{section}_{i}", options.keys(), horizontal=True, key=f"teen_{section}_{i}", label_visibility="collapsed")
            responses[f"본인1318_{section}_{i}"] = options[res]
    return responses

# --- [만 13세 - 만 18세 보호자용: PedsQL] ---
def show_instructions_parent_13_18():
    st.info("💡 **보호자(부모용) 설문 지시사항**")
    st.markdown("지난 한 달 동안 귀하의 십대 자녀에게 다음 항목들이 얼마나 문제가 되었는지 그 정도를 선택해 주십시오.")

def peds_ql_parent_13_18():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}

    st.markdown("### 지난 한 달 동안 다음 항목이 귀하의 십대 자녀에게 얼마나 문제가 되었습니까?")

    # 1. 신체적 기능
    st.subheader("📍 신체적 기능")
    p_items = [
        "단거리(100미터 이상) 걷기",
        "달리기",
        "활동적인 놀이나 운동에 참여하기",
        "무거운 것 들기",
        "혼자서 목욕이나 샤워하기",
        "집안일 하기",
        "아프거나 통증이 있음",
        "기운이 떨어짐"
    ]
    for i, item in enumerate(p_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_13p{i}", options.keys(), horizontal=True, key=f"parent13_p{i}", label_visibility="collapsed")
        responses[f"보호자1318_신체_{i}"] = options[res]

    # 2. 정서적 기능
    st.subheader("📍 정서적 기능")
    e_items = [
        "두렵거나 무서워 함",
        "슬퍼함",
        "화를 냄",
        "잠자기 어려움",
        "자신에게 일어날 일에 대해 걱정함"
    ]
    for i, item in enumerate(e_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_13e{i}", options.keys(), horizontal=True, key=f"parent13_e{i}", label_visibility="collapsed")
        responses[f"보호자1318_정서_{i}"] = options[res]

    # 3. 사회적 기능
    st.subheader("📍 사회적 기능")
    s_items = [
        "다른 십대들과 잘 지냄",
        "다른 십대들이 친구를 하려고 하지 않음",
        "다른 십대들에게 놀림 당함",
        "또래의 다른 십대들이 하는 것을 하지 못함",
        "다른 십대들과 놀 때 잘 따라감"
    ]
    for i, item in enumerate(s_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_13s{i}", options.keys(), horizontal=True, key=f"parent13_s{i}", label_visibility="collapsed")
        responses[f"보호자1318_사회_{i}"] = options[res]

    # 4. 학교에서의 생활/활동 능력
    st.subheader("📍 학교에서의 생활/활동 능력")
    sch_items = [
        "수업 시간에 집중을 함",
        "건망증",
        "학교 활동을 잘 따라감",
        "컨디션이 좋지 않아 학교 결석",
        "의사의 진료를 받거나 병원에 가기 위해 학교 결석"
    ]
    for i, item in enumerate(sch_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_13sch{i}", options.keys(), horizontal=True, key=f"parent13_sch{i}", label_visibility="collapsed")
        responses[f"보호자1318_학교_{i}"] = options[res]

    return responses

    # --- [만 19세 - 만 25세 청년 본인용] ---
def show_instructions_18_25():
    st.info("💡 **청년(19-25세)을 위한 지시사항**")
    st.markdown("다음은 여러분에게 문제가 될 수 있는 일들입니다. **지난 한 달 동안** 각각의 항목이 여러분에게 얼마나 문제가 되었는지 해당되는 숫자에 표시해 주세요.")

def peds_ql_18_25():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}
    
    sections = {
        "나의 건강 및 활동에 관하여 (다음과 같은 문제가...)": [
        "나는 100 미터 이상 걷기 힘들다",
        "나는 달리는 것이 힘들다",
        "나는 스포츠 활동이나 운동을 하기가 힘들다",
        "나는 무거운 것을 들기가 힘들다",
        "나는 혼자서 목욕이나 샤워를 하기가 힘들다",
        "나는 집안일을 돕는 것이 힘들다",
        "나는 몸이 아프거나 통증이 있다",
        "나는 기운이 떨어진다"
    ],
    "나의 기분에 관하여 (다음과 같은 문제가...)": [
        "나는 두렵거나 무섭다",
        "나는 슬프다",
        "나는 화가 난다",
        "나는 잠자는 데 어려움이 있다",
        "나는 나에게 무슨 일이 일어날지 걱정한다"
    ],
    "다른 사람들과 어울리기 (다음과 같은 문제가...)": [
        "나는 다른 성인들과 어울리기가 힘들다",
        "다른 성인들이 나와 친구가 되고 싶어하지 않는다",
        "다른 성인들이 나를 놀린다",
        "나와 같은 나이의 다른 사람들이 할 수 있는 것 중에 내가 하지 못하는 것이 있다",
        "나는 또래들을 잘 따라가기가 힘들다"
    ],
    "나의 직업/학업에 관하여 (다음과 같은 문제가...)": [
        "직장 또는 학교에서 집중하기가 힘들다",
        "나는 무언가를 깜빡 잊어버린다",
        "나는 직장 업무 또는 학업을 따라가기가 어렵다",
        "나는 몸이 좋지 않아 직장에 결근하거나 학교에 결석한다",
        "나는 의사를 보러 가거나 병원에 가느라 직장에 결근하거나 학교에 결석한다"
    ]
    }
    for sec_name, items in sections.items():
        st.subheader(f"📍 {sec_name}")
        for i, item in enumerate(items, 1):
            st.markdown(f'<span class="survey-q">{i}. 나는 {item} 것이 힘들다.</span>', unsafe_allow_html=True)
            res = st.radio(f"q_young_{sec_name}_{i}", options.keys(), horizontal=True, key=f"young_{sec_name}_{i}", label_visibility="collapsed")
            responses[f"본인1825_{sec_name}_{i}"] = options[res]
    return responses

# --- [청년용 추가 설문: RS (회복탄력성)] ---
def show_instructions_rs_19():
    st.info("💡 **추가 설문 지시사항 (RS)**")
    st.markdown("자신과 같거나 가깝다고 생각되는 번호에 표시해 주시기 바랍니다.")

def rs_survey_19():
    apply_custom_font()
    responses = {}
    options = {"전혀 아니다(1)": 1, "아니다(2)": 2, "보통이다(3)": 3, "그렇다(4)": 4, "매우 그렇다(5)": 5}
    questions = [
        "나는 끈기가 있다는 말을 많이 듣는다", "내 주변 사람들은 내 기분을 잘 이해한다", "나는 친구와 의견이 부딪혀도 내 감정을 잘 조절할 수 있다",
        "나는 어떤 일을 시작할 때 결과를 미리 생각해본다", "나는 힘든 일도 끝까지 하는 편이다", "다른 사람들의 문제에 대해 쉽게 마음 아파한다",
        "문제가 생겼을 때 피하지 않고 그 문제를 해결하려고 한다", "서로 마음을 터놓고 편하게 얘기할 수 있는 친구가 많이 있다",
        "상대방이 화를 내더라도 내 기분대로 하기보다는 그 사람의 말을 먼저 들으려고 한다", "문제가 발생하면 해결방법에는 어떤 것들이 있을지 두루 살펴본다",
        "새로운 문제에 부딪혀도 나는 잘 처리해 나갈 수 있다", "나는 도움이 필요할 때 도움을 요청할 사람이 있다", "나는 문제가 생기면 나의 편이 되어줄 친구가 있다",
        "열심히 하면 언제나 보답이 있으리라고 생각한다", "문제가 생기면 그 이유를 파악하기 위해 과거에 일어났던 비슷한 일들을 생각해본다",
        "예상하지 못한 상황이 있어도 쉽게 포기하지 않는다", "나는 친구와 다른 생각을 가지고 있을 때 친구의 입장에서 생각해 보고 더 잘 이해하려고 노력한다",
        "나는 어려운 상황을 이겨낼 수 있는 능력이 있다", "나는 어려운 일이 닥쳤을 때 내 감정을 통제할 수 있다", "어려운 일이 생기면 그 원인이 무엇인지 신중하게 생각한다",
        "내 주변 사람들은 대부분 나를 좋아하는 편이다", "누군가에게 화가 날 때 잠시나마 그 사람의 입장이 되려고 노력한다", "나는 내 미래에 대한 희망을 가지고 있다",
        "나는 내 주변 사람들로부터 사랑과 관심을 받고 있다", "나에게는 항상 기회가 있다고 느낀다", "나는 목표가 정해지면 시간이 오래 걸려도 꾸준히 한다",
        "나는 대부분의 상황에 잘 대응할 수 있다", "나는 화가 날 때도 참을 수 있다", "어려움이 많더라도 언젠가는 반드시 내 꿈을 이룰 것이다", "나는 내 자신을 믿는다",
        "친구가 억울한 일을 당하면 나도 속이 상한다", "나는 한번 시작한 일은 끝까지 해낸다", "나는 방해를 받아도 하고 있는 일에 계속 집중할 수 있다", "나는 기분이 나빠도 내 기분을 잘 드러내지 않는다",
        "나는 힘든 일이 생겨도 앞으로 잘 될 것이라고 생각한다"
    ]
    st.subheader("📍 회복탄력성 척도 (RS)")
    for i, q in enumerate(questions, 1):
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_rs19_{i}", options.keys(), horizontal=True, key=f"rs19_{i}", label_visibility="collapsed")
        responses[f"RS19_{i}"] = options[res]
    return responses

# --- [만 26세 이상 성인 환자 본인용 PedsQL] ---
def show_instructions_adult():
    st.info("💡 **성인용 삶의 질 조사 지시사항**")
    st.markdown("다음 항목이 **지난 한 달 동안** 귀하에게 얼마나 문제가 되었는지 해당되는 숫자를 선택해 주세요.")

def peds_ql_adult():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}
    
    sections = {
        "신체적 기능": ["100미터 이상 걷기", "달리기", "스포츠 활동이나 운동", "무거운 것 들기", "혼자서 목욕이나 샤워하기", "집안일 하기", "통증이나 아픔", "기운이 없음"],
        "정서적 기능": ["두렵거나 무섭다", "슬프다", "화가 난다", "잠자는 데 어려움이 있다", "나에게 무슨 일이 일어날지 걱정한다"],
        "사회적 기능": ["다른 성인들과 어울리는 것이 힘들다", "다른 사람들이 나와 시간을 보내고 싶어하지 않는 것 같다", "다른 사람들이 나를 놀린다", "내 또래의 사람들이 보통 할 수 있는 일을 하지 못한다", "다른 사람들과 보조를 맞추기가 힘들다"],
        "직업 및 학업 기능": ["직장 업무나 학교 수업에 집중하기가 힘들다", "일을 하거나 수업 중에 내용을 잊어버린다", "직장 업무나 학교 공부를 따라가기가 힘들다", "몸 상태가 좋지 않아 직장에 결근하거나 학교에 결석한다", "병원에 가느라 직장에 결근하거나 학교에 결석한다"]
    }

    for sec_name, items in sections.items():
        st.subheader(f"📍 {sec_name}")
        for i, item in enumerate(items, 1):
            st.markdown(f'<span class="survey-q">{i}. 나는 {item} 것이 힘들다.</span>', unsafe_allow_html=True)
            res = st.radio(f"q_adult_{sec_name}_{i}", options.keys(), horizontal=True, key=f"adult_{sec_name}_{i}", label_visibility="collapsed")
            responses[f"성인_{sec_name}_{i}"] = options[res]
    return responses



# --- [주관적 신체 활동 평가 (8세 이상 본인용)] ---
def show_instructions_physical_activity():
    st.info("💡 **주관적 신체 활동 평가**")
    st.markdown("다음 질문은 귀하의 평소 신체 활동량에 대한 질문입니다.")

def physical_activity_survey():
    apply_custom_font()

    responses = {}
    options = {
        "0일": 0, "1일": 1, "2일": 2, "3일": 3,
        "4일": 4, "5일": 5, "6일": 6, "7일": 7
    }
    
    st.subheader("📍 주관적 신체 활동 평가")
    q = "평균적인 한 주 동안, 하루 60분 이상 몸을 움직이며 활동하는 날이 며칠이나 되나요?"
    st.markdown(f'<span class="survey-q">{q}</span>', unsafe_allow_html=True)
    res = st.radio("q_pa_1", options.keys(), horizontal=True, key="pa_1", label_visibility="collapsed")
    responses["신체활동_일수"] = options[res]
    
    return responses

# --- [만 1~12개월 영아 보호자용 PedsQL] ---
def show_instructions_infant_1_12m():
    st.info("💡 **영아(1~12개월) 보호자 설문 지시사항**")
    st.markdown("다음은 귀하의 아기에게 문제가 될 수 있는 항목들입니다. **지난 한 달 동안** 각 항목이 아기에게 얼마나 문제가 되었는지 선택해 주십시오.")

def peds_ql_infant_1_12m():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}

    st.markdown("### 지난 한 달 동안 다음 항목이 여러분의 자녀에게 얼마나 문제가 되었습니까?")

    # 1. 신체적 기능
    st.subheader("📍 신체적 기능")
    p_items = [
        "기운이 떨어짐",
        "활동적인 놀이에 참여하기 힘듦",
        "아프거나 통증이 있음",
        "피곤해 함",
        "무기력함",
        "많이 쉼"
    ]
    for i, item in enumerate(p_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_inf_p{i}", options.keys(), horizontal=True, key=f"inf1_p{i}", label_visibility="collapsed")
        responses[f"보호자_영아12m_신체_{i}"] = options[res]

    # 2. 신체적 증상
    st.subheader("📍 신체적 증상")
    sym_items = [
        "배에 가스가 참",
        "먹은 후 게움",
        "숨쉬기 힘들어 함",
        "배탈이 남",
        "삼키기 힘듦",
        "변비가 있음",
        "발진이 있음",
        "설사를 함",
        "숨을 쉴 때 쌕쌕거리는 소리가 남",
        "구토를 함"
    ]
    for i, item in enumerate(sym_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_inf_sym{i}", options.keys(), horizontal=True, key=f"inf1_sym{i}", label_visibility="collapsed")
        responses[f"보호자_영아12m_신체증상_{i}"] = options[res]

    # 3. 정서적 기능
    st.subheader("📍 정서적 기능")
    e_items = [
        "두렵거나 무서워 함",
        "화를 냄",
        "혼자 있을 때 울거나 짜증을 냄",
        "화가 났을 때 스스로 진정하기 힘듦",
        "잠들기 어려움",
        "안아줄 때 울거나 짜증을 냄",
        "슬퍼함",
        "안아서 달래 주어도 진정하기 힘듦",
        "밤새도록 잠을 설침",
        "많이 욺",
        "짜증이 나 있음",
        "낮잠을 잘 못 잠"
    ]
    for i, item in enumerate(e_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_inf_e{i}", options.keys(), horizontal=True, key=f"inf1_e{i}", label_visibility="collapsed")
        responses[f"보호자_영아12m_정서_{i}"] = options[res]

    return responses

# --- [만 13~24개월 영유아 보호자용 PedsQL] ---
def show_instructions_infant_13_24m():
    st.info("💡 **영유아(13~24개월) 보호자 설문 지시사항**")
    st.markdown("지난 한 달 동안 **귀하의 자녀**에게 다음의 항목들이 얼마나 문제가 되었는지 해당되는 숫자를 선택해 주십시오.")

def peds_ql_infant_13_24m():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}

    st.markdown("### 지난 한 달 동안 다음 항목이 여러분의 자녀에게 얼마나 문제가 되었습니까?")

    # 1. 신체적 기능 (9문항 - 1-12개월과 다름)
    st.subheader("📍 신체적 기능")
    p_items = [
        "기운이 떨어짐",
        "활동적인 놀이에 참여하기 힘듦",
        "아프거나 통증이 있음",
        "피곤해 함",
        "무기력함",
        "많이 쉼",
        "너무 피곤해서 잘 놀지 못 함",
        "걷기 힘듦",
        "넘어지지 않고 짧은 거리를 달리기 힘듦"
    ]
    for i, item in enumerate(p_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_inf2_p{i}", options.keys(), horizontal=True, key=f"inf2_p{i}", label_visibility="collapsed")
        responses[f"보호자_영아24m_신체_{i}"] = options[res]

    # 2. 신체적 증상 (10문항 - 동일)
    st.subheader("📍 신체적 증상")
    sym_items = [
        "배에 가스가 참",
        "먹은 후 게움",
        "숨쉬기 힘들어 함",
        "배탈이 남",
        "삼키기 힘듦",
        "변비가 있음",
        "발진이 있음",
        "설사를 함",
        "숨을 쉴 때 쌕쌕거리는 소리가 남",
        "구토를 함"
    ]
    for i, item in enumerate(sym_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_inf2_sym{i}", options.keys(), horizontal=True, key=f"inf2_sym{i}", label_visibility="collapsed")
        responses[f"보호자_영아24m_신체증상_{i}"] = options[res]

    # 3. 정서적 기능 (12문항 - 동일)
    st.subheader("📍 정서적 기능")
    e_items = [
        "두렵거나 무서워 함",
        "화를 냄",
        "혼자 있을 때 울거나 짜증을 냄",
        "화가 났을 때 스스로 진정하기 힘듦",
        "잠자기 어려움",
        "안아줄 때 울거나 짜증을 냄",
        "슬퍼함",
        "안아서 달래 주어도 진정하기 힘듦",
        "밤새도록 잠을 설침",
        "많이 욺",
        "짜증이 나 있음",
        "낮잠을 잘 못 잠"
    ]
    for i, item in enumerate(e_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_inf2_e{i}", options.keys(), horizontal=True, key=f"inf2_e{i}", label_visibility="collapsed")
        responses[f"보호자_영아24m_정서_{i}"] = options[res]

    return responses

# --- [만 2세 - 만 4세 유아 보호자용 PedsQL] ---
def show_instructions_toddler_2_4y():
    st.info("💡 **유아(2-4세) 보호자 설문 지시사항**")
    st.markdown("지난 한 달 동안 각각의 항목이 **여러분의 자녀**에게 얼마나 문제가 되었는지 해당되는 숫자에 표시해주세요.")

def peds_ql_toddler_2_4y():
    apply_custom_font()
    responses = {}
    options = {"전혀 없음 (0)": 0, "거의 없음 (1)": 1, "가끔 있음 (2)": 2, "자주 있음 (3)": 3, "거의 항상 있음 (4)": 4}

    st.markdown("### 지난 한 달 동안 다음 항목이 여러분의 자녀에게 얼마나 문제가 되었습니까?")

    # 1. 신체적 기능
    st.subheader("📍 신체적 기능")
    p_items = [
        "걷기",
        "달리기",
        "활동적인 놀이나 운동에 참여하기",
        "무거운 것 들기",
        "목욕",
        "장난감 정리 거들기",
        "아프거나 통증이 있음",
        "기운이 떨어짐"
    ]
    for i, item in enumerate(p_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_tod_p{i}", options.keys(), horizontal=True, key=f"tod_p{i}", label_visibility="collapsed")
        responses[f"보호자_유아24y_신체_{i}"] = options[res]

    # 2. 정서적 기능
    st.subheader("📍 정서적 기능")
    e_items = [
        "두렵거나 무서워 함",
        "슬퍼함",
        "화를 냄",
        "잠자기 어려움",
        "걱정함"
    ]
    for i, item in enumerate(e_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_tod_e{i}", options.keys(), horizontal=True, key=f"tod_e{i}", label_visibility="collapsed")
        responses[f"보호자_유아24y_정서_{i}"] = options[res]

    # 3. 사회적 기능
    st.subheader("📍 사회적 기능")
    s_items = [
        "다른 아이들과 함께 놀기",
        "다른 아이들이 같이 놀고 싶어하지 않음",
        "다른 아이들에게 놀림 당함",
        "같은 연령대의 다른 아이들이 하는 것을 하지 못 함",
        "다른 아이들과 놀 때 잘 따라감"
    ]
    for i, item in enumerate(s_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_tod_s{i}", options.keys(), horizontal=True, key=f"tod_s{i}", label_visibility="collapsed")
        responses[f"보호자_유아24y_사회_{i}"] = options[res]

    # 4. 학교/기관에서의 기능 (선택 항목)
    st.markdown("---")
    st.markdown("**✅ 아래 항목은 자녀가 학교나 어린이집에 다니는 경우에만 작성해주십시오.**")
    st.subheader("📍 학교/기관에서의 기능")
    sch_items = [
        "또래들과 똑같은 학교/어린이집 활동을 함",
        "몸이 좋지 않아 학교/어린이집 결석",
        "병원에 가기 위해 학교/어린이집 결석"
    ]
    for i, item in enumerate(sch_items, 1):
        st.markdown(f'<span class="survey-q">{i}. {item}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_tod_sch{i}", options.keys(), horizontal=True, key=f"tod_sch{i}", label_visibility="collapsed")
        responses[f"보호자_유아24y_학교_{i}"] = options[res]

    return responses

# --- [소아청소년과 증상 체크 리스트 (PSC-35)] ---
def show_instructions_psc():
    st.info("💡 **소아청소년과 증상 체크 리스트 (PSC) 지시사항**")
    st.markdown("귀하의 자녀를 가장 잘 나타내는 항목에 체크해 주시기 바랍니다.")

def psc_symptom_survey_35():
    apply_custom_font()
    responses = {}
    options = {"전혀 그렇지 않다(0)": 0, "때때로 그렇다(1)": 1, "자주 그렇다(2)": 2}
    
    questions = [
        "통증과 고통을 호소함", "더 많은 시간을 혼자서 보냄", "쉽게 지치고, 에너지가 별로 없음", 
        "안절부절 못하고, 가만히 앉아있지 못함", "선생님과의 사이에 문제가 있음", "학교에 관심이 별로 없음", 
        "몸에 모터가 있는 것처럼 행동함", "멍하게 있는 시간이 지나치게 많음", "쉽게 주의가 산만해짐", 
        "새로운 상황을 두려워함", "슬프고 기분이 좋지 않음", "짜증이 나고 화가 남", 
        "희망이 없다고 느낌", "집중하는 것이 어려움", "친구에 별로 관심이 없음", 
        "다른 아이들과 싸움", "학교에 결석함", "학교 성적이 떨어짐", 
        "자존감이 낮음", "의사를 만나 봐도 별다른 문제를 찾지 못함", "수면에 어려움이 있음", 
        "걱정이 많음", "전보다 더 부모와 함께 있기를 원함", "자신이 나쁘다고 느낌", 
        "불필요한 위험을 감수함", "자주 상처를 받음", "재미를 느끼지 못하는 것처럼 보임", 
        "같은 나이의 다른 또래보다 더 어리게 행동함", "규칙을 따르지 않음", "감정을 보이지 않음", 
        "다른 사람들의 감정을 이해하지 못함", "다른 사람들을 괴롭힘", "자신의 문제에 대해 다른 이들을 탓함", 
        "자신의 것이 아닌 물건들을 가져감", "함께 나누어 쓰기를 거부함"
    ]

    st.subheader("📍 증상 체크 리스트 (35개 항목)")
    for i, q in enumerate(questions, 1):
        st.markdown(f'<span class="survey-q">{i}. {q}</span>', unsafe_allow_html=True)
        res = st.radio(f"q_psc_{i}", options.keys(), horizontal=True, key=f"psc_{i}", label_visibility="collapsed")
        responses[f"PSC_증상_{i}"] = options[res]
    return responses
