import chess
import streamlit as st
import streamlit.components.v1 as components

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

# 현재 FEN 주소 및 가능한 이동 목록 가져오기
current_fen = board.fen()
legal_moves = [move.uci() for move in board.legal_moves]

# HTML / JS Interactive Chessboard (Chessboard.js + Chess.js 사용)
chessboard_html = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            background-color: transparent;
        }}
        #board {{
            width: 420px;
        }}
        /* 선택된 칸 강조 스타일 */
        .highlight-square {{
            background-color: #f6ec7a !important;
        }}
        /* 이동 가능 칸 하이라이트 점 */
        .highlight-hint {{
            background: radial-gradient(circle, rgba(20,85,30,0.5) 25%, transparent 25%);
        }}
    </style>
</head>
<body>
    <div id="board"></div>

    <script>
        var board = null;
        var game = new Chess('{current_fen}');
        var $board = $('#board');

        function removeHighlights() {{
            $board.find('.square-55d68').removeClass('highlight-square');
            $board.find('.square-55d68').removeClass('highlight-hint');
        }}

        function addHighlight(square) {{
            $board.find('.square-' + square).addClass('highlight-square');
        }}

        function addHint(square) {{
            $board.find('.square-' + square).addClass('highlight-hint');
        }}

        function onDragStart (source, piece, position, orientation) {{
            // 게임이 끝났거나 차례가 아닌 말은 드래그 불가능
            if (game.game_over()) return false;
            if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
                (game.turn() === 'b' && piece.search(/^w/) !== -1)) {{
                return false;
            }}
        }}

        function onMouseoverSquare (square, piece) {{
            // 해당 칸에서 움직일 수 있는 위치 가져오기
            var moves = game.moves({{
                square: square,
                verbose: true
            }});

            if (moves.length === 0) return;

            // 선택한 위치 및 이동 가능한 위치 하이라이트
            addHighlight(square);
            for (var i = 0; i < moves.length; i++) {{
                addHint(moves[i].to);
            }}
        }}

        function onMouseoutSquare (square, piece) {{
            removeHighlights();
        }}

        function onDrop (source, target) {{
            removeHighlights();

            // 유효한 수인지 확인
            var move = game.move({{
                from: source,
                to: target,
                promotion: 'q' // 기본 승급을 여왕(Queen)으로 설정
            }});

            // 유효하지 않은 수라면 원래대로 복귀
            if (move === null) return 'snapback';

            // Python Streamlit 서버로 수 전달
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: source + target + (move.promotion ? move.promotion : '')
            }}, '*');
        }}

        function onSnapEnd () {{
            board.position(game.fen());
        }}

        var config = {{
            draggable: true,
            position: '{current_fen}',
            onDragStart: onDragStart,
            onDrop: onDrop,
            onMouseoverSquare: onMouseoverSquare,
            onMouseoutSquare: onMouseoutSquare,
            onSnapEnd: onSnapEnd,
            pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{{piece}}.png'
        }};

        board = Chessboard('board', config);
    </script>
</body>
</html>
"""

# HTML 컴포넌트를 통해 체스판 렌더링 및 유저의 이동(Move) 이벤트 수신
user_move = components.html(chessboard_html, height=450)

# JS에서 넘겨받은 수 처리
if user_move:
    # 텍스트 형태의 수(예: "e2e4")를 chess.Move 객체로 변환
    try:
        move = chess.Move.from_uci(str(user_move))
        if move in board.legal_moves:
            board.push(move)
            st.rerun()
    except ValueError:
        pass
