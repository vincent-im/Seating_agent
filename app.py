import streamlit as st
import pandas as pd
import random
import os

# 1. 기본 화면 설정 및 가로폭 최대화
st.set_page_config(
    page_title="Security솔루션팀 좌석 배치 앱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 하나의 레이아웃 내부에서 PC(좌우) / 모바일(상하 + 명단 수평 4열)을 구현하는 핵심 CSS
st.markdown("""
    <style>
    /* 상단 타이틀 메뉴 바 잘림 방지 및 기본 여백 최적화 */
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

    /* 💻 [PC 환경 전용 스타일: 너비 800px 이상] -> 좌우 레이아웃 최적화 */
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

    /* 📱 [모바일폰 환경 전용 스타일: 너비 799px 이하] -> 상하 레이아웃 및 4열 강제 고정 */
    @media (max-width: 799px) {
        /* 1. Streamlit의 좌우 컬럼 분할을 강제로 상하 적층(수직) 구도로 전환 */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 1.5rem !important;
        }
        
        /* 2. 명단 버튼들이 포함된 첫 번째 블록(명단 컨테이너)을 가로 수평 4열 격자로 강제 유지 */
        [data-testid="stHorizontalBlock"] > div:first-child [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 6px !important;
        }
        /* 개별 명단 버튼이 모바일에서 가로폭의 정확히 1/4(25%)씩 차지하도록 칼같이 고정 */
        [data-testid="stHorizontalBlock"] > div:first-child [data-testid="stHorizontalBlock"] > div {
            flex: 0 0 calc(25% - 5px) !important;
            min-width: calc(25% - 5px) !important;
            max-width: calc(25% - 5px) !important;
            padding: 0 !important;
        }
        
        /* 모바일용 버튼 콤팩트화 */
        div.stButton > button {
            font-size: 0.75rem !important;
            padding: 4px 2px !important;
            min-height: 32px !important;
            border-radius: 4px !important;
        }
        
        /* 하단 배치도 공간을 위한 10% 이상 상하 압축 */
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

# 3. 데이터 로드 함수 (명단.xlsx 지원)
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

# 4. 좌석배치.xlsx 구조 분석 함수
def load_excel_layout():
    file_name = "좌석배치.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, header=None)
            df = df.fillna("")
            df = df.map(lambda x: str(x).strip()) if hasattr(df, 'map') else df.applymap(lambda x: str(x).strip())
            
            seats = []
            for row in df.values:
                for val in row:
                    if val != "":
                        seats.append(val)
            return df, seats
        except Exception as e:
            st.error(f"좌석배치.xlsx 파싱 오류: {e}")
            
    backup_data = [
        ["A", "B", "C", "", "D", "E", "F"],
        ["", "", "", "", "", "", ""],         
        ["", "G", "H", "", "I", "J", "K"],
        ["L", "M", "N", "", "O", "P", "Q"],
        ["", "", "", "", "", "", ""],         
        ["R", "S", "T", "", "U", "V", "W"]
    ]
    return pd.DataFrame(backup_data), ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W"]

# 5. 세션 관리 및 데이터 초기 마운트
layout_df, available_seats_list = load_excel_layout()

if 'members' not in st.session_state:
    st.session_state.members = load_initial_members()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
if 'available_seats' not in st.session_state:
    st.session_state.available_seats = available_seats_list.copy()

def assign_seat(name):
    if st.session_state.available_seats:
        chosen_seat = random.choice(st.session_state.available_seats)
        st.session_state.available_seats.remove(chosen_seat)
        st.session_state.assignments[chosen_seat] = name
        st.session_state.members.remove(name)
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
    if st.button("🔄 초기화", key="reset_btn", use_container_width=True):
        reset_program()

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# 단일 통합 레이아웃 가동 (PC: 좌우 자동 / 모바일: 상하 자동 전환)
# ------------------------------------------------------------------
# left_col과 right_col이 PC에서는 1:2.5 비율의 좌우 배치로 서빙되며,
# 모바일 브라우저로 진입하는 순간 CSS 미디어 쿼리가 이를 감지하여 유연하게 상하(수직)로 재정렬시킵니다.
left_col, right_col = st.columns([1, 2.5])

# [명단 영역]
with left_col:
    st.markdown("<div class='section-title'>👥 명단</div>", unsafe_allow_html=True)
    if st.session_state.members:
        # 가로 4열 구조로 버튼을 그립니다.
        # PC(넓은 화면): 좌측폭이 좁아 가로로 나열되다 2열씩 이쁘게 줄바꿈되어 2X9에 가깝게 정착합니다.
        # 모바일(좁은 화면): 아래 주입된 Flex CSS에 의해 꺾이지 않고 가로 수평 4열(4X5 격자)을 칼같이 고정 유지합니다.
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
            elif cell_value == "":
                html_table += "<td class='empty-space'></td>"
            else:
                assigned_user = st.session_state.assignments.get(cell_value, None)
                html_table += "<td>"
                if assigned_user:
                    style_class = "name-leader" if "팀장" in assigned_user else "name-member"
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