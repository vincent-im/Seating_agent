import streamlit as st
import pandas as pd
import random
import os
import base64

# 1. 반응형 및 모바일 접근성을 위한 기본 페이지 설정
st.set_page_config(
    page_title="도면 맵핑 좌석 배치 에이전트", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 인라인 CSS: 실제 도면 비율 유지 및 모바일 초소형 뷰 보장 스타일링
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

    /* [반응형 기기별 명단 뷰 분기] */
    @media (min-width: 800px) { 
        .pc-hint { display: block; } 
        .mobile-hint { display: none; } 
        div.stButton > button {
            font-size: 0.9rem !important;
            padding: 8px 4px !important;
            min-height: 40px !important;
        }
        .floating-name {
            font-size: 12px !important;
            padding: 4px 8px !important;
        }
    }
    @media (max-width: 799px) { 
        .pc-hint { display: none; } 
        .mobile-hint { display: block; } 
        /* 모바일 5x4 배열 단추 초소형화 */
        div.stButton > button {
            font-size: 0.7rem !important;
            padding: 2px 1px !important;
            min-height: 28px !important;
            margin-bottom: 1px !important;
        }
        /* 모바일 축소 이미지 맞춤 소형 이름표 */
        .floating-name {
            font-size: 8.5px !important;
            padding: 2px 4px !important;
        }
    }

    /* 이미지와 이름표를 묶는 절대 좌표 기준 컨테이너 */
    .image-container {
        position: relative;
        width: 100%;
        display: inline-block;
    }
    
    /* 도면 이미지 반응형 스타일 (모바일에서도 가로폭에 맞춰 자동 축소) */
    .bg-image {
        width: 100%;
        height: auto;
        display: block;
        border-radius: 6px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* 이미지 비율에 동기화되는 절대 위치 이름표 서식 */
    .floating-name {
        position: absolute;
        transform: translate(-50%, -50%);
        font-weight: bold;
        border-radius: 3px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        white-space: nowrap;
        pointer-events: none;
        z-index: 10;
    }
    .name-leader { background-color: #FFEB3B; color: #E65100; border: 1.5px solid #E65100; }
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

# 📍 [정밀 조율] 제공해주신 실제 배치 도면 이미지 비율에 맞춘 각 알파벳 책상 중심 좌표 설정
# 가로(left) 비율 및 세로(top) 분할 구조를 실제 도면 격자에 맞춰 한 땀 한 땀 최적화했습니다.
SEAT_COORDINATES = {
    # 1번째 줄 (A ~ F)
    'A': {'top': '14.5%', 'left': '18.2%'}, 'B': {'top': '14.5%', 'left': '31.4%'}, 'C': {'top': '14.5%', 'left': '44.8%'},
    'D': {'top': '14.5%', 'left': '65.2%'}, 'E': {'top': '14.5%', 'left': '78.5%'}, 'F': {'top': '14.5%', 'left': '91.6%'},
    
    # 2번째 줄 (G ~ K) -> 창가 첫 자리는 기둥이므로 복도 방향인 G부터 시작
    'G': {'top': '44.2%', 'left': '31.4%'}, 'H': {'top': '44.2%', 'left': '44.8%'},
    'I': {'top': '44.2%', 'left': '65.2%'}, 'J': {'top': '44.2%', 'left': '78.5%'}, 'K': {'top': '44.2%', 'left': '91.6%'},
    
    # 3번째 줄 (L ~ Q)
    'L': {'top': '59.0%', 'left': '18.2%'}, 'M': {'top': '59.0%', 'left': '31.4%'}, 'N': {'top': '59.0%', 'left': '44.8%'},
    'O': {'top': '59.0%', 'left': '65.2%'}, 'P': {'top': '59.0%', 'left': '78.5%'}, 'Q': {'top': '59.0%', 'left': '91.6%'},
    
    # 4번째 줄 (R ~ W) -> 요청하신 사양대로 맨 오른쪽 빈 곳이 최종 W 자리로 맵핑됨
    'R': {'top': '88.5%', 'left': '18.2%'}, 'S': {'top': '88.5%', 'left': '31.4%'}, 'T': {'top': '88.5%', 'left': '44.8%'},
    'U': {'top': '88.5%', 'left': '65.2%'}, 'V': {'top': '88.5%', 'left': '78.5%'}, 'W': {'top': '88.5%', 'left': '91.6%'}
}

# 세션 상태 캐싱 시스템 연동 (연속 클릭 버그 해결 단락)
if 'original_members' not in st.session_state:
    st.session_state.original_members = load_member_list()
if 'current_members' not in st.session_state:
    st.session_state.current_members = st.session_state.original_members.copy()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
if 'available_seats' not in st.session_state:
    st.session_state.available_seats = list(SEAT_COORDINATES.keys())

def reset_all():
    st.session_state.current_members = st.session_state.original_members.copy()
    st.session_state.assignments = {}
    st.session_state.available_seats = list(SEAT_COORDINATES.keys())

# --- 화면 UI 빌드 시작 ---
st.markdown("<h1>🖥️ 이미지 기반 팀 좌석 랜덤 배치 에이전트</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title-text'>기기 크기에 맞춰 도면과 명단 배열이 자동 축소 및 정렬됩니다.</div>", unsafe_allow_html=True)

# 레이아웃 정의 (PC 가로 분할 / 모바일 세로 적층 자동 연동)
left_panel, right_panel = st.columns([1, 1.8])

# --- [1] 좌측/상단 패널: 팀 명단 영역 ---
with left_panel:
    st.markdown("<h3>👥 팀 명단</h3>", unsafe_allow_html=True)
    
    if st.session_state.current_members:
        # PC용 명단 레이아웃 (가로 2열 바둑판 구조)
        st.markdown("<div class='pc-hint'>", unsafe_allow_html=True)
        pc_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = pc_cols[idx % 2]
            if col_target.button(name, key=f"pc_{name}_{len(st.session_state.current_members)}", use_container_width=True):
                if st.session_state.available_seats:
                    chosen_seat = random.choice(st.session_state.available_seats)
                    st.session_state.available_seats.remove(chosen_seat)
                    st.session_state.assignments[chosen_seat] = name
                    st.session_state.current_members.remove(name)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 모바일용 명단 레이아웃 (요청 반영: 스마트폰 상단 공간 절약을 위한 5x4 컴팩트 격자 배열)
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
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("🎉 모든 팀원의 좌석 배치가 완료되었습니다!")

# --- [2] 우측/하단 패널: 실제 도면 위에 이름 오버레이 영역 ---
with right_panel:
    st.markdown("<hr style='margin: 0.6rem 0;' class='mobile-hint'>", unsafe_allow_html=True)
    title_space, reset_space = st.columns([3, 1])
    title_space.markdown("<h3>🪑 실시간 배치도</h3>", unsafe_allow_html=True)
    
    with reset_space:
        if st.button("🔄 전체 리셋", key="reset_trigger", use_container_width=True):
            reset_all()
            st.rerun()

    image_path = "좌석배치.png"
    if os.path.exists(image_path):
        try:
            html_buffer = "<div class='image-container'>"
            
            # 1. 업로드해주신 원본 좌석배치.png 이미지 인코딩 로드
            with open(image_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            html_buffer += f"<img src='data:image/png;base64,{img_base64}' class='bg-image' alt='사무실 좌석 배치도'>"
            
            # 2. 이미지 위에 랜덤 배정 완료된 이름표 레이어 팝업
            for seat, user_name in st.session_state.assignments.items():
                if seat in SEAT_COORDINATES:
                    pos = SEAT_COORDINATES[seat]
                    class_type = "name-leader" if "팀장" in user_name else "name-member"
                    
                    # 퍼센트(%) 단위를 사용하여 스마트폰 화면 축소 시에도 이름표 위치가 정확히 연동하여 함께 축소됩니다.
                    html_buffer += f"""
                        <div class='floating-name {class_type}' style='top: {pos["top"]}; left: {pos["left"]};'>
                            {user_name}
                        </div>
                    """
            html_buffer += "</div>"
            
            # 3. 완성된 HTML 인터랙티브 뷰 주입
            st.markdown(html_buffer, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"도면 처리 엔진 구동 실패: {e}")
    else:
        st.error(f"🚨 시스템 에러: 폴더 내에서 '{image_path}' 파일을 읽어올 수 없습니다. 경로를 점검해 주세요.")