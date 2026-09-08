import chess
import chess.svg
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Interactive Chess Game", layout="centered")

st.title("♟️ 터치/클릭으로 두는 체스 게임")

# 세션 상태 초기화
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None

board = st.session_state.board

# 상단 제어 및 상태 표시
col1, col2 = st.columns([1, 2])

with col1:
    if st.button("🔄 새 게임 시작"):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        st.rerun()

with col2:
    if board.is_checkmate():
        st.error("🏆 체크메이트! 게임 종료")
    elif board.is_stalemate():
        st.warning("🤝 스테일메이트! 비겼습니다")
    elif board.is_check():
        st.warning(f"⚠️ 체크! 차례: {'백(White)' if board.turn == chess.WHITE else '흑(Black)'}")
    else:
        st.info(f"현재 차례: **{'백(White)' if board.turn == chess.WHITE else '흑(Black)'}**")

# 하이라이트 계산
selected_sq = st.session_state.selected_square
highlight_dict = {}

if selected_sq is not None:
    # 선택한 칸 하이라이트 (노란색)
    highlight_dict[selected_sq] = {"fill": "#f6ec7a"}
    
    # 해당 말이 움직일 수 있는 칸들 하이라이트 (연두색)
    for move in board.legal_moves:
        if move.from_square == selected_sq:
            highlight_dict[move.to_square] = {"fill": "#a2d149"}

# 체스판 SVG 생성
svg_code = chess.svg.board(
    board=board,
    size=380,
    fill=highlight_dict,
    coordinates=True
)

# SVG 체스판 출력
components.html(f"""
<div style="display: flex; justify-content: center; align-items: center;">
    {svg_code}
</div>
""", height=400)

# 터치/클릭 조작 인터페이스
st.subheader("📍 말 이동하기")

if selected_sq is None:
    st.write("1. **움직일 말의 위치**를 선택하세요.")
else:
    from_name = chess.square_name(selected_sq)
    st.write(f"선택한 위치: **{from_name.upper()}** ➡️ **도착할 위치**를 선택하세요.")

# 칸 선택 드롭다운 (현재 상태 반영)
squares = [chess.square_name(i) for i in range(64)]

# 선택 가능한 수/말 필터링
if selected_sq is None:
    # 현재 차례의 말이 있는 위치만 필터링
    valid_from_squares = list(set([chess.square_name(m.from_square) for m in board.legal_moves]))
    valid_from_squares.sort()
    
    selected_from = st.selectbox(
        "움직일 말 선택",
        options=["선택하세요..."] + [s.upper() for s in valid_from_squares],
        key="select_from"
    )
    
    if selected_from != "선택하세요...":
        sq_idx = chess.parse_square(selected_from.lower())
        st.session_state.selected_square = sq_idx
        st.rerun()

else:
    # 선택된 말이 갈 수 있는 위치만 필터링
    valid_to_squares = [chess.square_name(m.to_square) for m in board.legal_moves if m.from_square == selected_sq]
    valid_to_squares.sort()
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        selected_to = st.selectbox(
            "도착 위치 선택",
            options=["선택하세요..."] + [s.upper() for s in valid_to_squares],
            key="select_to"
        )
        if selected_to != "선택하세요...":
            to_sq_idx = chess.parse_square(selected_to.lower())
            
            # 수 두기
            move = chess.Move(selected_sq, to_sq_idx)
            # 폰 승급 처리 (기본 퀸)
            if chess.Move(selected_sq, to_sq_idx, promotion=chess.QUEEN) in board.legal_moves:
                move = chess.Move(selected_sq, to_sq_idx, promotion=chess.QUEEN)
                
            board.push(move)
            st.session_state.selected_square = None
            st.rerun()
            
    with col_b:
        if st.button("❌ 선택 취소", use_container_width=True):
            st.session_state.selected_square = None
            st.rerun()
