import chess
import chess.svg
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Chess", layout="centered")

st.title("♟️ Streamlit 체스 게임")

# 세션 상태 초기화
if "board" not in st.session_state:
    st.session_state.board = chess.Board()

board = st.session_state.board

# 리셋 버튼
if st.button("새 게임 시작"):
    st.session_state.board = chess.Board()
    st.rerun()

# 현재 차례 및 상태 표시
if board.is_checkmate():
    st.error("체크메이트! 게임이 종료되었습니다.")
elif board.is_stalemate():
    st.warning("스테일메이트! 비겼습니다.")
else:
    turn_str = "백(White)" if board.turn == chess.WHITE else "흑(Black)"
    st.info(f"현재 차례: **{turn_str}**")

# 체스판 SVG 출력
board_svg = chess.svg.board(board=board, size=400)
components.html(board_svg, height=410)

# 수 입력
with st.form(key="move_form", clear_on_submit=True):
    move_input = st.text_input(
        "수를 입력하세요 (예: e2e4, g1f3)",
        placeholder="SAN 또는 UCI 형식 (예: e4, Nf3, e2e4)"
    )
    submit_button = st.form_submit_button(label="수 두기")

if submit_button and move_input:
    try:
        # SAN 형식(예: e4, Nf3) 우선 시도 후 UCI 형식(예: e2e4) 시도
        try:
            move = board.parse_san(move_input.strip())
        except ValueError:
            move = chess.Move.from_uci(move_input.strip())

        if move in board.legal_moves:
            board.push(move)
            st.rerun()
        else:
            st.error("유효하지 않은 수입니다. 규칙에 맞는 수를 입력하세요.")
    except Exception:
        st.error("입력 형식이 올바르지 않습니다. (예: e4, Nf3 또는 e2e4)")

# 가능한 유효 수 안내
with st.expander("현재 가능한 수 (UCI)"):
    legal_moves_str = ", ".join([move.uci() for move in board.legal_moves])
    st.write(legal_moves_str)
