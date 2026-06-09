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

# 2. 강제 정중앙 오버레이 정렬을 위한 CSS 주입 (수평/수직 완벽 보정)
st.markdown("""
    <style>
    /* 전체 레이아웃 패딩 최적화 */
    .block-container {
        padding: 1.5rem 1rem !important;
    }
    h2 { font-size: 1.4rem !important; font-weight: bold; margin-bottom: 1rem !important; }
    
    /* 대기 명단 네모 박스 스타일 */
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

    /* 반응형 화면 제어 */
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
        div.stButton > button {
            font-size: 0.75rem !important;
            padding: 4px 2px !important;
            min-height: 32px !important;
            border-radius: 4px !important;
        }
    }

    /* 💡 [정중앙 정렬 핵심 코어] 이미지 컨테이너 및 앵커 포인트 정의 */
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
    
    /* 이름표 가독성 폰트 규격 및 절대 정중앙(-50%, -50%) 강제 우선순위 지정 */
    .floating-name {
        position: absolute !important;
        display: inline-block !important;
        /* 박스의 정중앙을 top, left 좌표값과 완벽히 잃치시키는 축 변경 */
        transform: translate(-50%, -50%) !important; 
        -webkit-transform: translate(-50%, -50%) !important;
        -ms-transform: translate(-50%, -50%) !important;
        
        padding: 5px 10px !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        text-align: center !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
        white-space: nowrap !important;
        pointer-events: none !important;
        z-index: 999 !important;
    }
    
    /* 기기별 폰트 밸런스 패치 */
    @media (min-width: 800px) {
        .floating-name {
            font-size: 13px !important;
            min-width: 70px !important;
        }
    }
    @media (max-width: 799px) {
        .floating-name {
            font-size: 9px !important;
            padding: 2px 4px !important;
            min-width: 45px !important;
        }
    }
    
    /* 이름표 고대비 배색 */
    .name-leader { background-color: #FFEB3B !important; color: #E65100 !important; border: 2px solid #E65100 !important; }
    .name-member { background-color: #2ECC71 !important; color: #FFFFFF !important; border: 1px solid #27AE60 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 🎯 [정밀 실측 수정] 실제 '좌석배치.png' 파일 도면의 격자 슬롯별 정중앙 매핑 좌표 (%)
SEAT_COORDINATES = {
    # 1번째 라인 (A ~ F)
    'A': {'top': '14.8%', 'left': '18.4%'}, 'B': {'top': '14.8%', 'left': '31.6%'}, 'C': {'top': '14.8%', 'left': '44.9%'},
    'D': {'top': '14.8%', 'left': '65.4%'}, 'E': {'top': '14.8%', 'left': '78.7%'}, 'F': {'top': '14.8%', 'left': '91.8%'},
    
    # 2번째 라인 (G ~ K) -> 기둥 공백 한 칸 건너뛰고 G부터 시작
    'G': {'top': '44.4%', 'left': '31.6%'}, 'H': {'top': '44.4%', 'left': '44.9%'},
    'I': {'top': '44.4%', 'left': '65.4%'}, 'J': {'top': '44.4%', 'left': '78.7%'}, 'K': {'top': '44.4%', 'left': '91.8%'},
    
    # 3번째 라인 (L ~ Q)
    'L': {'top': '59.3%', 'left': '18.4%'}, 'M': {'top': '59.3%', 'left': '31.6%'}, 'N': {'top': '59.3%', 'left': '44.9%'},
    'O': {'top': '59.3%', 'left': '65.4%'}, 'P': {'top': '59.3%', 'left': '78.7%'}, 'Q': {'top': '59.3%', 'left': '91.8%'},
    
    # 4번째 라인 (R ~ W) -> 맨 오른쪽 공백 슬롯이 최종 W 매칭
    'R': {'top': '88.8%', 'left': '18.4%'}, 'S': {'top': '88.8%', 'left': '31.6%'}, 'T': {'top': '88.8%', 'left': '44.9%'},
    'U': {'top': '88.8%', 'left': '65.4%'}, 'V': {'top': '88.8%', 'left': '78.7%'}, 'W': {'top': '88.8%', 'left': '91.8%'}
}

# 4. 데이터 로드 함수 (명단.xlsx)
def load_initial_members():
    file_name = "명단.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name)
            names = df.iloc[:, 0].dropna().astype(str).tolist()
            return [name.strip() for name in names if name.strip()]
        except:
            pass
    return ["김광녕(팀장)", "김형정", "김홍석", "남광봉", "박명식", "설동민", "원상호", "유정욱", "이병동", 
            "이홍범", "임정빈", "정성영", "정현철", "조관진", "최주용", "한승엽", "홍성화", "이명주"]

# 5. 세션 상태 초기화
if 'members' not in st.session_state:
    st.session_state.members = load_initial_members()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
if 'available_seats' not in st.session_state:
    st.session_state.available_seats = list(SEAT_COORDINATES.keys())

# 6. 공통 배정 처리 함수
def assign_seat(name):
    if st.session_state.available_seats:
        chosen_seat = random.choice(st.session_state.available_seats)
        st.session_state.available_seats.remove(chosen_seat)
        st.session_state.assignments[chosen_seat] = name
        st.session_state.members.remove(name)
        st.rerun()

# 7. 리셋 로직
def reset_program():
    st.session_state.members = load_initial_members()
    st.session_state.assignments = {}
    st.session_state.available_seats = list(SEAT_COORDINATES.keys())
    st.rerun()

# ------------------------------------------------------------------
# 상단 글로벌 제어바 헤더
# ------------------------------------------------------------------
title_col, btn_col = st.columns([4, 1])
title_col.subheader("🖥️ 오피스 자율 좌석 배치 시스템")
with btn_col:
    if st.button("🔄 초기화", key="reset_btn", use_container_width=True):
        reset_program()

# ------------------------------------------------------------------
# [1] PC 브라우저용 대형 레이아웃 뷰
# ------------------------------------------------------------------
st.markdown("<div class='pc-layout'>", unsafe_allow_html=True)
pc_left, pc_right = st.columns([1, 2.2])

with pc_left:
    st.markdown("<h2>👥 선택 대기 명단</h2>", unsafe_allow_html=True)
    if st.session_state.members:
        pc_grid_cols = st.columns(2) # 요구사양: 2X9 구조 배열
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
        
        html_code = "<div class='image-container'>"
        html_code += f"<img src='data:image/png;base64,{img_base64}' class='bg-image'>"
        
        # 실시간 레이어 이름표 오버레이 매핑
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
# [2] 스마트폰 모바일 브라우저용 축소 레이아웃 뷰
# ------------------------------------------------------------------
st.markdown("<div class='mobile-layout'>", unsafe_allow_html=True)

# 요구사양: 상단에 명단 박스 크기를 축소하여 4X5 배열 배치
st.markdown("<h2>👥 선택 대기 명단 (모바일)</h2>", unsafe_allow_html=True)
if st.session_state.members:
    mobile_grid_cols = st.columns(4) # 4열 배치 구조
    for idx, name in enumerate(st.session_state.members):
        col_target = mobile_grid_cols[idx % 4]
        if col_target.button(name, key=f"mo_member_{name}_{idx}", use_container_width=True):
            assign_seat(name)
else:
    st.success("모든 배정이 완료되었습니다!")

# 요구사양: 하단에 축소 동기화된 도면 및 중앙정렬 이름표 매핑
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