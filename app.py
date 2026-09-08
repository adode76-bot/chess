import streamlit as st
import chess
import chess.svg
import base64

st.set_page_config(page_title="스트림릿 체스 게임", page_icon="♟️")

st.title("♟️ Streamlit 체스 게임")

# 세션 상태 초기화 (게임 보드 및 기물 선택)
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None

board = st.session_state.board

# SVG 체스판을 HTML 이미지를 만드는 함수
def render_board(board, selected_square=None):
    # 가능한 이동 경로 하이라이트
    fill = {}
    if selected_square is not None:
        fill[selected_square] = "#7B68EE" # 선택한 기물 (보라색)
        for move in board.legal_moves:
            if move.from_square == selected_square:
                fill[move.to_square] = "#90EE90" # 이동 가능한 칸 (연두색)

    board_svg = chess.svg.board(
        board=board,
        fill=fill,
        size=400,
        lastmove=board.peek() if board.move_stack else None
    )
    b64 = base64.b64encode(board_svg.encode('utf-8')).decode('utf-8')
    return f'<img src="data:image/svg+xml;base64,{b64}" width="100%"/>'

# 상단 게임 상태 출력
if board.is_checkmate():
    st.error("체크메이트! 게임이 종료되었습니다.")
elif board.is_stalemate():
    st.warning("스테일메이트! 비겼습니다.")
elif board.is_check():
    st.warning(f"체크! ({'백' if board.turn == chess.WHITE else '흑'} 차례)")
else:
    st.info(f"현재 턴: **{'백(White)' if board.turn == chess.WHITE else '흑(Black)'}**")

col1, col2 = st.columns([1, 1])

with col1:
    # 체스판 시각화
    st.markdown(render_board(board, st.session_state.selected_square), unsafe_allow_html=True)
    
    if st.button("🔄 게임 리셋", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        st.rerun()

with col2:
    st.subheader("🎮 수 두기")
    
    # 1. 기물 선택 방식 (클릭 대용 셀렉트 박스)
    legal_moves = list(board.legal_moves)
    
    if not board.is_game_over():
        # 이동 가능한 출발 지점 목록
        from_squares = sorted(list(set(m.from_square for m in legal_moves)))
        from_options = {chess.square_name(sq): sq for sq in from_squares}
        
        selected_from_name = st.selectbox(
            "1. 움직일 기물 위치 선택",
            options=["선택하세요"] + list(from_options.keys())
        )
        
        if selected_from_name != "선택하세요":
            from_sq = from_options[selected_from_name]
            st.session_state.selected_square = from_sq
            
            # 선택한 기물이 갈 수 있는 도착 지점 목록
            to_squares = [m.to_square for m in legal_moves if m.from_square == from_sq]
            to_options = {chess.square_name(sq): sq for sq in to_squares}
            
            selected_to_name = st.selectbox(
                "2. 도달할 위치 선택",
                options=["선택하세요"] + list(to_options.keys())
            )
            
            # 승급(Promotion) 처리
            promotion = None
            if any(m.promotion for m in legal_moves if m.from_square == from_sq):
                promo_piece = st.selectbox("승급 기물 선택", ["퀸(Q)", "룩(R)", "비숍(B)", "나이트(N)"])
                promo_map = {"퀸(Q)": chess.QUEEN, "룩(R)": chess.ROOK, "비숍(B)": chess.BISHOP, "나이트(N)": chess.KNIGHT}
                promotion = promo_map[promo_piece]

            if st.button("착수하기", type="primary", use_container_width=True):
                if selected_to_name != "선택하세요":
                    to_sq = to_options[selected_to_name]
                    move = chess.Move(from_sq, to_sq, promotion=promotion)
                    
                    if move in board.legal_moves:
                        board.push(move)
                        st.session_state.selected_square = None
                        st.rerun()
                    else:
                        st.error("유효하지 않은 이동입니다.")
        else:
            st.session_state.selected_square = None

    # 기보 기록
    with st.expander("📜 기보 기록 (SAN)"):
        st.write(board.to_san(board.move_stack) if board.move_stack else "기록 없음")
