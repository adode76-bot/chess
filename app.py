import streamlit as st
import chess

st.set_page_config(page_title="터치 체스 게임", page_icon="♟️", layout="centered")

st.title("♟️ 터치/클릭 체스 게임")

# 1. 유니코드 체스 기물 심볼 매핑
PIECE_UNICODE = {
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙', # 백
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟', # 흑
    None: ' '
}

# 2. 세션 상태 초기화
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_sq" not in st.session_state:
    st.session_state.selected_sq = None

board = st.session_state.board

# 클릭 이벤트 처리 함수
def handle_square_click(sq_index):
    # 이미 선택된 칸이 있는 경우 -> 두 번째 클릭 (이동 시도)
    if st.session_state.selected_sq is not None:
        from_sq = st.session_state.selected_sq
        to_sq = sq_index
        
        # 동일한 칸을 다시 누르면 선택 취소
        if from_sq == to_sq:
            st.session_state.selected_sq = None
            return

        # 승급(폰이 끝까지 간 경우) 기본값을 퀸(Queen)으로 처리
        move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
        
        # 법적으로 가능한 수인지 확인
        if move in board.legal_moves:
            board.push(move)
            st.session_state.selected_sq = None
        else:
            # 합법적인 이동이 아니고, 클릭한 곳에 본인 기물이 있다면 선택 칸 변경
            piece = board.piece_at(to_sq)
            if piece and piece.color == board.turn:
                st.session_state.selected_sq = to_sq
            else:
                st.session_state.selected_sq = None
    # 선택된 칸이 없는 경우 -> 첫 번째 클릭 (기물 선택)
    else:
        piece = board.piece_at(sq_index)
        # 자기 턴의 기물만 선택 가능
        if piece and piece.color == board.turn:
            st.session_state.selected_sq = sq_index

# CSS 스타일 적용 (체스판 보더 및 버튼 크기 제어)
st.markdown("""
    <style>
    /* 버튼 폰트 크기 및 높이 설정 */
    div[data-testid="stColumn"] button {
        height: 60px !important;
        font-size: 30px !important;
        line-height: 1 !important;
        padding: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 게임 상태 표시
if board.is_checkmate():
    st.error("🏆 체크메이트! 게임이 종료되었습니다.")
elif board.is_stalemate():
    st.warning("🤝 스테일메이트! 비겼습니다.")
elif board.is_check():
    st.warning(f"⚠️ 체크! ({'백(White)' if board.turn == chess.WHITE else '흑(Black)'} 차례)")
else:
    st.info(f"현재 턴: **{'백(White)' if board.turn == chess.WHITE else '흑(Black)'}**")

# 선택된 기물 및 안내문 표시
if st.session_state.selected_sq is not None:
    sq_name = chess.square_name(st.session_state.selected_sq)
    st.caption(f"선택한 기물 위치: **{sq_name.upper()}** (이동할 위치를 클릭하세요)")
else:
    st.caption("움직일 기물을 클릭/터치하세요.")

# 4. 체스판 UI 렌더링 (8x8 Grid)
# 체스판은 8행(rank 8~1) x 8열(file a~h)로 구성됨
legal_destinations = []
if st.session_state.selected_sq is not None:
    legal_destinations = [m.to_square for m in board.legal_moves if m.from_square == st.session_state.selected_sq]

for rank in range(7, -1, -1):
    cols = st.columns(8)
    for file in range(8):
        sq = chess.square(file, rank)
        piece = board.piece_at(sq)
        piece_symbol = PIECE_UNICODE[piece.symbol()] if piece else " "
        
        # 버튼 라벨 및 스타일링
        # 선택된 칸 -> 🟪 (보라)
        # 이동 가능한 칸 -> 🟩 (연두)
        # 기본 체스판 -> ⬜ / ⬛
        is_selected = (sq == st.session_state.selected_sq)
        is_highlighted = sq in legal_destinations
        
        if is_selected:
            label = f"🟪 {piece_symbol}" if piece_symbol != " " else "🟪"
        elif is_highlighted:
            label = f"🟩 {piece_symbol}" if piece_symbol != " " else "🟩"
        else:
            label = piece_symbol

        with cols[file]:
            st.button(
                label,
                key=f"sq_{sq}",
                on_click=handle_square_click,
                args=(sq,),
                use_container_width=True
            )

# 5. 리셋 및 기보 기록
st.divider()
col_btn, col_exp = st.columns([1, 2])

with col_btn:
    if st.button("🔄 게임 리셋", type="secondary", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.selected_sq = None
        st.rerun()

with col_exp:
    with st.expander("📜 기보 기록 (SAN)"):
        st.write(board.to_san(board.move_stack) if board.move_stack else "기록 없음")
