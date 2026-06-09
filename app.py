import streamlit as st
import pandas as pd
import random
import os

# 1. 반응형 및 모바일 접근성을 위한 기본 페이지 설정
st.set_page_config(
    page_title="팀 좌석 배치 에이전트 (도면 이미지 버전)", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 인라인 CSS: PC와 모바일 환경에 따른 명단 배열 및 텍스트 톤 조절
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    h1 { font-size: 1.6rem !important; margin-bottom: 0.1rem !important; text-align: center; }
    .sub-title-text { font-size: 0.8rem; color: #7F8C8D; text-align: center; margin-bottom: 0.8rem; }
    h3 { font-size: 1.1rem !important; margin-top: 0.4rem !important; margin-bottom: 0.3rem !important; }

    /* PC 환경 스타일 (화면 폭 800px 이상) */
    @media (min-width: 800px) {
        .pc-hint { display: block; }
        .mobile-hint { display: none; }
        div.stButton > button {
            font-size: 0.9rem !important;
            padding: 8px 4px !important;
            min-height: 40px !important;
            border-radius: 5px !important;
        }
    }
    
    /* 모바일 환경 스타일 (화면 폭 800px 미만) */
    @media (max-width: 799px) {
        .pc-hint { display: none; }
        .mobile-hint { display: block; }
        div.stButton > button {
            font-size: 0.73rem !important;
            padding: 2px 1px !important;
            min-height: 28px !important;
            margin-bottom: 1px !important;
            border-radius: 3px !important;
        }
    }

    /* 배정 현황 보드 스타일 */
    .status-board {
        background-color: #F8F9FA;
        border: 1px solid #E9ECEF;
        border-radius: 6px;
        padding: 10px;
        margin-top: 5px;
    }
    .status-item {
        display: inline-block;
        padding: 4px 8px;
        margin: 2px;
        background-color: #E8F5E9;
        color: #2E7D32;
        font-size: 11px;
        font-weight: bold;
        border-radius: 4px;
        border: 1px solid #A5D6A7;
    }
    .status-item-leader {
        background-color: #FFF3E0;
        color: #D84315;
        border: 1px solid #FFCC80;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 및 초기화 구조 정의
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

if 'original_members' not in st.session_state:
    st.session_state.original_members = load_member_list()
if 'current_members' not in st.session_state:
    st.session_state.current_members = st.session_state.original_members.copy()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}

# 고정된 좌석 알파벳 풀 (G 기둥 제외, 마지막 칸 W)
seat_structure = [
    ["A", "B", "C", "", "D", "E", "F"],
    ["기둥", "G", "H", "", "I", "J", "K"], 
    ["L", "M", "N", "", "O", "P", "Q"],   
    ["R", "S", "T", "", "U", "V", "W"]
]
all_valid_seats = [cell for row in seat_structure for cell in row if cell and cell != "기둥"]
assigned_seats = list(st.session_state.assignments.keys())
available_seats = [s for s in all_valid_seats if s not in assigned_seats]

def reset_all():
    st.session_state.current_members = st.session_state.original_members.copy()
    st.session_state.assignments = {}

# --- 레이아웃 타이틀 ---
st.markdown("<h1>🖥️ 하이브리드 팀 좌석 배치 에이전트</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title-text'>배치도 도면 이미지를 기반으로 무작위 좌석 배정을 진행합니다.</div>", unsafe_allow_html=True)

# PC 뷰에서는 좌우 구조 / 모바일 뷰에서는 상하 구조 자동 전환
left_panel, right_panel = st.columns([1, 1.8])

# -------------------------------------------------------------
# [1] 좌측 패널: 팀 명단 영역
# -------------------------------------------------------------
with left_panel:
    st.markdown("<h3>👥 팀 명단</h3>", unsafe_allow_html=True)
    
    if st.session_state.current_members:
        # PC 환경용 2x9 격자 배열
        st.markdown("<div class='pc-hint'>", unsafe_allow_html=True)
        pc_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = pc_cols[idx % 2]
            if col_target.button(name, key=f"pc_btn_{name}", use_container_width=True):
                if available_seats:
                    chosen_seat = random.choice(available_seats)
                    st.session_state.assignments[chosen_seat] = name
                    st.session_state.current_members.remove(name)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 모바일 환경용 5x4 격자 배열
        st.markdown("<div class='mobile-hint'>", unsafe_allow_html=True)
        mobile_cols = st.columns(5)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = mobile_cols[idx % 5]
            if col_target.button(name, key=f"mo_btn_{name}", use_container_width=True):
                if available_seats:
                    chosen_seat = random.choice(available_seats)
                    st.session_state.assignments[chosen_seat] = name
                    st.session_state.current_members.remove(name)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("🎉 모든 팀원 배치가 완료되었습니다!")

    # 실시간 배정 명단 텍스트 보드 (웹 접근성 보완 및 이미지 보조용)
    st.markdown("<h3>📊 실시간 배정 현황 리스트</h3>", unsafe_allow_html=True)
    if st.session_state.assignments:
        html_status = "<div class='status-board'>"
        # 좌석 이름 순으로 정렬해서 표시
        for seat in sorted(st.session_state.assignments.keys()):
            user_name = st.session_state.assignments[seat]
            style_class = "status-item status-item-leader" if "팀장" in user_name else "status-item"
            html_status += f"<span class='{style_class}'>{seat}: {user_name}</span>"
        html_status += "</div>"
        st.markdown(html_status, unsafe_allow_html=True)
    else:
        st.caption("아직 배정된 좌석이 없습니다.")

# -------------------------------------------------------------
# [2] 우측 패널: 좌석배치도 그림 출력 영역
# -------------------------------------------------------------
with right_panel:
    st.markdown("<hr style='margin: 0.6rem 0;' class='mobile-hint'>", unsafe_allow_html=True)
    
    title_space, reset_space = st.columns([3, 1])
    title_space.markdown("<h3>🪑 오피스 좌석 도면</h3>", unsafe_allow_html=True)
    
    with reset_space:
        if st.button("🔄 전체 리셋", key="global_reset", use_container_width=True):
            reset_all()
            st.rerun()

    # 이미지 로드 및 오류 검증 처리
    image_path = "좌석배치.png"
    if os.path.exists(image_path):
        # PC와 모바일 화면폭에 맞춰 자동으로 꽉 차게 렌더링 (use_container_width=True)
        st.image(image_path, caption="참조용 좌석배치도 도면", use_container_width=True)
    else:
        st.error(
            f"🚨 '{image_path}' 파일을 찾을 수 없습니다.\n\n"
            "파워포인트 파일의 좌석 배치도 그림을 PNG로 저장하여 "
            "이 프로그램 파일과 같은 폴더에 넣어주세요."
        )