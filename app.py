import streamlit as st
import pandas as pd
import os
from datetime import datetime
import surveys

# --- 1. 세션 상태 초기화 ---
if 'step' not in st.session_state:
    st.session_state.step = 'name_input'
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'completed_targets' not in st.session_state:
    st.session_state.completed_targets = []
if 'all_responses' not in st.session_state:
    st.session_state.all_responses = {}
if 'sub_step' not in st.session_state:
    st.session_state.sub_step = 1

st.title("🏥 일차성 부정맥 환자-보호자 통합 삶의 질 조사")
# 전체 페이지 기본 폰트 크기 및 스타일 통일 적용
surveys.apply_custom_font()

# 화면 전환 시 맨 위로 스크롤하기 위한 상태 관리
if 'last_scroll_target' not in st.session_state:
    st.session_state.last_scroll_target = ("", 0)

current_scroll_target = (st.session_state.step, st.session_state.get('sub_step', 0))

if st.session_state.last_scroll_target != current_scroll_target:
    st.session_state.last_scroll_target = current_scroll_target
    
    # 화면 상단으로 포커스를 맞추기 위한 투명 앵커 삽입
    st.markdown("<div id='top'></div>", unsafe_allow_html=True)
    
    import streamlit.components.v1 as components
    import time
    
    # 렌더링 즉시 앵커로 이동하도록 해킹 방법 사용
    components.html(
        f"""
        <script>
            // DOM 요소들이 완전히 렌더링된 후 실행되도록 지연
            setTimeout(function() {{
                const link = window.parent.document.createElement('a');
                link.href = '#top';
                window.parent.document.body.appendChild(link);
                link.click();
                window.parent.document.body.removeChild(link);
            }}, 100);
        </script>
        <!-- {time.time()} -->
        """,
        height=0
    )

# --- 2. 메인 로직 흐름 ---

# STEP 1: 기본 정보 및 연령 선택
if st.session_state.step == 'name_input':
    st.header("1. 환자의 기본 정보 및 연령대 선택")
    col_name, col_age = st.columns([3, 1])
    with col_name:
        # 브라우저 자동완성을 방지하기 위해 autocomplete="new-password" 사용 (또는 "off")
        patient_name = st.text_input("환자 성함", placeholder="성함 입력", autocomplete="new-password")
    with col_age:
        actual_age = st.number_input("현재 나이", min_value=0, max_value=120, step=1)
    
    st.divider()
    eval_type = st.radio("평가 구분", ["초기 평가", "추적 관찰"], horizontal=True)

    st.divider()
    ages = ["만 5세 미만", "만 5세 - 만 7세", "만 8세 - 만 12세", "만 13세 - 만 18세", "만 19세 이상"]
    col1, col2 = st.columns(2)
    for i, age in enumerate(ages):
        with [col1, col2][i % 2]:
            if st.button(age, use_container_width=True):
                if patient_name.strip():
                    st.session_state.user_info = {
                        'patient_name': patient_name,
                        'actual_age': actual_age,
                        'age_group': age,
                        'eval_type': eval_type
                    }
                    st.session_state.step = 'target_selection'
                    st.rerun()
                else: st.error("성함을 입력해 주세요.")

# STEP 2: 대상자 선택
elif st.session_state.step == 'target_selection':
    st.header("2. 작성 대상을 선택해주세요")
    age_group = st.session_state.user_info['age_group']
    eval_type = st.session_state.user_info.get('eval_type', '초기 평가')
    st.info(f"대상 환자: {st.session_state.user_info['patient_name']} ({age_group}) / {eval_type}")
    
    col1, col2 = st.columns(2)
    with col1:
        is_infant = age_group == "만 5세 미만"
        is_p_done = "본인" in st.session_state.completed_targets
        btn_label = "❌ 본인 설문 없음" if is_infant else ("✅ 본인 (완료)" if is_p_done else "본인 (환자)")
        if st.button(btn_label, use_container_width=True, disabled=(is_p_done or is_infant)):
            st.session_state.current_target = "본인"
            st.session_state.step = 'survey_form'
            st.rerun()

    with col2:
        if age_group == "만 19세 이상":
            st.write("💡 성인 환자는 본인 설문만 진행합니다.")
        else:
            is_g_done = "보호자" in st.session_state.completed_targets
            btn_label = "✅ 보호자 (완료)" if is_g_done else "보호자 (주양육자)"
            if st.button(btn_label, use_container_width=True, disabled=is_g_done):
                st.session_state.current_target = "보호자"
                st.session_state.sub_step = 0
                st.session_state.step = 'survey_form'
                st.rerun()

    st.divider()
    if st.button("⬅️ 처음으로 (이름/연령 다시 선택)", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    is_finished = ("본인" in st.session_state.completed_targets) if age_group == "만 19세 이상" else \
                  (("보호자" in st.session_state.completed_targets) if age_group == "만 5세 미만" else (len(st.session_state.completed_targets) >= 2))
    
    if is_finished:
        if st.button("🚀 최종 데이터 제출 및 저장", use_container_width=True, type="primary"):
            surveys.save_survey({**st.session_state.user_info, **st.session_state.all_responses})
            st.session_state.step = 'final_thanks'
            st.rerun()

# STEP 3: 설문 진행 로직
elif st.session_state.step == 'survey_form':
    target = st.session_state.current_target
    age_group = st.session_state.user_info.get('age_group', '')
    actual_age = st.session_state.user_info.get('actual_age', 0)
    eval_type = st.session_state.user_info.get('eval_type', '초기 평가')
    sub_step = st.session_state.sub_step
    
    # -------------------------------------------------------------
    # [추적 관찰] 생략되는 문항:
    # 1. 환자 본인 (RS 제외):
    #    -> 8세 이상이면 기존은 5단계지만, RS(4단계)가 빠져야 함
    # 2. 보호자 (PSOC, FACE-IV 제외):
    #    -> 5세 미만: 기존 6단계에서 5(PSOC), 6(FACE-IV) 제외
    #    -> 5세 이상: 기존 6/5단계에서 마지막 두 단계 제외
    # -------------------------------------------------------------
    
    # 총 단계 수 계산 로직
    if target == "본인":
        # 5-7세: 무조건 1단계
        if age_group == "만 5세 - 만 7세":
            total_steps = 1
        else:
            # 기본 5단계(1:PedsQL, 2:CESD, 3:GAD/SCARED, 4:RS, 5:신체활동)
            # 추적관찰인 경우 RS(4단계)를 스킵해야 하므로, 보여지는 전체 단계 수를 1 줄임(또는 유지하되 4단계를 건너뛰게 함)
            # 여기서는 스킵 처리를 편하게 하기 위해 total_steps는 그대로 유지하되 렌더링을 스킵하는 로직 사용을 권장.
            # 하지만 UI 진행도를 위해 실제 거치는 스텝수를 반영하는 방식을 채택합니다.
            total_steps = 5 if eval_type == "초기 평가" else 4
    else: # 보호자
        if age_group == "만 5세 미만": 
            total_steps = 6 if eval_type == "초기 평가" else 4 # 5(PSOC), 6(FACE-IV) 제거
        elif age_group in ["만 8세 - 만 12세", "만 13세 - 만 18세"]: 
            total_steps = 6 if eval_type == "초기 평가" else 4 # 4(PSOC), 5(FACE-IV) 제거됨 (idx기준 4, 5)
        else: 
            total_steps = 5 if eval_type == "초기 평가" else 3 # 4(PSOC), 5(FACE-IV) 제거됨 (idx기준 4, 5)

    # UI 진행 상태에 맞는 표시 (내부 sub_step과 별개로 사용자에게는 1부터 순서대로 보여지도록 함)
    # 복잡성을 피하기 위해 여기서는 sub_step 스킵 로직을 사용합니다.
    st.header(f"📋 {target} 설문 진행 ({sub_step if sub_step > 0 else '사전 정보'})")
    
    # st.form 대신 단순히 그룹화 
    # (라디오 버튼 누를 때마다 총점 갱신을 위해 즉시 재계산 허용)
    current_responses = {}
    
    # --- [CASE 1] 환자 본인 ---
    if target == "본인":
        if sub_step == 1:
            if age_group == "만 5세 - 만 7세":
                surveys.show_instructions_5_7(); current_responses = surveys.peds_ql_5_7()
            elif age_group == "만 8세 - 만 12세":
                surveys.show_instructions_8_12(); current_responses = surveys.peds_ql_8_12()
            elif age_group == "만 13세 - 만 18세":
                surveys.show_instructions_13_18(); current_responses = surveys.peds_ql_13_18()
            elif age_group == "만 19세 이상":
                if actual_age >= 26: surveys.show_instructions_adult(); current_responses = surveys.peds_ql_adult()
                else: surveys.show_instructions_18_25(); current_responses = surveys.peds_ql_18_25()
        elif sub_step == 2:
            if actual_age >= 18: surveys.show_instructions_ces_d(); current_responses = surveys.ces_d_survey_20()
            else: surveys.show_instructions_ces_dc(); current_responses = surveys.ces_dc_survey_20()
        elif sub_step == 3:
            if actual_age >= 18: surveys.show_instructions_gad_7(); current_responses = surveys.gad_7_survey_7()
            else: surveys.show_instructions_scared(); current_responses = surveys.scared_survey_41()
        elif sub_step == 4:
            if eval_type == "초기 평가":
                if actual_age >= 19: surveys.show_instructions_rs_19(); current_responses = surveys.rs_survey_19()
                else: surveys.show_instructions_rs_y(); current_responses = surveys.rs_y_survey_17()
            else:
                # 추적 관찰 시 4번째 단계는 '신체 활동 평가'로 대체됨
                surveys.show_instructions_physical_activity()
                current_responses = surveys.physical_activity_survey()
        elif sub_step == 5 and eval_type == "초기 평가":
            # 초기 평가의 5번째 단계
            surveys.show_instructions_physical_activity()
            current_responses = surveys.physical_activity_survey()

    # --- [CASE 2] 보호자 ---
    elif target == "보호자":
        # [Add Parent Demographic Step]
        if sub_step == 0:
            st.subheader("👨‍👩‍👧 보호자 기본 정보")
            st.info("💡 **보호자 설문을 시작하기 전에 아래 인적 정보를 입력해 주세요.**")
            surveys.apply_custom_font()
            
            # 보호자 인적사항 입력위젯들을 모아둠
            rel_options = ["부", "모", "기타"]
            res_rel = st.radio("대상자와의 관계", rel_options, horizontal=True)
            res_birth = st.date_input("보호자 생년월일", min_value=datetime(1920, 1, 1), max_value=datetime.today())
            
            edu_options = ["중학교 졸업", "고등학교 졸업", "대학교 졸업", "대학원 졸업 이상"]
            res_edu = st.radio("보호자 교육수준", edu_options, horizontal=True)
            
            job_options = ["관리직", "전문직", "사무직", "서비스직", "판매직", "군인", "농어업종사자", "단순 노무 종사자", "기능직", "기술직", "기타"]
            res_job = st.selectbox("보호자 직업", job_options)
            
            family_options = ["부", "모", "남자형제", "여자형제", "배우자", "자녀"]
            res_family = st.multiselect("대상자의 가족 구성 (환자 기준, 중복 선택 가능)", family_options)
            
            current_responses["보호자_관계"] = res_rel
            current_responses["보호자_생년월일"] = res_birth.strftime("%Y-%m-%d")
            current_responses["보호자_교육수준"] = res_edu
            current_responses["보호자_직업"] = res_job
            current_responses["대상자_가족구성"] = ", ".join(res_family) if res_family else "없음"

        elif age_group == "만 5세 미만":
            if sub_step == 1:
                st.subheader("👶 아기의 세부 연령 선택")
                infant_age = st.radio("해당되는 월령을 선택하세요", ["1-12개월", "13-24개월", "2세-4세"], horizontal=True)
                st.session_state.temp_infant_age = infant_age
            elif sub_step == 2:
                selected = st.session_state.get('temp_infant_age', '2세-4세')
                if selected == "1-12개월": surveys.show_instructions_infant_1_12m(); current_responses = surveys.peds_ql_infant_1_12m()
                elif selected == "13-24개월": surveys.show_instructions_infant_13_24m(); current_responses = surveys.peds_ql_infant_13_24m()
                else: surveys.show_instructions_toddler_2_4y(); current_responses = surveys.peds_ql_toddler_2_4y()
            elif sub_step == 3: surveys.show_instructions_ces_d(); current_responses = surveys.ces_d_survey_20()
            elif sub_step == 4: surveys.show_instructions_gad_7(); current_responses = surveys.gad_7_survey_7()
            # 추적 관찰 시 5(PSOC), 6(FACE-IV) 단계는 생략됨 (total_steps 에 의해 도달하지 않음)
            elif sub_step == 5 and eval_type == "초기 평가": surveys.show_instructions_psoc(); current_responses = surveys.psoc_survey_16()
            elif sub_step == 6 and eval_type == "초기 평가": surveys.show_instructions_face_iv(); current_responses = surveys.face_iv_survey_20()
        
        else: # 5세 이상 보호자
            if sub_step == 1:
                if age_group == "만 5세 - 만 7세": surveys.show_instructions_parent(); current_responses = surveys.peds_ql_parent_5_7()
                elif age_group == "만 8세 - 만 12세": surveys.show_instructions_parent_8_12(); current_responses = surveys.peds_ql_parent_8_12()
                elif age_group == "만 13세 - 만 18세": surveys.show_instructions_parent_13_18(); current_responses = surveys.peds_ql_parent_13_18()
            
            # 8-18세 보호자에게만 PSC 추가
            elif sub_step == 2 and age_group in ["만 8세 - 만 12세", "만 13세 - 만 18세"]:
                surveys.show_instructions_psc(); current_responses = surveys.psc_symptom_survey_35()
            
            # 공통 보호자 설문 (단계 밀림 대응)
            idx = sub_step if age_group not in ["만 8세 - 만 12세", "만 13세 - 만 18세"] else sub_step - 1
            if idx == 2: surveys.show_instructions_ces_d(); current_responses = surveys.ces_d_survey_20()
            elif idx == 3: surveys.show_instructions_gad_7(); current_responses = surveys.gad_7_survey_7()
            # 추적 관찰 시 4(PSOC), 5(FACE-IV) 단계는 생략됨 (total_steps 에 의해 도달하지 않음)
            elif idx == 4 and eval_type == "초기 평가": surveys.show_instructions_psoc(); current_responses = surveys.psoc_survey_16()
            elif idx == 5 and eval_type == "초기 평가": surveys.show_instructions_face_iv(); current_responses = surveys.face_iv_survey_20()

    # 총점 계산 및 표시
    # 값 중에 숫자가 아닌 것들(예: 주양육자 관계 등 문자열)은 제외하고 합산
    total_score = sum(v for v in current_responses.values() if isinstance(v, (int, float)))
    
    # 인적사항(sub_step == 0)이나 기타 점수 합산이 무의미한 단계에서는 점수 표시 생략
    show_score = True
    if target == "보호자" and sub_step == 0:
        show_score = False
    if target == "보호자" and age_group == "만 5세 미만" and sub_step == 1:
        show_score = False
        
    if show_score and len(current_responses) > 0:
        st.divider()
        st.markdown(f"**현재 페이지 총점:** `{total_score}점`")

    # 버튼 영역
    col_prev, col_next = st.columns(2)
    with col_prev:
        if st.button("⬅️ 이전 단계로"):
            # 보호자의 경우 sub_step 0이 처음임
            min_step = 0 if target == "보호자" else 1
            if sub_step > min_step:
                st.session_state.sub_step -= 1
                st.rerun()
            else:
                st.session_state.step = 'target_selection'
                st.rerun()
    
    with col_next:
        is_last = (sub_step == total_steps)
        if st.button("최종 제출" if is_last else "다음 단계로 ➡️", type="primary"):
            if target == "보호자" and age_group == "만 5세 미만" and sub_step == 1:
                st.session_state.user_info['infant_sub_group'] = st.session_state.temp_infant_age
            else:
                prefix = f"[{age_group}_{target}] Step{sub_step}_" if sub_step > 0 else f"[{target}_인적사항] "
                st.session_state.all_responses.update({f"{prefix}{k}": v for k, v in current_responses.items()})
            
            if not is_last:
                st.session_state.sub_step += 1
                st.rerun()
            else:
                st.session_state.completed_targets.append(target)
                st.session_state.sub_step = 1
                st.session_state.step = 'inter_thanks'
                st.rerun()

# STEP 4: 중간 감사 페이지
elif st.session_state.step == 'inter_thanks':
    st.success("해당 대상의 설문이 임시 저장되었습니다.")
    if st.button("작성 대상 선택 화면으로 돌아가기", use_container_width=True):
        st.session_state.step = 'target_selection'
        st.rerun()

# STEP 5: 최종 완료 페이지
elif st.session_state.step == 'final_thanks':
    st.balloons()
    st.header("🎉 모든 과정이 완료되었습니다.")
    
    st.divider()
    st.subheader("🔒 관리자 데이터 다운로드")
    
    admin_pw = st.text_input("데이터 추출 비밀번호를 입력하세요:", type="password")
    
    if admin_pw == "admin1234":
        if os.path.exists("survey_results.csv"):
            df = pd.read_csv("survey_results.csv", encoding='utf-8-sig')
            
            st.success("인증되었습니다. 데이터를 다운로드할 수 있습니다.")
            st.divider()
            
            import io
            
            def create_excel_download(dataframe):
                """주어진 데이터프레임을 설문 종류별 시트로 분리하고 총점 컬럼을 추가한 엑셀 바이트 데이터를 생성합니다."""
                output = io.BytesIO()
                
                # 기본 정보 컬럼들
                base_info_cols = ['patient_name', 'actual_age', 'age_group', 'eval_type', 'infant_sub_group', '제출시간']
                base_info_cols = [c for c in base_info_cols if c in dataframe.columns]
                
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # 전체 통합 데이터 시트
                    dataframe.to_excel(writer, index=False, sheet_name='전체 원본 데이터')
                    
                    # 각 설문 종류판별 로직:
                    # 컬럼 이름의 패턴 (예: "[만 8세 - 만 12세_보호자] Step2_CESD_1" -> 접두어 식별)
                    survey_cols = [c for c in dataframe.columns if c not in base_info_cols]
                    
                    # 분류를 위한 Prefix 그룹화 (예: '보호자_인적사항', 'PedsQL_본인' 등 의미단위로 묶기)
                    grouped_data = {}
                    
                    for col in survey_cols:
                        col_str = str(col)  # Ensure it is a string for string operations
                        # 대괄호로 대상 및 연령 구분 파악
                        if col_str.startswith('['):
                            # [그룹설명] 이후의 부분을 가져옴
                            parts = col_str.split('] ')
                            if len(parts) >= 2:
                                group_tag = parts[0][1:] # "만 8세 - 만 12세_보호자" 등
                                remain = parts[1] # "StepX_설문이름_번호" 등
                                survey_name = "기타_설문"
                                
                                # 인적사항인지 설문인지 파악
                                if "인적사항" in group_tag:
                                    survey_name = "인적사항"
                                elif remain.startswith("Step"):
                                    if "CESDC" in remain: survey_name = "CES-DC"
                                    elif "CESD" in remain: survey_name = "CES-D"
                                    elif "GAD7" in remain: survey_name = "GAD-7"
                                    elif "SCARED" in remain: survey_name = "SCARED"
                                    elif "RSY" in remain: survey_name = "RSY"
                                    elif "RS_" in remain: survey_name = "RS"
                                    elif "PSOC" in remain: survey_name = "PSOC"
                                    elif "FACE" in remain: survey_name = "FACE-IV"
                                    elif "PSC" in remain: survey_name = "PSC"
                                    elif "신체활동" in remain: survey_name = "주관적_신체활동"
                                    else: survey_name = "PedsQL" # StepX로 시작하지만 위의 키워드가 없으면 모두 PedsQL
                                    
                                # 시트명 생성 (예: 보호자_CES-D)
                                target = "본인" if "본인" in group_tag else "보호자"
                                sheet_name = str(f"{target}_{survey_name}")
                                # 엑셀 시트명 길이 제한(31자) 대비
                                sheet_name = sheet_name[:31]
                                
                                if sheet_name not in grouped_data:
                                    grouped_data[sheet_name] = []
                                grouped_data[sheet_name].append(col)
                        else:
                            # 괄호로 시작하지 않는 레거시 컬럼 등
                            if '기타' not in grouped_data: grouped_data['기타'] = []
                            grouped_data['기타'].append(col)
                            
                    # 각 시트별 데이터프레임 생성 및 총점 계산
                    for sheet_name, cols in grouped_data.items():
                        sheet_df = dataframe[base_info_cols + cols].copy()
                        # 데이터가 모두 비어있는 컬럼은 제외 (해당 연령대가 아닌 경우 방지)
                        sheet_df.dropna(axis=1, how='all', inplace=True)
                        
                        # 이 시트에 남은 질문 컬럼들
                        active_q_cols = [c for c in cols if c in sheet_df.columns]
                        
                        if active_q_cols:
                            # 보호자 인적사항 등 숫자가 아닌 값이 있는 시트는 총점 계산 제외
                            if "인적사항" not in sheet_name and "기타" not in sheet_name:
                                # 숫자형식 컬럼만 골라서 합산 (문자열 등은 0으로 처리, NaN도 0)
                                numeric_df = sheet_df[active_q_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
                                sheet_df['총점'] = numeric_df.sum(axis=1)
                        
                        # 시트에 데이터가 1줄이라도 존재하는 경우만 (NaN이 아닌 데이터 기준)
                        if len(sheet_df) > 0 and len(active_q_cols) > 0:
                            sheet_df.to_excel(writer, index=False, sheet_name=sheet_name)
                            
                return output.getvalue()

            st.subheader("📊 설문 데이터 다운로드")
            
            # 전체 다운로드 (Excel)
            excel_all = create_excel_download(df)
            st.download_button(
                label="📥 전체 성적 데이터 다운로드 (통합 Excel)", 
                data=excel_all, 
                file_name="Survey_Results_All_Grouped.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
            
            st.divider()
            st.write("💡 특정 연령대 그룹의 결과만 따로 다운로드하실 수 있습니다.")
            
            age_groups = ["만 5세 미만", "만 5세 - 만 7세", "만 8세 - 만 12세", "만 13세 - 만 18세", "만 19세 이상"]
            tabs = st.tabs(age_groups)
            
            for i, age_group in enumerate(age_groups):
                with tabs[i]:
                    if 'age_group' in df.columns:
                        filtered_df = df[df['age_group'] == age_group]
                        if not filtered_df.empty:
                            # Remove completely empty columns for this target group
                            filtered_df_clean = filtered_df.dropna(axis=1, how='all')
                            
                            excel_filtered = create_excel_download(filtered_df_clean)
                            st.download_button(
                                label=f"📥 [{age_group}] 엑셀 그룹 다운로드",
                                data=excel_filtered,
                                file_name=f"Survey_Results_{age_group.replace(' ', '')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            st.dataframe(filtered_df_clean.head(3))
                        else:
                            st.info(f"아직 '{age_group}' 그룹에 제출된 설문 결과가 없습니다.")
                    else:
                        st.warning("데이터 형식을 확인할 수 없습니다.")
    elif admin_pw:
        st.error("비밀번호가 일치하지 않습니다.")

    st.divider()
    if st.button("🔄 처음으로 돌아가기"):
        st.session_state.clear()
        st.rerun()