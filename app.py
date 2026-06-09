import streamlit as st
import pandas as pd
import random
import os

# 1. 페이지 설정
st.set_page_config(
    page_title="이미지 맵핑 좌석 배치 에이전트", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 인라인 CSS: 이미지 위에 이름을 절대 좌표로 얹기 위한 핵심 스타일 스타일링
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

    /* 반응형 명단 배열 제어 */
    @media (min-width: 800px) { .pc-hint { display: block; } .mobile-hint { display: none; } }
    @media (max-width: 799px) { .pc-hint { display: none; } .mobile-hint { display: block; } }

    /* 이미지와 이름을 감싸는 컨테이너 (기준점) */
    .image-container {
        position: relative;
        width: 100%;
        display: inline-block;
    }
    
    /* 도면 이미지 스타일 */
    .bg-image {
        width: 100%;
        height: auto;
        display: block;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    /* 이미지 위에 올라갈 이름표 서식 (고대비 및 가독성 확보) */
    .floating-name {
        position: absolute;
        transform: translate(-50%, -50%); /* 지정 좌표의 정중앙에 이름이 오도록 설정 */
        padding: 4px 8px;
        font-size: 12px;
        font-weight: bold;
        border-radius: 4px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        white-space: nowrap;
        pointer-events: none; /* 마우스 클릭 방해 금지 */
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

# 📍 [핵심 수정 구간] 좌석별 이미지 내 상대 좌표 설정 (top: 위에서부터 %, left: 왼쪽에서부터 %)
# 실제 좌석배치.png 이미지의 해상도와 위치에 맞게 이 숫자를 자유롭게 튜닝해 주세요!
SEAT_COORDINATES = {
    # 1행 (A~F)
    'A': {'top': '12%', 'left': '18%'}, 'B': {'top': '12%', 'left': '32%'}, 'C': {'top': '12%', 'left': '45%'},
    'D': {'top': '12%', 'left': '65%'}, 'E': {'top': '12%', 'left': '78%'}, 'F': {'top': '12%', 'left': '91%'},
    # 3행 (G~K) -> 기존 G 자리는 기둥이므로 수동 조정 시 기둥 위치는 제외
    'G': {'top': '42%', 'left': '32%'}, 'H': {'top': '42%', 'left': '45%'},
    'I': {'top': '42%', 'left': '65%'}, 'J': {'top': '42%', 'left': '78%'}, 'K': {'top': '42%', 'left': '91%'},
    # 4행 (L~Q)
    'L': {'top': '58%', 'left': '18%'}, 'M': {'top': '58%', 'left': '32%'}, 'N': {'top': '58%', 'left': '45%'},
    'O': {'top': '58%', 'left': '65%'}, 'P': {'top': '58%', 'left': '78%'}, 'Q': {'top': '58%', 'left': '91%'},
    # 6행 (R~W)
    'R': {'top': '88%', 'left': '18%'}, 'S': {'top': '88%', 'left': '32%'}, 'T': {'top': '88%', 'left': '45%'},
    'U': {'top': '88%', 'left': '65%'}, 'V': {'top': '88%', 'left': '78%'}, 'W': {'top': '88%', 'left': '91%'}
}

all_valid_seats = list(SEAT_COORDINATES.keys())
assigned_seats = list(st.session_state.assignments.keys())
available_seats = [s for s in all_valid_seats if s not in assigned_seats]

def reset_all():
    st.session_state.current_members = st.session_state.original_members.copy()
    st.session_state.assignments = {}

# --- 레이아웃 드로잉 ---
st.markdown("<h1>🖥️ 이미지 맵핑 팀 좌석 배치 에이전트</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title-text'>명단을 터치하면 실제 도면 이미지 위에 이름이 오버레이됩니다.</div>", unsafe_allow_html=True)

left_panel, right_panel = st.columns([1, 1.8])

# --- [1] 좌측 명단 패널 ---
with left_panel:
    st.markdown("<h3>👥 팀 명단</h3>", unsafe_allow_html=True)
    
    if st.session_state.current_members:
        # PC용 2x9 격자
        st.markdown("<div class='pc-hint'>", unsafe_allow_html=True)
        pc_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = pc_cols[idx % 2]
            if col_target.button(name, key=f"pc_{name}", use_container_width=True):
                if available_seats:
                    chosen_seat = random.choice(available_seats)
                    st.session_state.assignments[chosen_seat] = name
                    st.session_state.current_members.remove(name)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 모바일용 5x4 격자
        st.markdown("<div class='mobile-hint'>", unsafe_allow_html=True)
        mobile_cols = st.columns(5)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = mobile_cols[idx % 5]
            if col_target.button(name, key=f"mo_{name}", use_container_width=True):
                if available_seats:
                    chosen_seat = random.choice(available_seats)
                    st.session_state.assignments[chosen_seat] = name
                    st.session_state.current_members.remove(name)
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("🎉 모든 팀원 배치가 완료되었습니다!")

# --- [2] 우측 도면 이미지 오버레이 패널 ---
with right_panel:
    st.markdown("<hr style='margin: 0.6rem 0;' class='mobile-hint'>", unsafe_allow_html=True)
    title_space, reset_space = st.columns([3, 1])
    title_space.markdown("<h3>🪑 실시간 배치도 (한눈에 보기)</h3>", unsafe_allow_html=True)
    
    with reset_space:
        if st.button("🔄 전체 리셋", key="reset", use_container_width=True):
            reset_all()
            st.rerun()

    image_path = "좌석배치.png"
    if os.path.exists(image_path):
        # 💡 HTML 렌더링 엔진 가동: 이미지 위에 절대좌표로 이름표 띄우기
        html_buffer = f"<div class='image-container'>"
        
        # 기본 배경 이미지 레이어
        # 배포 주소 및 로컬 환경에서 이미지를 인라인으로 동적 호출하기 위해 streamlit의 static 서빙 방식을 간접 이용하거나 
        # 간단히 로컬 이미지를 웹 브라우저가 그리도록 구성
        import base64
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()
        html_buffer += f"<img src='data:image/png;base64,{img_base64}' class='bg-image' alt='사무실 도면'>"
        
        # 배정된 이름들 실시간 오버레이 레이어
        for seat, user_name in st.session_state.assignments.items():
            if seat in SEAT_COORDINATES:
                pos = SEAT_COORDINATES[seat]
                class_type = "name-leader" if "팀장" in user_name else "name-member"
                
                # 각 알파벳 좌표값에 맞춰 div 뱃지를 생성
                html_buffer += f"""
                    <div class='floating-name {class_type}' style='top: {pos["top"]}; left: {pos["left"]};'>
                        {user_name}
                    </div>
                """
        html_buffer += "</div>"
        
        # 디자인된 HTML 컴포넌트를 브라우저에 주입
        st.markdown(html_buffer, unsafe_allow_html=True)
    else:
        st.error(f"🚨 폴더 내에서 '{image_path}' 파일을 찾을 수 없습니다. 이미지를 추가해 주세요.")