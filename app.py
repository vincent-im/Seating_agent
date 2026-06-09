import streamlit as st
import pandas as pd
import random
import os

# 1. PC 화면 최적화 및 레이아웃 기본 설정
st.set_page_config(
    page_title="오피스 좌석 배치 프로그램",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 엑셀 기반 좌석 표(Table) 및 잘림 방지 패딩 보정을 위한 CSS 주입
st.markdown("""
    <style>
    /* 💡 [핵심 교정 단락] 상단 시스템 메뉴와 겹쳐 잘리는 현상을 막기 위해 여백을 4.5rem으로 늘림 */
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    
    /* 섹션 타이틀 서식 */
    .section-title { 
        font-size: 1.4rem !important; 
        font-weight: bold; 
        margin-bottom: 1.2rem !important; 
        color: #2C3E50; 
    }
    
    /* 대기 명단 네모 박스 스타일 (2X9 배열) */
    div.stButton > button {
        width: 100% !important;
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #dcdcdc !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 10px 5px !important;
        min-height: 45px !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #4A90E2 !important;
        background-color: #f0f7ff !important;
    }

    /* 엑셀 스타일 좌석 테이블 디자인 */
    .seat-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 12px; /* 셀과 셀 사이의 가로 통로 간격 */
        table-layout: fixed;
    }
    .seat-table td {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        height: 90px; /* 일반 좌석 슬롯의 높이 */
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
        height: 40px !important; /* 세로 공백 통로의 높이 */
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
        padding: 4px;
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05);
    }
    
    /* 이름표 뱃지 서식 및 배색 */
    .name-badge {
        font-size: 14px !important;
        font-weight: bold !important;
        padding: 6px 12px !important;
        border-radius: 4px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        display: inline-block;
        white-space: nowrap;
    }
    .name-leader { background-color: #FFEB3B !important; color: #E65100 !important; border: 2px solid #E65100 !important; }
    .name-member { background-color: #2ECC71 !important; color: #FFFFFF !important; border: 1px solid #27AE60 !important; }
    
    /* 슬롯 안의 원래 좌석 문자 투명도 조절 */
    .seat-label {
        font-size: 11px;
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
            df = df.fillna("") # 결측치를 빈 문자열로 변환
            
            # 호환성을 고려한 맵핑 함수 가동
            if hasattr(df, 'map'):
                df = df.map(lambda x: str(x).strip())
            else:
                df = df.applymap(lambda x: str(x).strip())
            
            # 배정 대상이 될 실제 좌석 문자만 풀(Pool)로 수집
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
# 상단 글로벌 제어바 헤더 (패딩 보정으로 완벽하게 노출됨)
# ------------------------------------------------------------------
title_col, btn_col = st.columns([4, 1])
title_col.subheader("🖥️ 오피스 자율 좌석 배치 시스템")
with btn_col:
    if st.button("🔄 초기화", key="reset_btn", use_container_width=True):
        reset_program()

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# PC 전용 레이아웃 분할 (좌측 명단 2X9, 우측 엑셀 데이터 동적 표)
# ------------------------------------------------------------------
pc_left, pc_right = st.columns([1, 2.5])

# [좌측] 선택 대기 명단 영역 (2X9 격자 배열)
with pc_left:
    st.markdown("<div class='section-title'>👥 선택 대기 명단</div>", unsafe_allow_html=True)
    if st.session_state.members:
        pc_grid_cols = st.columns(2)
        for idx, name in enumerate(st.session_state.members):
            col_target = pc_grid_cols[idx % 2]
            if col_target.button(name, key=f"pc_member_{name}_{idx}", use_container_width=True):
                assign_seat(name)
    else:
        st.success("모든 배정이 완료되었습니다!")

# [우측] 엑셀의 세로 공백 행까지 완벽하게 재현하는 테이블 드로잉 영역
with pc_right:
    st.markdown("<div class='section-title'>🪑 실시간 배치 도면 (세로 통로 반영)</div>", unsafe_allow_html=True)
    
    html_table = "<table class='seat-table'>"
    
    for r_idx, row in layout_df.iterrows():
        # 해당 행 전체가 완전히 비어있는 행(세로 공백 행)인지 판별
        is_empty_row = all(cell_value == "" for cell_value in row)
        
        html_table += "<tr>"
        for c_idx, cell_value in enumerate(row):
            if is_empty_row:
                # 완전히 비어있는 줄인 경우 넓고 투명한 세로 통로 공간으로 출력
                html_table += f"<td class='empty-row-space' colspan='{len(row)}'></td>"
                break
            elif cell_value == "":
                # 행 내부의 일반 빈 칸 (가로 통로 분리 구역)
                html_table += "<td class='empty-space'></td>"
            else:
                # 유효 좌석 슬롯 마운트
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
                    html_table += f"<span style='color: #BCBCBC; font-size: 1.1rem;'>{cell_value}</span>"
                html_table += "</td>"
        html_table += "</tr>"
    
    html_table += "</table>"
    st.markdown(html_table, unsafe_allow_html=True)