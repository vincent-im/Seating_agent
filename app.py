import streamlit as st
import pandas as pd
import random
import os

# 1. 반응형 및 모바일 접근성을 위한 기본 페이지 설정
st.set_page_config(
    page_title="팀 좌석 랜덤 배치 에이전트 (모바일 지원)", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 인라인 CSS 주입: 모바일 스크롤 및 웹 접근성(시각 대비, 터치 영역) 향상
st.markdown("""
    <style>
    /* 기본 글꼴 세팅 및 터치 타겟 최소 크기 확보 */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    }
    
    /* 모바일 환경에서 스크롤 부드럽게 설정 및 패딩 최적화 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* 웹 접근성: 고대비 및 가독성을 위한 컴포넌트 커스텀 정의 */
    .seat-box {
        text-align: center;
        padding: 12px 6px;
        border-radius: 6px;
        min-height: 75px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# 2. 파일 검증 및 데이터 로드 함수
def check_pptx_file():
    if not os.path.exists("좌석배치.pptx"):
        st.sidebar.warning("⚠️ '좌석배치.pptx' 파일이 폴더 내에 없습니다.")

def load_member_list():
    file_name = "명단.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name)
            names = df.iloc[:, 0].dropna().astype(str).tolist()
            return [name.strip() for name in names if name.strip()]
        except Exception as e:
            st.sidebar.error(f"명단 로드 실패: {e}")
            return [f"팀원{i}" for i in range(1, 19)]
    else:
        return [f"홍길동{i}" for i in range(1, 19)]

# 3. 웹 세션 상태 초기화
check_pptx_file()
if 'original_members' not in st.session_state:
    st.session_state.original_members = load_member_list()
if 'current_members' not in st.session_state:
    st.session_state.current_members = st.session_state.original_members.copy()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}

# 고정된 오피스 레이아웃 구조 (G는 기둥, 마지막 칸은 W)
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

# 4. 웹 화면 레이아웃 구성
st.title("🖥️ 오피스 좌석 랜덤 배치 에이전트")
st.markdown("Accessible & Mobile-friendly Web App")
st.markdown("---")

# 반응형 분할: 대화면(PC)에서는 좌우 구조, 소화면(모바일)에서는 자동으로 위아래 구조로 재배치됨
left_col, right_col = st.columns([1, 2.3])

# --- 좌측 영역: 팀 명단 패널 (모바일 접속 시 상단에 노출됨) ---
with left_col:
    st.subheader("👥 팀 명단")
    st.markdown("<p style='color:#555555; font-size:14px;'>배치할 팀원의 이름을 터치/클릭하세요.</p>", unsafe_allow_html=True)
    
    if st.session_state.current_members:
        # 모바일 가로폭을 고려하여 스마트폰 화면에서도 깨지지 않게 2열 단추 레이아웃 고정
        btn_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = btn_cols[idx % 2]
            
            # 모바일 접근성: 버튼 터치 타겟(너비 가득 채움) 확장형 적용
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

# --- 우측 영역: 오피스 좌석 배치도 패널 (모바일 접속 시 하단에 노출됨) ---
with right_col:
    st.markdown("<br class='mobile-break' style='display:none;'>", unsafe_allow_html=True) # 모바일용 여백
    
    # 상단 타이틀 및 초기화 버튼 배치
    title_sub, btn_sub = st.columns([3, 1.2])
    title_sub.subheader("🪑 좌석 배치 현황")
    
    # 모바일 접근성: 리셋 버튼의 크기와 폰트를 키워 조작 편의성 증대
    if btn_sub.button("🔄 전체 초기화", type="secondary", use_container_width=True):
        reset_all()
        st.rerun()
        
    st.write("") 

    # 7열 오피스 레이아웃 그리드 구성 (모바일 화면 비율 최적화를 위해 폭 비율 조정)
    grid_cols = st.columns([0.5] + [1]*7)
    window_chars = ["W", "I", "N", "D", "O", "W"]
    
    for r_idx, row in enumerate(seat_structure):
        # 0번 열: 창가 라벨 (시각 보조용 배경색 매핑)
        if r_idx in [0, 2, 3, 5]:
            w_idx = [0, 2, 3, 5].index(r_idx)
            grid_cols[0].markdown(
                f"<div style='background-color:#E0F7FA; color:#006064; text-align:center; "
                f"padding:22px 0; font-weight:bold; border:1px solid #006064; border-radius:5px; font-size:12px;'>{window_chars[w_idx]}</div>", 
                unsafe_allow_html=True
            )
        else:
            grid_cols[0].write("")

        # 1~7번 열: 동적 좌석 드로잉
        for c_idx, val in enumerate(row):
            target_col = grid_cols[c_idx + 1]
            
            if val == "기둥":
                # 웹 접근성: 배경과 텍스트의 고대비(#2C3E50 vs #FFFFFF) 적용 및 스크린 리더 인식 고려
                target_col.markdown(
                    "<div class='seat-box' style='background-color:#2C3E50; color:#FFFFFF; "
                    "border:1px solid #1A252F; font-weight:bold; font-size:13px;' role='img' aria-label='기둥 공백 지역'>기 둥</div>", 
                    unsafe_allow_html=True
                )
            elif val != "":
                # 주인이 결정된 좌석 브랜딩
                if val in st.session_state.assignments:
                    assigned_name = st.session_state.assignments[val]
                    # 고대비 배색 설정: 팀장은 짙은 오렌지, 팀원은 짙은 초록색으로 시인성 개선
                    bg_color = "#FFF3E0" if "팀장" in assigned_name else "#E8F5E9"
                    font_color = "#D84315" if "팀장" in assigned_name else "#2E7D32"
                    border_color = "#E65100" if "팀장" in assigned_name else "#1B5E20"
                    
                    target_col.markdown(
                        f"<div class='seat-box' style='background-color:{bg_color}; color:{font_color}; "
                        f"border:2px solid {border_color}; font-size:14px;' role='text' aria-label='{val}번 좌석 배정 완료 {assigned_name}'>"
                        f"<span style='font-size:10px; color:#7F8C8D;'>{val}</span>"
                        f"<span style='margin-top:2px;'><b>{assigned_name}</b></span></div>", 
                        unsafe_allow_html=True
                    )
                # 아직 비어있는 빈 자리 브랜딩
                else:
                    target_col.markdown(
                        f"<div class='seat-box' style='background-color:#FFFFFF; color:#7F8C8D; "
                        f"border:1px solid #BDC3C7; font-size:13px;' role='text' aria-label='{val}번 빈 좌석'>"
                        f"<span style='font-size:10px; color:#95A5A6;'>{val}</span>"
                        f"<span style='margin-top:4px; color:#BDC3C7;'>빈자리</span></div>", 
                        unsafe_allow_html=True
                    )
            else:
                # 복도 분리선 가시성 패딩 적용
                if r_idx in [1, 4]:
                    target_col.markdown("<div style='text-align:center; color:#E0E0E0; font-size:10px; padding:22px 0;'>━</div>", unsafe_allow_html=True)
                else:
                    target_col.write("")