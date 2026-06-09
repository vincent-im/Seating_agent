import streamlit as st
import pandas as pd
import random
import os

# 1. 화면 최적화 및 레이아웃 기본 설정
st.set_page_config(
    page_title="Security솔루션팀 좌석 배치 앱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 엑셀 도면 서식(통로/X 마킹 검은색 박스)을 완벽히 구현하는 CSS 주입
st.markdown("""
    <style>
    /* 상단 메뉴바 잘림 방지 및 전체 레이아웃 패딩 최적화 */
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* 섹션 타이틀 공통 서식 */
    .section-title { 
        font-size: 1.25rem !important; 
        font-weight: bold; 
        margin-bottom: 0.8rem !important; 
        color: #2C3E50; 
    }
    
    /* 대기 명단 개별 네모 박스 공통 서식 */
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

    /* 리셔플링 및 초기화 특수 버튼 스타일 지정 */
    .custom-control-btn button {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        color: #1E293B !important;
    }
    .custom-control-btn button:hover {
        background-color: #E2E8F0 !important;
        border-color: #94A3B8 !important;
    }

    /* 💻 [PC 환경 전용 스타일: 너비 800px 이상] */
    @media (min-width: 800px) {
        div.stButton > button {
            font-size: 0.95rem !important;
            padding: 8px 5px !important;
            min-height: 40px !important;
            border-radius: 6px !important;
        }
        .seat-table { border-spacing: 12px; }
        .seat-table td { height: 80px; }
        .empty-row-space { height: 35px !important; }
        .name-badge { font-size: 13px !important; padding: 5px 10px !important; }
    }

    /* 📱 [모바일폰 환경 전용 스타일: 너비 799px 이하] */
    @media (max-width: 799px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 1.5rem !important;
        }
        [data-testid="stHorizontalBlock"] > div:first-child [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 6px !important;
        }
        [data-testid="stHorizontalBlock"] > div:first-child [data-testid="stHorizontalBlock"] > div {
            flex: 0 0 calc(25% - 5px) !important;
            min-width: calc(25% - 5px) !important;
            max-width: calc(25% - 5px) !important;
            padding: 0 !important;
        }
        div.stButton > button {
            font-size: 0.75rem !important;
            padding: 4px 2px !important;
            min-height: 32px !important;
            border-radius: 4px !important;
        }
        .seat-table { border-spacing: 6px !important; }
        .seat-table td { height: 55px !important; border-radius: 5px !important; }
        .empty-row-space { height: 18px !important; }
        .name-badge { font-size: 9.5px !important; padding: 2px 4px !important; }
        .seat-label { font-size: 8px !important; margin-top: 1px !important; }
        .unassigned-text { font-size: 0.85rem !important; }
    }

    /* 엑셀 구조 렌더링용 테이블 디자인 기본 서식 */
    .seat-table {
        width: 100%;
        border-collapse: separate;
        table-layout: fixed;
    }
    .seat-table td {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        text-align: center;
        vertical-align: middle;
        font-weight: bold;
        position: relative;
        background-color: #F8F9FA;
    }
    
    /* 엑셀 내 X 표시 셀 전용 서식 (테두리가 있는 선명한 검은색 박스) */
    .black-pillar-space {
        border: 1px solid #475569 !important;
        background-color: #1E293B !important;
        border-radius: 8px;
    }
    
    /* 테두리가 아예 없는 투명한 가로/세로 통로 영역 */
    .empty-row-space { border: none !important; background-color: transparent !important; }
    .empty-space { border: none !important; background-color: transparent !important; }
    
    .seat-slot-assigned {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 6px;
        padding: 2px;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05);
    }
    
    .name-badge {
        font-weight: bold !important;
        border-radius: 4px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        display: inline-block;
        white-space: nowrap;
    }
    .name-leader { background-color: #FFEB3B !important; color: #E65100 !important; border: 1.5px solid #E65100 !important; }
    .name-member { background-color: #2ECC71 !important; color: #FFFFFF !important; border: 1px solid #27AE60 !important; }
    
    .seat-label {
        font-size: 10px;
        color: #A0A0A0;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수 (명단.xlsx의 모든 형태 완벽 동기화 파싱)
def load_initial_members():
    file_name = "명단.xlsx"
    if os.path.exists(file_name):
        try:
            # 첫 번째 행이 헤더로 유실되는 것을 막기 위해 header=None으로 먼저 읽거나 처리
            df = pd.read_excel(file_name, header=None)
            names = []
            for col in df.columns:
                names.extend(df[col].dropna().astype(str).tolist())
            
            cleaned_names = [n.strip() for n in names if n.strip() and n.strip() != "nan"]
            
            # '김광녕' 유실 방지 검증: 만약 엑셀을 읽었는데 '김광녕'이 없다면 강제로 최상단에 추가
            if "김광녕" not in cleaned_names:
                cleaned_names.insert(0, "김광녕")
                
            return cleaned_names
        except:
            pass
            
    # 백업 리스트 보정
    return ["김광녕", "김형정", "김홍석", "남광봉", "박명식", "설동민", "원상호", "유정욱", "이병동", 
            "이홍범", "임정빈", "정성영", "정현철", "조관진", "최주용", "한승엽", "홍성화", "이명주"]

# 4. 좌석배치.xlsx 파일 분석 엔진 (A~S 가용 좌석만 추출)
def load_excel_layout():
    valid_seat_letters = [chr(i) for i in range(65, 84)] # 오직 A부터 S까지만 허용 (총 19개)
    file_name = "좌석배치.xlsx"
    
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, header=None)
            df = df.fillna("")
            df = df.map(lambda x: str(x).strip()) if hasattr(df, 'map') else df.applymap(lambda x: str(x).strip())
            
            seats = []
            for row in df.values:
                for val in row:
                    if val in valid_seat_letters:
                        seats.append(val)
            return df, seats
        except Exception as e:
            st.error(f"좌석배치.xlsx 파싱 오류: {e}")
            
    # 백업 도면 사양
    backup_data = [
        ["A", "B", "C", "", "D", "E", "X"],
        ["", "", "", "", "", "", ""],         
        ["X", "F", "G", "", "H", "I", "X"],
        ["J", "K", "L", "", "M", "N", "X"],
        ["", "", "", "", "", "", ""],         
        ["O", "P", "Q", "", "R", "S", "X"]
    ]
    backup_seats = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S"]
    return pd.DataFrame(backup_data), backup_seats

# 5. 세션 관리 및 데이터 초기 마운트
layout_df, available_seats_list = load_excel_layout()

# 엑셀 파일이 수정되었을 때 세션이 구버전 데이터를 쥐고 있는 문제를 해결하기 위해
# '전체 초기화'를 하지 않더라도 강제로 초기 로드 리스트에 반영되도록 로직 보완
initial_members_list = load_initial_members()

if 'members' not in st.session_state:
    st.session_state.members = initial_members_list.copy()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
if 'available_seats' not in st.session_state:
    st.session_state.available_seats = available_seats_list.copy()

# 혹시 세션 상태에 '김광녕'이 누락되어 있다면 강제로 주입 (세션 브레이커 방어 코드)
if st.session_state.members and "김광녕" not in st.session_state.members and not any("김광녕" in k or v == "김광녕" for k, v in st.session_state.assignments.items()):
    st.session_state.members.insert(0, "김광녕")

def assign_seat(name):
    if st.session_state.available_seats:
        chosen_seat = random.choice(st.session_state.available_seats)
        st.session_state.available_seats.remove(chosen_seat)
        st.session_state.assignments[chosen_seat] = name
        st.session_state.members.remove(name)
        st.rerun()

# 명단 순서를 무작위로 뒤섞는 리셔플링 함수
def shuffle_members():
    random.shuffle(st.session_state.members)
    st.rerun()

def reset_program():
    _, fresh_seats = load_excel_layout()
    st.session_state.members = load_initial_members()
    st.session_state.assignments = {}
    st.session_state.available_seats = fresh_seats
    st.rerun()

# ------------------------------------------------------------------
# 상단 글로벌 제어바 헤더
# ------------------------------------------------------------------
title_col, btn_col = st.columns([4, 1])
title_col.subheader("🖥️ Security솔루션팀 좌석 배치 앱")
with btn_col:
    if st.button("🔄 전체 초기화", key="reset_btn", use_container_width=True):
        reset_program()

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 단일 통합 레이아웃 가동 (PC: 좌우 자동 / 모바일: 상하 자동 전환)
# ------------------------------------------------------------------
left_col, right_col = st.columns([1, 2.5])

# [명단 영역]
with left_col:
    st.markdown("<div class='section-title'>👥 명단</div>", unsafe_allow_html=True)
    
    if st.session_state.members:
        st.markdown("<div class='custom-control-btn'>", unsafe_allow_html=True)
        if st.button("🔄 명단 리셔플링", key="shuffle_btn", use_container_width=True):
            shuffle_members()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
        
        grid_cols = st.columns(4)
        for idx, name in enumerate(st.session_state.members):
            col_target = grid_cols[idx % 4]
            if col_target.button(name, key=f"member_{name}_{idx}", use_container_width=True):
                assign_seat(name)
    else:
        st.success("모든 배정이 완료되었습니다!")

# [좌석 별 배치 영역]
with right_col:
    st.markdown("<div class='section-title'>🪑 좌석 별 배치</div>", unsafe_allow_html=True)
    
    html_table = "<table class='seat-table'>"
    
    for r_idx, row in layout_df.iterrows():
        is_empty_row = all(cell_value == "" for cell_value in row)
        
        html_table += "<tr>"
        for c_idx, cell_value in enumerate(row):
            if is_empty_row:
                html_table += f"<td class='empty-row-space' colspan='{len(row)}'></td>"
                break
            elif cell_value == "X":
                html_table += "<td class='black-pillar-space'></td>"
            elif cell_value == "":
                html_table += "<td class='empty-space'></td>"
            else:
                assigned_user = st.session_state.assignments.get(cell_value, None)
                html_table += "<td>"
                if assigned_user:
                    # '김광녕'인 경우 노란색 강조 스타일(name-leader) 지정
                    style_class = "name-leader" if "김광녕" in assigned_user else "name-member"
                    html_table += f"""
                    <div class='seat-slot-assigned'>
                        <span class='name-badge {style_class}'>{assigned_user}</span>
                        <span class='seat-label'>좌석 {cell_value}</span>
                    </div>
                    """
                else:
                    html_table += f"<span class='unassigned-text' style='color: #BCBCBC;'>{cell_value}</span>"
                html_table += "</td>"
        html_table += "</tr>"
    html_table += "</table>"
    
    st.markdown(html_table, unsafe_allow_html=True)
