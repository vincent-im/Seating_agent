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

# 2. 엑셀 기반 좌석 표(Table) 및 이름표 스타일 지정을 위한 CSS 주입
st.markdown("""
    <style>
    /* 전체 레이아웃 패딩 최적화 */
    .block-container {
        padding: 1.5rem 1rem !important;
    }
    .section-title { 
        font-size: 1.4rem !important; 
        font-weight: bold; 
        margin-bottom: 1rem !important; 
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

    /* 💡 엑셀 스타일 좌석 테이블 디자인 */
    .seat-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 12px; /* 셀과 셀 사이의 통로 간격 */
        table-layout: fixed;
    }
    .seat-table td {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        height: 90px; /* 좌석 슬롯의 높이 */
        text-align: center;
        vertical-align: middle;
        font-weight: bold;
        position: relative;
        background-color: #F8F9FA;
    }
    
    /* 💡 실제 배정된 좌석 슬롯의 스타일 (정중앙 정렬 보장) */
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
    
    /* 빈 공간 (통로, 기둥 등) 처리 */
    .empty-space {
        border: none !important;
        background-color: transparent !important;
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
    
    /* 슬롯 안의 원래 좌석 문자(A, B, C...) 투명도 조절 */
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

# 4. 💡 좌석배치.xlsx 파일 읽기 및 가용한 알파벳 좌석 추출 함수
def load_excel_layout():
    file_name = "좌석배치.xlsx"
    if os.path.exists(file_name):
        try:
            df = pd.read_excel(file_name, header=None)
            # 파일 내부의 모든 값을 공백 제거하여 리스트 및 DF 형태로 보관
            df = df.applymap(lambda x: str(x).strip() if pd.notna(x) else "")
            
            # 실제 배정 가능한 좌석 알파벳 리스트 추출
            seats = []
            for row in df.values:
                for val in row:
                    if val != "":
                        seats.append(val)
            return df, seats
        except Exception as e:
            st.error(f"좌석배치.xlsx 파싱 오류: {e}")
            
    # 파일이 없을 경우 기본 4x7 백업 테이블 레이아웃 자동 생성
    backup_data = [
        ["A", "B", "C", "", "D", "E", "F"],
        ["", "G", "H", "", "I", "J", "K"],
        ["L", "M", "N", "", "O", "P", "Q"],
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
title_col.subheader("🖥️ 오피스 자율 좌석 배치 시스템")
with btn_col:
    if st.button("🔄 초기화", key="reset_btn", use_container_width=True):
        reset_program()

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

# [우측] 💡 엑셀 직접 파싱 및 실시간 HTML 테이블 드로잉 영역
with pc_right:
    st.markdown("<div class='section-title'>🪑 실시간 배치 도면 (Excel 동적 연동)</div>", unsafe_allow_html=True)
    
    # 엑셀의 형태를 완벽하게 유지하는 순수 HTML Table 생성 시작
    html_table = "<table class='seat-table'>"
    
    for r_idx, row in layout_df.iterrows():
        html_table += "<tr>"
        for c_idx, cell_value in enumerate(row):
            # 빈 셀인 경우 (통로나 기둥 영역)
            if cell_value == "":
                html_table += "<td class='empty-space'></td>"
            else:
                # 해당 자리에 사람이 배정되었는지 확인
                assigned_user = st.session_state.assignments.get(cell_value, None)
                
                html_table += "<td>"
                if assigned_user:
                    # 사람이 있는 경우: 전용 컬러 뱃지로 정중앙 표시
                    style_class = "name-leader" if "팀장" in assigned_user else "name-member"
                    html_table += f"""
                    <div class='seat-slot-assigned'>
                        <span class='name-badge {style_class}'>{assigned_user}</span>
                        <span class='seat-label'>좌석 {cell_value}</span>
                    </div>
                    """
                else:
                    # 사람이 아직 없는 경우: 연한 폰트로 좌석 기호만 중앙 표시
                    html_table += f"<span style='color: #BCBCBC; font-size: 1.1rem;'>{cell_value}</span>"
                html_table += "</td>"
        html_table += "</tr>"
    
    html_table += "</table>"
    
    # 생성된 동적 HTML 테이블 마운트
    st.markdown(html_table, unsafe_allow_html=True)