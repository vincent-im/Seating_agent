import streamlit as st
import pandas as pd
import random
import os

# 페이지 기본 설정 (모바일 축소형 뷰 최적화)
st.set_page_config(
    page_title="팀 좌석 배치 에이전트 (모바일 축소 뷰)", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 인라인 CSS: 스마트폰 한 화면에 전체 요소를 압축해서 보여주는 스타일링
st.markdown("""
    <style>
    /* 기본 여백 최소화하여 한 화면에 우겨넣기 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
    }
    
    /* 타이틀 및 서브텍스트 크기 축소 */
    h1 { font-size: 1.5rem !important; margin-bottom: 0.2rem !important; text-align: center; }
    .sub-title-text { font-size: 0.8rem; color: #7F8C8D; text-align: center; margin-bottom: 0.8rem; }
    h3 { font-size: 1.1rem !important; margin-top: 0.5rem !important; margin-bottom: 0.3rem !important; }

    /* 명단 버튼(3x6) 초소형 스타일링 */
    div.stButton > button {
        font-size: 0.75rem !important;
        padding: 4px 2px !important;
        min-height: 32px !important;
        margin-bottom: 2px !important;
        border-radius: 4px !important;
    }
    
    /* 초기화 버튼 컴팩트 스타일링 */
    .reset-container button {
        font-size: 0.8rem !important;
        padding: 5px !important;
        background-color: #F0F2F6 !important;
    }

    /* 좌석 미니어처 상자 공통 스타일 */
    .mini-seat-box {
        text-align: center;
        padding: 4px 1px;
        border-radius: 4px;
        min-height: 48px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        line-height: 1.1;
    }
    .seat-id { font-size: 8px; color: #95A5A6; font-weight: bold; }
    .seat-name { font-size: 10.5px; font-weight: bold; margin-top: 1px; }
    .seat-empty { font-size: 9px; color: #BDC3C7; margin-top: 2px; }
    </style>
""", unsafe_allow_html=True)

# 데이터 로드 함수
def load_member_list():
    file_name = "명단.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name)
            names = df.iloc[:, 0].dropna().astype(str).tolist()
            return [name.strip() for name in names if name.strip()]
        except Exception as e:
            return [f"팀원{i}" for i in range(1, 19)]
    else:
        return [f"홍길동{i}" for i in range(1, 19)]

# 세션 상태 초기화
if 'original_members' not in st.session_state:
    st.session_state.original_members = load_member_list()
if 'current_members' not in st.session_state:
    st.session_state.current_members = st.session_state.original_members.copy()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}

# 오피스 고정 레이아웃 (G 자리는 기둥, 마지막 칸은 W)
seat_structure = [
    ["A", "B", "C", "", "D", "E", "F"],
    ["", "", "", "", "", "", ""],
    ["기둥", "G", "H", "", "I", "J", "K"], 
    ["L", "M", "N", "", "O", "P", "Q"],   
    ["", "", "", "", "", "", ""],
    ["R", "S", "T", "", "U", "V", "W"]
]

all_valid_seats = [cell for row in seat_structure for cell in row if cell and cell != "기둥"]
assigned_seats = list(st.session_state.assignments.keys())
available_seats = [s for s in all_valid_seats if s not in assigned_seats]

def reset_all():
    st.session_state.current_members = st.session_state.original_members.copy()
    st.session_state.assignments = {}

# --- 상단 타이틀 영역 ---
st.markdown("<h1>🖥️ 팀 좌석 배치 에이전트</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title-text'>모바일 한눈에 보기 뷰 (3x6 명단 & 축소 도면)</div>", unsafe_allow_html=True)

# --- 1층 영역: 3열 6행(3x6) 압축 팀 명단 패널 ---
st.markdown("<h3>👥 팀 명단 (이름 터치 시 배정)</h3>", unsafe_allow_html=True)

if st.session_state.current_members:
    # 정확히 3열 격자로 설정하여 가로폭 최적화
    btn_cols = st.columns(3)
    for idx, name in enumerate(st.session_state.current_members):
        col_target = btn_cols[idx % 3]
        if col_target.button(name, key=f"btn_{name}", use_container_width=True):
            if available_seats:
                chosen_seat = random.choice(available_seats)
                st.session_state.assignments[chosen_seat] = name
                st.session_state.current_members.remove(name)
                st.rerun()
            else:
                st.error("모든 좌석이 만석입니다!")
else:
    st.success("🎉 모든 팀원의 좌석 배치가 완료되었습니다!")

st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

# --- 2층 영역: 전체 좌석 배치 그림 한눈에 보기 패널 ---
title_space, reset_space = st.columns([3, 1])
title_space.markdown("<h3>🪑 좌석 배치 현황</h3>", unsafe_allow_html=True)

with reset_space:
    st.markdown("<div class='reset-container'>", unsafe_allow_html=True)
    if st.button("🔄 리셋", key="reset_top", use_container_width=True):
        reset_all()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 7열 미니어처 오피스 그리드 배치 (좌측 고정 창가 0.4폭, 나머지 좌석 각 1폭)
grid_cols = st.columns([0.4] + [1]*7)
window_chars = ["W", "I", "N", "D", "O", "W"]

for r_idx, row in enumerate(seat_structure):
    # 0번 열: 축소형 창가 가이드라인
    if r_idx in [0, 2, 3, 5]:
        w_idx = [0, 2, 3, 5].index(r_idx)
        grid_cols[0].markdown(
            f"<div style='background-color:#E0F7FA; color:#006064; text-align:center; "
            f'padding:14px 0; font-weight:bold; border:1px solid #006064; border-radius:3px; font-size:9px;\'>{window_chars[w_idx]}</div>', 
            unsafe_allow_html=True
        )
    else:
        grid_cols[0].write("")

    # 1~7번 열: 콤팩트 좌석 드로잉
    for c_idx, val in enumerate(row):
        target_col = grid_cols[c_idx + 1]
        
        if val == "기둥":
            target_col.markdown(
                "<div class='mini-seat-box' style='background-color:#2C3E50; color:#FFFFFF; "
                "border:1px solid #1A252F; font-size:9px; font-weight:bold;'>기둥</div>", 
                unsafe_allow_html=True
            )
        elif val != "":
            # 배정 완료된 상태의 상자 축소 디자인
            if val in st.session_state.assignments:
                assigned_name = st.session_state.assignments[val]
                bg_color = "#FFF3E0" if "팀장" in assigned_name else "#E8F5E9"
                font_color = "#D84315" if "팀장" in assigned_name else "#2E7D32"
                border_color = "#E65100" if "팀장" in assigned_name else "#1B5E20"
                
                target_col.markdown(
                    f"<div class='mini-seat-box' style='background-color:{bg_color}; color:{font_color}; "
                    f"border:1.5px solid {border_color};'>"
                    f"<span class='seat-id'>{val}</span>"
                    f"<span class='seat-name'>{assigned_name}</span></div>", 
                    unsafe_allow_html=True
                )
            # 미배정 빈 자리 축소 디자인
            else:
                target_col.markdown(
                    f"<div class='mini-seat-box' style='background-color:#FFFFFF; color:#7F8C8D; "
                    f"border:1px solid #BDC3C7;'>"
                    f"<span class='seat-id'>{val}</span>"
                    f"<span class='seat-empty'>빈자리</span></div>", 
                    unsafe_allow_html=True
                )
        else:
            # 복도 라인 간격 축소 최소화
            if r_idx in [1, 4]:
                target_col.markdown("<div style='text-align:center; color:#E0E0E0; font-size:8px; padding:12px 0;'>-</div>", unsafe_allow_html=True)
            else:
                target_col.write("")