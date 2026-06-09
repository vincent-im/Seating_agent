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

# 인라인 CSS
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

    @media (min-width: 800px) { .pc-hint { display: block; } .mobile-hint { display: none; } }
    @media (max-width: 799px) { .pc-hint { display: none; } .mobile-hint { display: block; } }

    .image-container {
        position: relative;
        width: 100%;
        display: inline-block;
    }
    .bg-image {
        width: 100%;
        height: auto;
        display: block;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .floating-name {
        position: absolute;
        transform: translate(-50%, -50%);
        padding: 4px 8px;
        font-size: 12px;
        font-weight: bold;
        border-radius: 4px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.20);
        white-space: nowrap;
        pointer-events: none;
    }
    .name-leader { background-color: #FFEB3B; color: #E65100; border: 2px solid #E65100; }
    .name-member { background-color: #2ECC71; color: #FFFFFF; border: 1px solid #27AE60; }
    </style>
""", unsafe_allow_html=True)

# 📍 좌석별 이미지 내 상대 위치 좌표 설정
SEAT_COORDINATES = {
    'A': {'top': '12%', 'left': '18%'}, 'B': {'top': '12%', 'left': '32%'}, 'C': {'top': '12%', 'left': '45%'},
    'D': {'top': '12%', 'left': '65%'}, 'E': {'top': '12%', 'left': '78%'}, 'F': {'top': '12%', 'left': '91%'},
    'G': {'top': '42%', 'left': '32%'}, 'H': {'top': '42%', 'left': '45%'},
    'I': {'top': '42%', 'left': '65%'}, 'J': {'top': '42%', 'left': '78%'}, 'K': {'top': '42%', 'left': '91%'},
    'L': {'top': '58%', 'left': '18%'}, 'M': {'top': '58%', 'left': '32%'}, 'N': {'top': '58%', 'left': '45%'},
    'O': {'top': '58%', 'left': '65%'}, 'P': {'top': '58%', 'left': '78%'}, 'Q': {'top': '58%', 'left': '91%'},
    'R': {'top': '88%', 'left': '18%'}, 'S': {'top': '88%', 'left': '32%'}, 'T': {'top': '88%', 'left': '45%'},
    'U': {'top': '88%', 'left': '65%'}, 'V': {'top': '88%', 'left': '78%'}, 'W': {'top': '88%', 'left': '91%'}
}

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

# 세션 상태(Session State) 안정화 처리
if 'original_members' not in st.session_state:
    st.session_state.original_members = load_member_list()
if 'current_members' not in st.session_state:
    st.session_state.current_members = st.session_state.original_members.copy()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
# ⭐ 핵심 수정: 잔여 좌석 풀 자체를 세션 상태에 기록하여 유실 방지
if 'available_seats' not in st.session_state:
    st.session_state.available_seats = list(SEAT_COORDINATES.keys())

def reset_all():
    st.session_state.current_members = st.session_state.original_members.copy()
    st.session_state.assignments = {}
    st.session_state.available_seats = list(SEAT_COORDINATES.keys())

# --- 메인 레이아웃 구성 ---
st.markdown("<h1>🖥️ 이미지 랜덤 매핑 좌석 배치 에이전트</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title-text'>명단을 터치하면 빈 좌석(A~W) 중 랜덤으로 자동 추첨되어 이미지 위에 표기됩니다.</div>", unsafe_allow_html=True)

left_panel, right_panel = st.columns([1, 1.8])

# --- [1] 좌측 패널: 팀 명단 영역 ---
with left_panel:
    st.markdown("<h3>👥 팀 명단</h3>", unsafe_allow_html=True)
    
    if st.session_state.current_members:
        # PC 환경: 가로 2열(2x9) 배열
        st.markdown("<div class='pc-hint'>", unsafe_allow_html=True)
        pc_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = pc_cols[idx % 2]
            # 버튼의 중복 생성을 막기 위해 key 고유값 처리
            if col_target.button(name, key=f"pc_{name}_{len(st.session_state.current_members)}", use_container_width=True):
                if st.session_state.available_seats:
                    # 세션 상태에 저장된 안전한 좌석 풀에서 무작위 선택
                    chosen_seat = random.choice(st.session_state.available_seats)
                    st.session_state.available_seats.remove(chosen_seat)
                    st.session_state.assignments[chosen_seat] = name
                    st.session_state.current_members.remove(name)
                    st.rerun()
                else:
                    st.error("모든 좌석이 만석입니다!")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 모바일 환경: 상단 배치용 가로 5열(5x4) 슬림 배열
        st.markdown("<div class='mobile-hint'>", unsafe_allow_html=True)
        mobile_cols = st.columns(5)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = mobile_cols[idx % 5]
            if col_target.button(name, key=f"mo_{name}_{len(st.session_state.current_members)}", use_container_width=True):
                if st.session_state.available_seats:
                    chosen_seat = random.choice(st.session_state.available_seats)
                    st.session_state.available_seats.remove(chosen_seat)
                    st.session_state.assignments[chosen_seat] = name
                    st.session_state.current_members.remove(name)
                    st.rerun()
                else:
                    st.error("모든 좌석이 만석입니다!")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("🎉 모든 팀원의 좌석 배치가 완료되었습니다!")

# --- [2] 우측 패널: 도면 이미지 및 실시간 랜덤 오버레이 영역 ---
with right_panel:
    st.markdown("<hr style='margin: 0.6rem 0;' class='mobile-hint'>", unsafe_allow_html=True)
    title_space, reset_space = st.columns([3, 1])
    title_space.markdown("<h3>🪑 실시간 배치도 (한눈에 보기)</h3>", unsafe_allow_html=True)
    
    with reset_space:
        if st.button("🔄 전체 리셋", key="reset_trigger", use_container_width=True):
            reset_all()
            st.rerun()

    image_path = "좌석배치.png"
    if os.path.exists(image_path):
        try:
            html_buffer = "<div class='image-container'>"
            
            # 배경 이미지 인라인 로드 (Base64)
            with open(image_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            html_buffer += f"<img src='data:image/png;base64,{img_base64}' class='bg-image' alt='사무실 좌석 배치도'>"
            
            # 배정 완료된 이름표 레이어 팝업
            for seat, user_name in st.session_state.assignments.items():
                if seat in SEAT_COORDINATES:
                    pos = SEAT_COORDINATES[seat]
                    class_type = "name-leader" if "팀장" in user_name else "name-member"
                    
                    html_buffer += f"""
                        <div class='floating-name {class_type}' style='top: {pos["top"]}; left: {pos["left"]};'>
                            {user_name}
                        </div>
                    """
            html_buffer += "</div>"
            st.markdown(html_buffer, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"이미지 처리 중 오류 발생: {e}")
    else:
        st.error(f"🚨 폴더 내에서 '{image_path}' 파일을 찾을 수 없습니다. 파일 이름을 확인해 주세요.")