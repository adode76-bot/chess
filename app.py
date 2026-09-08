import chess
import streamlit as st
from streamlit_chessboard import streamlit_chessboard

st.set_page_config(page_title="Streamlit Interactive Chess", layout="centered")

st.title("♟️ 드래그/클릭으로 움직이는 체스 게임")

# 세션 상태 초기화
if "board" not in st.session_state:
    st.session_state.board = chess.Board()

board = st.session_state.board

# 상단 제어 및 상태 표시
col1, col2 = st.columns([1, 2])

with col1:
    if st.button("🔄 새 게임 시작"):
        st.session_state.board = chess.Board()
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

# 체스판 컴포넌트 렌더링 (모바일 반응형 지원)
move = streamlit_chessboard(
    fen=board.fen(),
    key="chessboard",
)

# 유저가 말 이동을 완료했을 때 세션 업데이트
if move:
    # move 형태 예시: {'from': 'e2', 'to': 'e4', 'piece': 'p'}
    from_square = move.get("from")
    to_square = move.get("to")
    
    if from_square and to_square:
        uci_move = f"{from_square}{to_square}"
        
        # 프로모션(폰이 끝까지 갔을 때) 처리
        try:
            chess_move = chess.Move.from_uci(uci_move)
            if chess_move not in board.legal_moves:
                # 퀸으로 프로모션 시도
                chess_move = chess.Move.from_uci(f"{uci_move}q")
            
            if chess_move in board.legal_moves:
                board.push(chess_move)
                st.rerun()
        except ValueError:
            pass
