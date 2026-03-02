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

# --- 2. 메인 로직 흐름 ---

# STEP 1: 기본 정보 및 연령 선택
if st.session_state.step == 'name_input':
    st.header("1. 환자의 기본 정보 및 연령대 선택")
    col_name, col_age = st.columns([3, 1])
    with col_name:
        patient_name = st.text_input("환자 성함", placeholder="성함 입력")
    with col_age:
        actual_age = st.number_input("현재 나이", min_value=0, max_value=120, step=1)
    
    st.divider()
    ages = ["만 5세 미만", "만 5세 - 만 7세", "만 8세 - 만 12세", "만 13세 - 만 17세", "만 18세 이상"]
    col1, col2 = st.columns(2)
    for i, age in enumerate(ages):
        with [col1, col2][i % 2]:
            if st.button(age, use_container_width=True):
                if patient_name.strip():
                    st.session_state.user_info = {'patient_name': patient_name, 'actual_age': actual_age, 'age_group': age}
                    st.session_state.step = 'target_selection'
                    st.rerun()
                else: st.error("성함을 입력해 주세요.")

# STEP 2: 대상자 선택
elif st.session_state.step == 'target_selection':
    st.header("2. 작성 대상을 선택해주세요")
    age_group = st.session_state.user_info['age_group']
    st.info(f"대상 환자: {st.session_state.user_info['patient_name']} ({age_group})")
    
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
        if age_group == "만 18세 이상":
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

    is_finished = ("본인" in st.session_state.completed_targets) if age_group == "만 18세 이상" else \
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
    sub_step = st.session_state.sub_step
    
    # 총 단계 수 계산
    if target == "본인":
        total_steps = 1 if age_group == "만 5세 - 만 7세" else 4
    else: # 보호자
        if age_group == "만 5세 미만": total_steps = 6 # 인적사항(0) + 월령선택 + PedsQL + 4종
        elif age_group in ["만 8세 - 만 12세", "만 13세 - 만 17세"]: total_steps = 6 # 인적사항(0) + PedsQL + PSC + 4종
        else: total_steps = 5 # 인적사항(0) 포함

    st.header(f"📋 {target} 설문 진행 ({sub_step if sub_step > 0 else '사전 정보'} / {total_steps})")
    
    with st.form("current_survey_form"):
        current_responses = {}
        
        # --- [CASE 1] 환자 본인 ---
        if target == "본인":
            if sub_step == 1:
                if age_group == "만 5세 - 만 7세":
                    surveys.show_instructions_5_7()
                    current_responses = surveys.peds_ql_5_7()
                elif age_group == "만 8세 - 만 12세":
                    surveys.show_instructions_8_12()
                    current_responses = surveys.peds_ql_8_12()
                elif age_group == "만 13세 - 만 17세":
                    surveys.show_instructions_13_18()
                    current_responses = surveys.peds_ql_13_18()
                elif age_group == "만 18세 이상":
                    if actual_age >= 26:
                        surveys.show_instructions_adult()
                        current_responses = surveys.peds_ql_adult()
                    else:
                        surveys.show_instructions_18_25()
                        current_responses = surveys.peds_ql_18_25()
            elif sub_step == 2:
                if actual_age >= 18:
                    surveys.show_instructions_ces_d(); current_responses = surveys.ces_d_survey_20()
                else:
                    surveys.show_instructions_ces_dc(); current_responses = surveys.ces_dc_survey_20()
            elif sub_step == 3:
                if actual_age >= 18:
                    surveys.show_instructions_gad_7(); current_responses = surveys.gad_7_survey_7()
                else:
                    surveys.show_instructions_scared(); current_responses = surveys.scared_survey_41()
            elif sub_step == 4:
                if actual_age >= 19:
                    surveys.show_instructions_rs_19(); current_responses = surveys.rs_survey_19()
                else:
                    surveys.show_instructions_rs_y(); current_responses = surveys.rs_y_survey_17()

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
                elif sub_step == 5: surveys.show_instructions_psoc(); current_responses = surveys.psoc_survey_16()
                elif sub_step == 6: surveys.show_instructions_face_iv(); current_responses = surveys.face_iv_survey_20()
            
            else: # 5세 이상 보호자
                if sub_step == 1:
                    if age_group == "만 5세 - 만 7세": surveys.show_instructions_parent(); current_responses = surveys.peds_ql_parent_5_7()
                    elif age_group == "만 8세 - 만 12세": surveys.show_instructions_parent_8_12(); current_responses = surveys.peds_ql_parent_8_12()
                    elif age_group == "만 13세 - 만 17세": surveys.show_instructions_parent_13_18(); current_responses = surveys.peds_ql_parent_13_18()
                
                # 8-17세 보호자에게만 PSC 추가
                elif sub_step == 2 and age_group in ["만 8세 - 만 12세", "만 13세 - 만 17세"]:
                    surveys.show_instructions_psc(); current_responses = surveys.psc_symptom_survey_35()
                
                # 공통 보호자 설문 (단계 밀림 대응)
                idx = sub_step if age_group not in ["만 8세 - 만 12세", "만 13세 - 만 17세"] else sub_step - 1
                if idx == 2: surveys.show_instructions_ces_d(); current_responses = surveys.ces_d_survey_20()
                elif idx == 3: surveys.show_instructions_gad_7(); current_responses = surveys.gad_7_survey_7()
                elif idx == 4: surveys.show_instructions_psoc(); current_responses = surveys.psoc_survey_16()
                elif idx == 5: surveys.show_instructions_face_iv(); current_responses = surveys.face_iv_survey_20()

        # 버튼 영역
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.form_submit_button("⬅️ 이전 단계로"):
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
            if st.form_submit_button("최종 제출" if is_last else "다음 단계로 ➡️"):
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
            
            st.subheader("📊 설문 데이터 다운로드")
            # 전체 다운로드
            csv_all = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 전체 성적 데이터 다운로드 (통합)", 
                data=csv_all, 
                file_name="Survey_Results_All.csv", 
                mime="text/csv",
                type="primary"
            )
            
            st.divider()
            st.write("💡 특정 연령대 그룹의 결과만 따로 다운로드하실 수 있습니다.")
            
            age_groups = ["만 5세 미만", "만 5세 - 만 7세", "만 8세 - 만 12세", "만 13세 - 만 17세", "만 18세 이상"]
            tabs = st.tabs(age_groups)
            
            for i, age_group in enumerate(age_groups):
                with tabs[i]:
                    if 'age_group' in df.columns:
                        filtered_df = df[df['age_group'] == age_group]
                        if not filtered_df.empty:
                            # Remove columns that are completely empty for this target group
                            filtered_df_clean = filtered_df.dropna(axis=1, how='all')
                            
                            csv_filtered = filtered_df_clean.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label=f"📥 [{age_group}] 대상자 그룹 다운로드",
                                data=csv_filtered,
                                file_name=f"Survey_Results_{age_group.replace(' ', '')}.csv",
                                mime="text/csv"
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