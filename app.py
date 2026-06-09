import streamlit as st
import pandas as pd
import random
import os
import base64

# 1. 반응형 및 레이아웃 기본 설정
st.set_page_config(
    page_title="오피스 좌석 배치 프로그램",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. PC 및 모바일 화면 최적화를 위한 인라인 CSS 스타일 설정
st.markdown("""
    <style>
    /* 전체 여백 최적화 */
    .block-container {
        padding: 1.5rem 1rem !important;
    }
    h2 { font-size: 1.4rem !important; font-weight: bold; margin-bottom: 1rem !important; }
    
    /* 명단 박스 기본 스타일 (네모 박스 형태) */
    div.stButton > button {
        width: 100% !important;
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #dcdcdc !important;
        font-weight: 500 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #4A90E2 !important;
        background-color: #f0f7ff !important;
    }

    /* PC 및 모바일 화면 전환 제어 */
    @media (min-width: 800px) {
        .pc-layout { display: block; }
        .mobile-layout { display: none; }
        div.stButton > button {
            font-size: 0.95rem !important;
            padding: 10px 5px !important;
            min-height: 45px !important;
            border-radius: 6px !important;
        }
    }
    @media (max-width: 799px) {
        .pc-layout { display: none; }
        .mobile-layout { display: block; }
        /* 모바일에서는 상단 공간 절약을 위해 박스 크기 및 폰트 축소 */
        div.stButton > button {
            font-size: 0.75rem !important;
            padding: 4px 2px !important;
            min-height: 32px !important;
            border-radius: 4px !important;
        }
    }

    /* 이미지 및 오버레이 이름표 스타일 */
    .image-container {
        position: relative;
        width: 100%;
        display: inline-block;
    }
    .bg-image {
        width: 100%;
        height: auto;
        display: block;
        border-radius: 6px;
    }
    .floating-name {
        position: absolute;
        transform: translate(-50%, -50%);
        padding: 4px 8px;
        font-weight: bold;
        border-radius: 4px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        white-space: nowrap;
        pointer-events: none;
        z-index: 10;
    }
    @media (max-width: 799px) {
        .floating-name {
            font-size: 9px !important;
            padding: 2px 4px !important;
        }
    }
    .name-leader { background-color: #FFEB3B; color: #E65100; border: 1.5px solid #E65100; }
    .name-member { background-color: #2ECC71; color: #FFFFFF; border: 1px solid #27AE60; }
    </style>
""", unsafe_allow_html=True)

# 3. 실제 '좌석배치.png' 이미지 내 각 알파벳 책상의 정밀 정중앙 좌표 설정 (%)
SEAT_COORDINATES = {
    'A': {'top': '14.5%', 'left': '18.2%'}, 'B': {'top': '14.5%', 'left': '31.4%'}, 'C': {'top': '14.5%', 'left': '44.8%'},
    'D': {'top': '14.5%', 'left': '65.2%'}, 'E': {'top': '14.5%', 'left': '78.5%'}, 'F': {'top': '14.5%', 'left': '91.6%'},
    
    'G': {'top': '44.2%', 'left': '31.4%'}, 'H': {'top': '44.2%', 'left': '44.8%'},
    'I': {'top': '44.2%', 'left': '65.2%'}, 'J': {'top': '44.2%', 'left': '78.5%'}, 'K': {'top': '44.2%', 'left': '91.6%'},
    
    'L': {'top': '59.0%', 'left': '18.2%'}, 'M': {'top': '59.0%', 'left': '31.4%'}, 'N': {'top': '59.0%', 'left': '44.8%'},
    'O': {'top': '59.0%', 'left': '65.2%'}, 'P': {'top': '59.0%', 'left': '78.5%'}, 'Q': {'top': '59.0%', 'left': '91.6%'},
    
    'R': {'top': '88.5%', 'left': '18.2%'}, 'S': {'top': '88.5%', 'left': '31.4%'}, 'T': {'top': '88.5%', 'left': '44.8%'},
    'U': {'top': '88.5%', 'left': '65.2%'}, 'V': {'top': '88.5%', 'left': '78.5%'}, 'W': {'top': '88.5%', 'left': '91.6%'}
}

# 4. 데이터 로드 함수 (명단.xlsx 지원)
def load_initial_members():
    file_name = "명단.xlsx"
    if os.path.exists(file_name):
        try:
            # 엑셀 파일 읽기 (첫 번째 열을 명단으로 인식)
            df = pd.read_excel(file_name)
            names = df.iloc[:, 0].dropna().astype(str).tolist()
            return [name.strip() for name in names if name.strip()]
        except:
            pass
    # 파일이 없거나 오류 발생 시 기본 샘플 명단 출력
    return ["김광녕(팀장)", "김형정", "김홍석", "남광봉", "박명식", "설동민", "원상호", "유정욱", "이병동", 
            "이홍범", "임정빈", "정성영", "정현철", "조관진", "최주용", "한승엽", "홍성화", "이명주"]

# 5. 세션 상태 캐싱 공간 초기화 (에러 방지의 핵심)
if 'members' not in st.session_state:
    st.session_state.members = load_initial_members()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
if 'available_seats' not in st.session_state:
    st.session_state.available_seats = list(SEAT_COORDINATES.keys())

# 6. 공통 클릭 및 배정 처리 로직
def assign_seat(name):
    if st.session_state.available_seats:
        chosen_seat = random.choice(st.session_state.available_seats)
        st.session_state.available_seats.remove(chosen_seat)
        st.session_state.assignments[chosen_seat] = name
        st.session_state.members.remove(name)
        st.rerun()

# 7. 초기화 기능 정의
def reset_program():
    st.session_state.members = load_initial_members()
    st.session_state.assignments = {}
    st.session_state.available_seats = list(SEAT_COORDINATES.keys())
    st.rerun()

# ------------------------------------------------------------------
# 공통 상단 영역: 타이틀 및 우측 상단 초기화 버튼 배치
# ------------------------------------------------------------------
title_col, btn_col = st.columns([4, 1])
title_col.subheader("🖥️ 오피스 자율 좌석 배치 시스템")
with btn_col:
    # 화면 우측 상단에 배치되는 초기화 버튼
    if st.button("🔄 초기화", key="reset_btn", use_container_width=True):
        reset_program()

# ------------------------------------------------------------------
# [1] PC용 환경 레이아웃 (화면 너비 800px 이상일 때 가동)
# ------------------------------------------------------------------
st.markdown("<div class='pc-layout'>", unsafe_allow_html=True)
pc_left, pc_right = st.columns([1, 2.2])

with pc_left:
    st.markdown("<h2>👥 선택 대기 명단</h2>", unsafe_allow_html=True)
    if st.session_state.members:
        # 좌측에 정확히 2X9 배열 구조 생성
        pc_grid_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.members):
            col_target = pc_grid_cols[idx % 2]
            if col_target.button(name, key=f"pc_member_{name}_{idx}", use_container_width=True):
                assign_seat(name)
    else:
        st.success("모든 배정이 완료되었습니다!")

with pc_right:
    st.markdown("<h2>🪑 실시간 배치 도면</h2>", unsafe_allow_html=True)
    image_path = "좌석배치.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        
        # HTML 레이어를 통해 도면 위에 이름표 안착
        html_code = "<div class='image-container'>"
        html_code += f"<img src='data:image/png;base64,{img_base64}' class='bg-image'>"
        
        for seat, user_name in st.session_state.assignments.items():
            pos = SEAT_COORDINATES[seat]
            class_style = "name-leader" if "팀장" in user_name else "name-member"
            html_code += f"<div class='floating-name {class_style}' style='top:{pos['top']}; left:{pos['left']};'>{user_name}</div>"
        html_code += "</div>"
        st.markdown(html_code, unsafe_allow_html=True)
    else:
        st.error("폴더에 '좌석배치.png' 파일이 존재하지 않습니다.")
st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# [2] 모바일폰용 환경 레이아웃 (화면 너비 799px 이하일 때 가동)
# ------------------------------------------------------------------
st.markdown("<div class='mobile-layout'>", unsafe_allow_html=True)

# [상단 배치] 명단 영역을 축소하여 4X5 배열 구조로 생성
st.markdown("<h2>👥 선택 대기 명단 (모바일)</h2>", unsafe_allow_html=True)
if st.session_state.members:
    mobile_grid_cols = st.columns(4)  # 4열 바둑판 배열
    for idx, name in enumerate(st.session_state.members):
        col_target = mobile_grid_cols[idx % 4]
        if col_target.button(name, key=f"mo_member_{name}_{idx}", use_container_width=True):
            assign_seat(name)
else:
    st.success("모든 배정이 완료되었습니다!")

# [하단 배치] 축소 동기화된 좌석배치 이미지 및 오버레이 이름표 위치
st.markdown("<br><h2>🪑 실시간 배치 도면 (모바일)</h2>", unsafe_allow_html=True)
if os.path.exists(image_path):
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()
    
    html_code_mo = "<div class='image-container'>"
    html_code_mo += f"<img src='data:image/png;base64,{img_base64}' class='bg-image'>"
    
    for seat, user_name in st.session_state.assignments.items():
        pos = SEAT_COORDINATES[seat]
        class_style = "name-leader" if "팀장" in user_name else "name-member"
        html_code_mo += f"<div class='floating-name {class_style}' style='top:{pos['top']}; left:{pos['left']};'>{user_name}</div>"
    html_code_mo += "</div>"
    st.markdown(html_code_mo, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)