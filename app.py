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

# 2. PC 및 모바일(가로 4열) 환경에 모두 대응하는 고도화된 CSS 주입
st.markdown("""
    <style>
    /* 상단 여백 조절 및 전체 레이아웃 패딩 최적화 */
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* 섹션 타이틀 서식 */
    .section-title { 
        font-size: 1.25rem !important; 
        font-weight: bold; 
        margin-bottom: 0.8rem !important; 
        color: #2C3E50; 
    }
    
    /* 💡 대기 명단 네모 박스 공통 스타일 */
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

    /* 💻 [PC 환경 전용 스타일: 너비 800px 이상] */
    @media (min-width: 800px) {
        .pc-layout { display: block; }
        .mobile-layout { display: none; }
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

    /* 📱 [모바일 환경 전용 스타일: 너비 799px 이하] */
    @media (max-width: 799px) {
        .pc-layout { display: none; }
        .mobile-layout { display: block; }
        
        /* 모바일 상단 공간 절약을 위한 명단 단추 초소형화 */
        div.stButton > button {
            font-size: 0.75rem !important;
            padding: 4px 2px !important;
            min-height: 32px !important;
            border-radius: 4px !important;
        }
        
        /* 하단 배치도 공간 확보를 위한 표 간격 압축 (10% 이상 추가 축소) */
        .seat-table { border-spacing: 6px !important; }
        .seat-table td { height: 55px !important; border-radius: 5px !important; }
        .empty-row-space { height: 18px !important; }
        .name-badge { font-size: 9.5px !important; padding: 2px 4px !important; }
        .seat-label { font-size: 8px !important; margin-top: 1px !important; }
        .unassigned-text { font-size: 0.85rem !important; }
    }

    /* 엑셀 스타일 좌석 테이블 디자인 */
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
    
    /* 세로 공백 행(완전 빈 행)을 위한 전용 스타일 */
    .empty-row-space {
        border: none !important;
        background-color: transparent !important;
    }
    
    /* 개별 가로 빈 칸 (통로, 기둥 등) 처리 */
    .empty-space {
        border: none !important;
        background-color: transparent !important;
    }
    
    /* 실제 배정된 좌석 슬롯의 스타일 */
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
    
    /* 이름표 뱃지 서식 및 배색 */
    .name-badge {
        font-weight: bold !important;
        border-radius: 4px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        display: inline-block;
        white-space: nowrap;
    }
    .name-leader { background-color: #FFEB3B !important; color: #E65100 !important; border: 1.5px solid #E65100 !important; }
    .name-member { background-color: #2ECC71 !important; color: #FFFFFF !important; border: 1px solid #27AE60 !important; }
    
    /* 슬롯 안의 원래 좌석 문자 투명도 조절 */
    .seat-label {
        font-size: 10px;
        color: #A0A0A0;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터 로드 함수 (명단.xlsx)
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

# 4. 좌석배치.xlsx 파일에서 구조(세로 공백 포함)를 가져오는 함수
def load_excel_layout():
    file_name = "좌석배치.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, header=None)
            df = df.fillna("")
            
            if hasattr(df, 'map'):
                df = df.map(lambda x: str(x).strip())
            else:
                df = df.applymap(lambda x: str(x).strip())
            
            seats = []
            for row in df.values:
                for val in row:
                    if val != "":
                        seats.append(val)
            return df, seats
        except Exception as e:
            st.error(f"좌석배치.xlsx 파싱 오류: {e}")
            
    # 파일이 없을 경우 작동할 기본 백업 레이아웃
    backup_data = [
        ["A", "B", "C", "", "D", "E", "F"],
        ["", "", "", "", "", "", ""],         
        ["", "G", "H", "", "I", "J", "K"],
        ["L", "M", "N", "", "O", "P", "Q"],
        ["", "", "", "", "", "", ""],         
        ["R", "S", "T", "", "U", "V", "W"]
    ]
    df_backup = pd.DataFrame(backup_data)
    seats_backup = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W"]
    return df_backup, seats_backup

# 5. 프로그램 초기 세션 및 레이아웃 데이터 로드
layout_df, available_seats_list = load_excel_layout()

if 'members' not in st.session_state:
    st.session_state.members = load_initial_members()
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}
if 'available_seats' not in st.session_state:
    st.session_state.available_seats = available_seats_list.copy()

# 6. 공통 배정 처리 함수
def assign_seat(name):
    if st.session_state.available_seats:
        chosen_seat = random.choice(st.session_state.available_seats)
        st.session_state.available_seats.remove(chosen_seat)
        st.session_state.assignments[chosen_seat] = name
        st.session_state.members.remove(name)
        st.rerun()

# 7. 리셋 로직
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
# 공통 테이블 빌더 (HTML 문자열 생성)
# ------------------------------------------------------------------
def build_html_table():
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
    return html_table


# ------------------------------------------------------------------
# [1] PC 브라우저용 레이아웃 (좌측 명단 2X9, 우측 좌석 표)
# ------------------------------------------------------------------
st.markdown("<div class='pc-layout'>", unsafe_allow_html=True)
pc_left, pc_right = st.columns([1, 2.5])

with pc_left:
    st.markdown("<div class='section-title'>👥 명단</div>", unsafe_allow_html=True)
    if st.session_state.members:
        pc_grid_cols = st.columns(2) # 💡 PC 가로 2열 배열
        for idx, name in enumerate(st.session_state.members):
            col_target = pc_grid_cols[idx % 2]
            if col_target.button(name, key=f"pc_member_{name}_{idx}", use_container_width=True):
                assign_seat(name)
    else:
        st.success("모든 배정이 완료되었습니다!")

with pc_right:
    st.markdown("<div class='section-title'>🪑 좌석 별 배치</div>", unsafe_allow_html=True)
    st.markdown(build_html_table(), unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# [2] 스마트폰 모바일용 레이아웃 (상단 명단 4X5, 하단 좌석 표 자동 압축)
# ------------------------------------------------------------------
st.markdown("<div class='mobile-layout'>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>👥 명단 (모바일)</div>", unsafe_allow_html=True)
if st.session_state.members:
    mobile_grid_cols = st.columns(4) # 💡 모바일 가로 4열 강제 배열 (4X5 격자 형성)
    for idx, name in enumerate(st.session_state.members):
        col_target = mobile_grid_cols[idx % 4]
        if col_target.button(name, key=f"mo_member_{name}_{idx}", use_container_width=True):
            assign_seat(name)
else:
    st.success("모든 배정이 완료되었습니다!")

st.markdown("<br><div class='section-title'>🪑 좌석 별 배치</div>", unsafe_allow_html=True)
st.markdown(build_html_table(), unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)