import streamlit as st
import pandas as pd
import random
import os
import base64

# 1. PC 화면 최적화 및 레이아웃 기본 설정
st.set_page_config(
    page_title="오피스 좌석 배치 프로그램",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 오차 없는 절대 정중앙 배치를 위한 CSS 주입
st.markdown("""
    <style>
    /* 전체 레이아웃 패딩 최적화 */
    .block-container {
        padding: 1.5rem 1rem !important;
    }
    .section-title { 
        font-size: 1.4rem !important; 
        font-weight: bold; 
        margin-bottom: 1rem !important; 
        color: #2C3E50; 
    }
    
    /* 대기 명단 네모 박스 스타일 (2X9 배열) */
    div.stButton > button {
        width: 100% !important;
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #dcdcdc !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 10px 5px !important;
        min-height: 45px !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #4A90E2 !important;
        background-color: #f0f7ff !important;
    }

    /* 독립 이미지 컨테이너 설정 */
    .image-container {
        position: relative !important;
        width: 100% !important;
        display: block !important;
        margin: 0 auto !important;
        padding: 0 !important;
    }
    .bg-image {
        width: 100% !important;
        height: auto !important;
        display: block !important;
        border-radius: 6px;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 이름표 뱃지를 좌석 사각형 슬롯의 완벽한 수평/수직 중간에 위치시키는 정렬법 */
    .floating-name {
        position: absolute !important;
        display: inline-block !important;
        transform: translate(-50%, -50%) !important; 
        -webkit-transform: translate(-50%, -50%) !important;
        -ms-transform: translate(-50%, -50%) !important;
        
        padding: 5px 10px !important;
        font-weight: bold !important;
        font-size: 13px !important;
        min-width: 75px !important;
        border-radius: 4px !important;
        text-align: center !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
        white-space: nowrap !important;
        pointer-events: none !important;
        z-index: 999 !important;
    }
    
    /* 고대비 뱃지 컬러 서식 */
    .name-leader { background-color: #FFEB3B !important; color: #E65100 !important; border: 2px solid #E65100 !important; }
    .name-member { background-color: #2ECC71 !important; color: #FFFFFF !important; border: 1px solid #27AE60 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 🎯 [동적 좌표 계산 시스템] 좌석배치.xlsx 파일에서 슬롯 위치를 읽어와 자동 비율화
def load_seat_coordinates():
    file_name = "좌석배치.xlsx"
    coordinates = {}
    
    if os.path.exists(file_name):
        try:
            # 헤더 없이 모든 셀 데이터를 가져옵니다.
            df = pd.read_excel(file_name, header=None)
            total_rows = len(df)
            total_cols = len(df.columns)
            
            for r_idx, row in df.iterrows():
                for c_idx, val in enumerate(row):
                    if pd.notna(val):
                        seat_name = str(val).strip()
                        if seat_name != "":
                            # 엑셀 셀의 상대적 행/열 위치를 기반으로 정중앙 퍼센트(%) 좌표 생성
                            # 여백 밸런스를 고려하여 정밀한 비율 분할을 적용합니다.
                            top_ratio = ((r_idx + 0.5) / total_rows) * 100
                            left_ratio = ((c_idx + 0.5) / total_cols) * 100
                            
                            coordinates[seat_name] = {
                                'top': f"{round(top_ratio, 2)}%",
                                'left': f"{round(left_ratio, 2)}%"
                            }
            return coordinates
        except Exception as e:
            st.sidebar.error(f"좌석배치.xlsx 로드 실패: {e}")
            
    # 파일이 없거나 에러 발생 시 최신 이미지 기준 백업 고정 좌표 작동
    return {
        'A': {'top': '8.2%', 'left': '18.4%'}, 'B': {'top': '8.2%', 'left': '31.6%'}, 'C': {'top': '8.2%', 'left': '44.9%'},
        'D': {'top': '8.2%', 'left': '65.4%'}, 'E': {'top': '8.2%', 'left': '78.7%'}, 'F': {'top': '8.2%', 'left': '91.8%'},
        'G': {'top': '42.0%', 'left': '31.6%'}, 'H': {'top': '42.0%', 'left': '44.9%'},
        'I': {'top': '42.0%', 'left': '65.4%'}, 'J': {'top': '42.0%', 'left': '78.7%'}, 'K': {'top': '42.0%', 'left': '91.8%'},
        'L': {'top': '58.8%', 'left': '18.4%'}, 'M': {'top': '58.8%', 'left': '31.6%'}, 'N': {'top': '58.8%', 'left': '44.9%'},
        'O': {'top': '58.8%', 'left': '65.4%'}, 'P': {'top': '58.8%', 'left': '78.7%'}, 'Q': {'top': '58.8%', 'left': '91.8%'},
        'R': {'top': '92.6%', 'left': '18.4%'}, 'S': {'top': '92.6%', 'left': '31.6%'}, 'T': {'top': '92.6%', 'left': '44.9%'},
        'U': {'top': '92.6%', 'left': '65.4%'}, 'V': {'top': '92.6%', 'left': '78.7%'}, 'W': {'top': '92.6%', 'left': '91.8%'}
    }

# 4. 데이터 로드 함수 (명단.xlsx 지원)
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

# 5. 세션 상태 및 좌표 실시간 마운트
SEAT_COORDINATES = load_seat_coordinates()

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
# 상단 글로벌 제어바 헤더 (타이틀 및 우측 상단 초기화 버튼)
# ------------------------------------------------------------------
title_col, btn_col = st.columns([4, 1])
title_col.subheader("🖥️ 오피스 자율 좌석 배치 시스템")
with btn_col:
    if st.button("🔄 초기화", key="reset_btn", use_container_width=True):
        reset_program()

# ------------------------------------------------------------------
# PC 전용 레이아웃 분할 (좌측 명단 2X9, 우측 도면)
# ------------------------------------------------------------------
pc_left, pc_right = st.columns([1, 2.2])

# [좌측] 선택 대기 명단 영역 (2X9 격자 배열)
with pc_left:
    st.markdown("<div class='section-title'>👥 선택 대기 명단</div>", unsafe_allow_html=True)
    if st.session_state.members:
        pc_grid_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.members):
            col_target = pc_grid_cols[idx % 2]
            if col_target.button(name, key=f"pc_member_{name}_{idx}", use_container_width=True):
                assign_seat(name)
    else:
        st.success("모든 배정이 완료되었습니다!")

# [우측] 실시간 배치 도면 영역 (엑셀 기반 자동 연동 구조)
with pc_right:
    st.markdown("<div class='section-title'>🪑 실시간 배치 도면</div>", unsafe_allow_html=True)
    image_path = "좌석배치.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        
        html_code = "<div class='image-container'>"
        html_code += f"<img src='data:image/png;base64,{img_base64}' class='bg-image'>"
        
        # 엑셀 데이터로부터 계산된 동적 좌표 위에 이름표 매핑
        for seat, user_name in st.session_state.assignments.items():
            if seat in SEAT_COORDINATES:
                pos = SEAT_COORDINATES[seat]
                class_style = "name-leader" if "팀장" in user_name else "name-member"
                html_code += f"<div class='floating-name {class_style}' style='top:{pos['top']}; left:{pos['left']};'>{user_name}</div>"
        html_code += "</div>"
        st.markdown(html_code, unsafe_allow_html=True)
    else:
        st.error("폴더에 '좌석배치.png' 파일이 존재하지 않습니다.")