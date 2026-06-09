import streamlit as st
import pandas as pd
import random
import os
import base64

# 1. 반응형 웹 환경 설정
st.set_page_config(
    page_title="이미지 랜덤 매핑 좌석 배치 에이전트", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 인라인 CSS: 이미지 위에 이름을 절대 좌표로 얹고 기기별 명단 격자 제어
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    h1 { font-size: 1.6rem !important; text-align: center; margin-bottom: 0.2rem; }
    .sub-title-text { font-size: 0.8rem; color: #7F8C8D; text-align: center; margin-bottom: 0.8rem; }
    h3 { font-size: 1.1rem !important; margin-bottom: 0.4rem !important; }

    /* 반응형 기기별 명단 뷰 분기 */
    @media (min-width: 800px) { .pc-hint { display: block; } .mobile-hint { display: none; } }
    @media (max-width: 799px) { .pc-hint { display: none; } .mobile-hint { display: block; } }

    /* 이미지 컨테이너 (좌표 기준점) */
    .image-container {
        position: relative;
        width: 100%;
        display: inline-block;
    }
    
    /* 도면 이미지 반응형 스타일 */
    .bg-image {
        width: 100%;
        height: auto;
        display: block;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* 이미지 위에 랜덤하게 올라갈 이름표 스타일 (고대비 및 터치 감안) */
    .floating-name {
        position: absolute;
        transform: translate(-50%, -50%); /* 좌표의 정중앙에 이름이 오도록 정렬 */
        padding: 4px 8px;
        font-size: 12px;
        font-weight: bold;
        border-radius: 4px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.20);
        white-space: nowrap;
        pointer-events: none; /* 클릭 이벤트 방해 방지 */
    }
    .name-leader { background-color: #FFEB3B; color: #E65100; border: 2px solid #E65100; }
    .name-member { background-color: #2ECC71; color: #FFFFFF; border: 1px solid #27AE60; }
    </style>
""", unsafe_allow_html=True)

# 2. 데이터 로드 및 초기화
def load_member_list():
    file_name = "명단.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name)
            names = df.iloc[:, 0].dropna().astype(str).tolist()
            return [name.strip() for name in names if name.strip()]
        except:
            return [f"팀원{i}" for i in range(1, 19)]
    return [f"홍길동{i}" for i in range(1, 19)]

if 'original_members' not in st.session_state:
    st.session_state.original_members = load_member_list()
if 'current_members' not in st.session_state:
    st.session_state.current_members = st.session_state.original_members.copy()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}

# 📍 좌석별 이미지 내 상대 위치 좌표 설정 (top: 위에서부터 %, left: 왼쪽에서부터 %)
# 실제 사용하는 '좌석배치.png' 도면 속 책상 위치에 맞춰 이 퍼센트 숫자들을 미세 조정해 주세요.
SEAT_COORDINATES = {
    # 1행 (A~F)
    'A': {'top': '12%', 'left': '18%'}, 'B': {'top': '12%', 'left': '32%'}, 'C': {'top': '12%', 'left': '45%'},
    'D': {'top': '12%', 'left': '65%'}, 'E': {'top': '12%', 'left': '78%'}, 'F': {'top': '12%', 'left': '91%'},
    # 3행 (G~K) -> G 자리는 기둥이므로 H가 첫 번째 좌석이 됨
    'G': {'top': '42%', 'left': '32%'}, 'H': {'top': '42%', 'left': '45%'},
    'I': {'top': '42%', 'left': '65%'}, 'J': {'top': '42%', 'left': '78%'}, 'K': {'top': '42%', 'left': '91%'},
    # 4행 (L~Q)
    'L': {'top': '58%', 'left': '18%'}, 'M': {'top': '58%', 'left': '32%'}, 'N': {'top': '58%', 'left': '45%'},
    'O': {'top': '58%', 'left': '65%'}, 'P': {'top': '58%', 'left': '78%'}, 'Q': {'top': '58%', 'left': '91%'},
    # 6행 (R~W)
    'R': {'top': '88%', 'left': '18%'}, 'S': {'top': '88%', 'left': '32%'}, 'T': {'top': '88%', 'left': '45%'},
    'U': {'top': '88%', 'left': '65%'}, 'V': {'top': '88%', 'left': '78%'}, 'W': {'top': '88%', 'left': '91%'}
}

# 랜덤 타겟팅을 위한 실시간 빈 잔여 좌석 계산
all_valid_seats = list(SEAT_COORDINATES.keys())
assigned_seats = list(st.session_state.assignments.keys())
available_seats = [s for s in all_valid_seats if s not in assigned_seats]

def reset_all():
    st.session_state.current_members = st.session_state.original_members.copy()
    st.session_state.assignments = {}

# --- 메인 레이아웃 구성 ---
st.markdown("<h1>🖥️ 이미지 랜덤 매핑 좌석 배치 에이전트</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title-text'>명단을 터치하면 빈 좌석(A~W) 중 랜덤으로 자동 추첨되어 이미지 위에 표기됩니다.</div>", unsafe_allow_html=True)

left_panel, right_panel = st.columns([1, 1.8])

# --- [1] 좌측 패널: 팀 명단 영역 ---
with left_panel:
    st.markdown("<h3>👥 팀 명단</h3>", unsafe_allow_html=True)
    
    if st.session_state.current_members:
        # PC 환경: 가로 2열(2x9) 배열로 단정하게 표시
        st.markdown("<div class='pc-hint'>", unsafe_allow_html=True)
        pc_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = pc_cols[idx % 2]
            if col_target.button(name, key=f"pc_{name}", use_container_width=True):
                if available_seats:
                    # ⭐ 핵심: 남아있는 빈 좌석 중 무작위로 하나를 선택(추첨)
                    chosen_seat = random.choice(available_seats)
                    st.session_state.assignments[chosen_seat]