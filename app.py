import streamlit as st
import pandas as pd
import random
import os

# 1. 반응형 레이아웃 및 웹 접근성을 위한 기본 페이지 설정
st.set_page_config(
    page_title="팀 좌석 배치 에이전트 (PC/모바일 하이브리드)", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 미디어 쿼리를 활용한 대형 화면(PC)과 소형 화면(모바일) 맞춤형 CSS 주입
st.markdown("""
    <style>
    /* 기본 여백 조정 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    h1 { font-size: 1.6rem !important; margin-bottom: 0.1rem !important; text-align: center; }
    .sub-title-text { font-size: 0.8rem; color: #7F8C8D; text-align: center; margin-bottom: 0.8rem; }
    h3 { font-size: 1.1rem !important; margin-top: 0.4rem !important; margin-bottom: 0.3rem !important; }

    /* [기기별 최적화 스타일 분기] */
    
    /* PC 환경 스타일 (화면 폭 800px 이상) */
    @media (min-width: 800px) {
        .pc-hint { display: block; }
        .mobile-hint { display: none; }
        
        /* PC 명단 버튼 크기 및 폰트 */
        div.stButton > button {
            font-size: 0.9rem !important;
            padding: 8px 4px !important;
            min-height: 40px !important;
            border-radius: 5px !important;
        }
        
        /* PC 대화면 좌석 상자 크기 */
        .dynamic-seat-box {
            min-height: 68px !important;
            padding: 10px 4px !important;
        }
        .dynamic-seat-id { font-size: 11px !important; }
        .dynamic-seat-name { font-size: 13px !important; margin-top: 2px !important; }
        .dynamic-seat-empty { font-size: 11px !important; margin-top: 4px !important; }
        .corridor-space { padding: 20px 0 !important; font-size: 10px !important; }
    }
    
    /* 모바일 환경 스타일 (화면 폭 800px 미만) */
    @media (max-width: 799px) {
        .pc-hint { display: none; }
        .mobile-hint { display: block; }
        
        /* 모바일용 초소형 5x4 명단 단추 세팅 */
        div.stButton > button {
            font-size: 0.73rem !important;
            padding: 2px 1px !important;
            min-height: 28px !important;
            margin-bottom: 1px !important;
            border-radius: 3px !important;
        }
        
        /* 모바일 한눈에 보기를 위한 미니어처 좌석 상자 세팅 */
        .dynamic-seat-box {
            min-height: 46px !important;
            padding: 3px 1px !important;
            border-radius: 3px !important;
        }
        .dynamic-seat-id { font-size: 8px !important; }
        .dynamic-seat-name { font-size: 10px !important; font-weight: bold !important; margin-top: 1px !important; }
        .dynamic-seat-empty { font-size: 8.5px !important; color: #BDC3C7 !important; margin-top: 1px !important; }
        .corridor-space { padding: 11px 0 !important; font-size: 8px !important; }
    }

    /* 공통 디자인 베이스 */
    .dynamic-seat-box {
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        line-height: 1.1;
    }
    .reset-container button {
        font-size: 0.85rem !important;
        padding: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 및 초기화 구조 정의
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

# 오피스 도면 매트릭스 (G 기둥, 마지막 칸 W 고정)
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

# --- 레이아웃 드로잉 엔진 파트 ---
st.markdown("<h1>🖥️ 하이브리드 팀 좌석 배치 에이전트</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title-text'>접속 기기(PC/모바일)에 맞춰 최적의 화면 뷰로 자동 전환됩니다.</div>", unsafe_allow_html=True)

# 기기 환경에 맞춰 분기 배치하기 위해 Streamlit의 표준 columns 레이아웃 구성
# PC 뷰에서는 이 단락이 명단 패널이 되고, 모바일 뷰에서는 상단 스택 구조가 됩니다.
left_panel, right_panel = st.columns([1, 2.3])

# -------------------------------------------------------------
# [1] 팀 명단 처리 파트
# -------------------------------------------------------------
with left_panel:
    st.markdown("<h3>👥 팀 명단</h3>", unsafe_allow_html=True)
    
    if st.session_state.current_members:
        # --- PC 브라우저용 2x9 격자 배열 생성 ---
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
        
        # --- 모바일 스마트폰용 5x4 격자 배열 생성 ---
        st.markdown("<div class='mobile-hint'>", unsafe_allow_html=True)
        mobile_cols = st.columns(5) # 가로 5열 설정으로 슬림하게 배치
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

# -------------------------------------------------------------
# [2] 오피스 좌석 배치도 처리 파트
# -------------------------------------------------------------
with right_panel:
    st.markdown("<hr style='margin: 0.6rem 0;' class='mobile-hint'>", unsafe_allow_html=True)
    
    title_space, reset_space = st.columns([3.5, 1])
    title_space.markdown("<h3>🪑 좌석 배치 현황</h3>", unsafe_allow_html=True)
    
    with reset_space:
        st.markdown("<div class='reset-container'>", unsafe_allow_html=True)
        if st.button("🔄 전체 리셋", key="global_reset", use_container_width=True):
            reset_all()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 7열 반응형 그리드 맵핑 (좌측 고정 창가 + 우측 오피스 7열 구조)
    grid_cols = st.columns([0.42] + [1]*7)
    window_chars = ["W", "I", "N", "D", "O", "W"]
    
    for r_idx, row in enumerate(seat_structure):
        # 0열: 고정 세로형 창가 라벨 배치 (미디어 쿼리에 따른 컴팩트 패딩 적용)
        if r_idx in [0, 2, 3, 5]:
            w_idx = [0, 2, 3, 5].index(r_idx)
            grid_cols[0].markdown(
                f"<div class='corridor-space' style='background-color:#E0F7FA; color:#006064; text-align:center; "
                f"font-weight:bold; border:1px solid #006064; border-radius:4px; padding:20px 0; font-size:10px;'>{window_chars[w_idx]}</div>", 
                unsafe_allow_html=True
            )
        else:
            grid_cols[0].write("")

        # 1~7열: 실시간 인공지능 좌석 매칭 시스템 빌드
        for c_idx, val in enumerate(row):
            target_col = grid_cols[c_idx + 1]
            
            if val == "기둥":
                target_col.markdown(
                    "<div class='dynamic-seat-box' style='background-color:#2C3E50; color:#FFFFFF; "
                    "border:1px solid #1A252F; font-weight:bold; font-size:11px;'>기둥</div>", 
                    unsafe_allow_html=True
                )
            elif val != "":
                # 배정 완료 시 하이라이트 배색 서식 스위칭
                if val in st.session_state.assignments:
                    assigned_name = st.session_state.assignments[val]
                    bg_color = "#FFF3E0" if "팀장" in assigned_name else "#E8F5E9"
                    font_color = "#D84315" if "팀장" in assigned_name else "#2E7D32"
                    border_color = "#E65100" if "팀장" in assigned_name else "#1B5E20"
                    
                    target_col.markdown(
                        f"<div class='dynamic-seat-box' style='background-color:{bg_color}; color:{font_color}; "
                        f"border:1.5px solid {border_color};'>"
                        f"<span class='dynamic-seat-id'>{val}</span>"
                        f"<span class='dynamic-seat-name'>{assigned_name}</span></div>", 
                        unsafe_allow_html=True
                    )
                # 공석 빈자리 서식 스위칭
                else:
                    target_col.markdown(
                        f"<div class='dynamic-seat-box' style='background-color:#FFFFFF; color:#7F8C8D; "
                        f"border:1px solid #BDC3C7;'> "
                        f"<span class='dynamic-seat-id'>{val}</span>"
                        f"<span class='dynamic-seat-empty'>빈자리</span></div>", 
                        unsafe_allow_html=True
                    )
            else:
                # 통로 공간 수평 격리 기호 처리
                if r_idx in [1, 4]:
                    target_col.markdown("<div class='corridor-space' style='text-align:center; color:#E0E0E0; font-size:10px; padding:20px 0;'>━</div>", unsafe_allow_html=True)
                else:
                    target_col.write("")