import streamlit as st
import pandas as pd
import random
import os

# 웹 페이지 기본 설정
st.set_page_config(page_title="팀 좌석 랜덤 배치 에이전트", layout="wide")

# 1. 파일 검증 및 데이터 로드 함수 정의
def check_pptx_file():
    if not os.path.exists("좌석배치.pptx"):
        st.sidebar.warning("⚠️ '좌석배치.pptx' 파일이 폴더 내에 없습니다. 참조용 파일을 넣어주세요.")

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
        st.sidebar.info("💡 '명단.xlsx'가 없어 임시 명단(18명)을 생성합니다.")
        return [f"홍길동{i}" for i in range(1, 19)]

# 2. 웹 세션 상태(상태 유지) 초기화
check_pptx_file()
if 'original_members' not in st.session_state:
    st.session_state.original_members = load_member_list()
if 'current_members' not in st.session_state:
    st.session_state.current_members = st.session_state.original_members.copy()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}  # {좌석알파벳: 이름}

# 고정된 오피스 레이아웃 구조 정의 (G는 기둥, 마지막 칸은 W)
seat_structure = [
    ["A", "B", "C", "", "D", "E", "F"],
    ["", "", "", "", "", "", ""],
    ["기둥", "G", "H", "", "I", "J", "K"], 
    ["L", "M", "N", "", "O", "P", "Q"],   
    ["", "", "", "", "", "", ""],
    ["R", "S", "T", "", "U", "V", "W"]
]

# 배치 가능한 전체 좌석 풀(Pool) 생성
all_valid_seats = [cell for row in seat_structure for cell in row if cell and cell != "기둥"]
assigned_seats = list(st.session_state.assignments.keys())
available_seats = [s for s in all_valid_seats if s not in assigned_seats]

# 초기화 로직 함수
def reset_all():
    st.session_state.current_members = st.session_state.original_members.copy()
    st.session_state.assignments = {}

# 3. 웹 화면 UI 레이아웃 구성
st.title("🖥️ 오피스 좌석 랜덤 배치 웹 에이전트")
st.markdown("---")

# 좌우 레이아웃 분할 (좌측 30%: 명단, 우측 70%: 좌석 배치도)
left_col, right_col = st.columns([1, 2.5])

# --- 좌측 영역: 팀 명단 패널 ---
with left_col:
    st.subheader("👥 팀 명단")
    st.caption("이름을 클릭하면 우측 자리에 무작위 배정됩니다.")
    
    # 2열 격자 구조로 이름 버튼 배치
    if st.session_state.current_members:
        btn_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.current_members):
            col_target = btn_cols[idx % 2]
            # 버튼 클릭 시 즉시 좌석 매칭 및 리스트 제외 처리
            if col_target.button(name, key=f"btn_{name}", use_container_width=True):
                if available_seats:
                    chosen_seat = random.choice(available_seats)
                    st.session_state.assignments[chosen_seat] = name
                    st.session_state.current_members.remove(name)
                    st.rerun()  # 화면 즉시 갱신
                else:
                    st.error("모든 좌석이 만석입니다!")
    else:
        st.success("🎉 모든 팀원의 좌석 배치가 완료되었습니다!")

# --- 우측 영역: 오피스 좌석 배치도 패널 ---
with right_col:
    # 헤더와 초기화 버튼 정렬
    title_sub, btn_sub = st.columns([4, 1])
    title_sub.subheader("🪑 좌석 배치 현황")
    if btn_sub.button("🔄 전체 초기화", type="secondary", use_container_width=True):
        reset_all()
        st.rerun()
        
    st.write("") # 공백용

    # 윈도우 창가 표시 + 7열 오피스 그리드 배치
    grid_cols = st.columns([0.6] + [1]*7)
    
    # 창가 라벨 세로 배치
    window_chars = ["W", "I", "N", "D", "O", "W"]
    
    for r_idx, row in enumerate(seat_structure):
        # 0번 열: 창가 라벨 (통로 행을 제외하고 배치)
        if r_idx in [0, 2, 3, 5]:
            w_idx = [0, 2, 3, 5].index(r_idx)
            grid_cols[0].markdown(
                f"<div style='background-color:#E0F7FA; color:#006064; text-align:center; "
                f"padding:20px 0; font-weight:bold; border:1px solid #006064; border-radius:5px;'>{window_chars[w_idx]}</div>", 
                unsafe_allow_html=True
            )
        else:
            grid_cols[0].write("") # 통로 행 공백 처리

        # 1~7번 열: 실제 좌석 데이터 매핑
        for c_idx, val in enumerate(row):
            target_col = grid_cols[c_idx + 1]
            
            if val == "기둥":
                # 검정색 box 형태의 기둥 UI 디자인
                target_col.markdown(
                    "<div style='background-color:#2C3E50; color:#FFFFFF; text-align:center; "
                    "padding:20px 0; font-weight:bold; border-radius:5px; border:1px solid #1A252F;'>기 둥</div>", 
                    unsafe_allow_html=True
                )
            elif val != "":
                # 주인이 있는 자리와 빈 자리 스타일 다르게 적용
                if val in st.session_state.assignments:
                    assigned_name = st.session_state.assignments[val]
                    bg_color = "#FFF3E0" if "팀장" in assigned_name else "#E8F5E9"
                    font_color = "#E65100" if "팀장" in assigned_name else "#2E7D32"
                    
                    target_col.markdown(
                        f"<div style='background-color:{bg_color}; color:{font_color}; text-align:center; "
                        f"padding:10px 0; border:2px solid {font_color}; border-radius:5px; min-height:68px;'>"
                        f"<span style='font-size:11px; color:#95A5A6;'>{val}</span><br><b>{assigned_name}</b></div>", 
                        unsafe_allow_html=True
                    )
                else:
                    target_col.markdown(
                        f"<div style='background-color:#FFFFFF; color:#BDC3C7; text-align:center; "
                        f"padding:10px 0; border:1px solid #BDC3C7; border-radius:5px; min-height:68px;'>"
                        f"<span style='font-size:11px; color:#95A5A6;'>{val}</span><br><span style='font-size:13px;'>빈 자리</span></div>", 
                        unsafe_allow_html=True
                    )
            else:
                # 데이터가 없는 공백(복도 및 통로) 처리
                if r_idx in [1, 4]:
                    target_col.markdown("<div style='text-align:center; color:#BDC3C7; font-size:11px; padding:20px 0;'>━━━━</div>", unsafe_allow_html=True)
                else:
                    target_col.write("")