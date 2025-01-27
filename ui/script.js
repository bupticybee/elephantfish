let ws;
let selectedPiece = null; // 当前选中的棋子
const GRID_SIZE = 80;  // 格子大小
const BOARD_PADDING = 40;  // 棋盘边距

function initializeBoard() {
    const chessboard = document.querySelector('.chessboard');
    const pieces = document.querySelectorAll('.piece');

    // 初始化棋子位置
    pieces.forEach(piece => {
        const position = piece.getAttribute('data-position');
        if (position) {
            const [col, row] = position.split('');
            const x = col.charCodeAt(0) - 'a'.charCodeAt(0);
            const y = parseInt(row);
            
            piece.style.left = `${BOARD_PADDING + x * GRID_SIZE}px`;
            piece.style.top = `${BOARD_PADDING + (9 - y) * GRID_SIZE}px`;
            // 确保棋子在最上层
            piece.style.zIndex = "100";
        }
    });

    // 确保棋盘网格在底层
    const boardGrid = document.querySelector('.board-grid');
    if (boardGrid) {
        boardGrid.style.zIndex = "1";
    }

    // 移除所有现有的点击事件
    document.removeEventListener('click', handleGlobalClick, true);
    
    // 在document级别添加一个捕获阶段的点击事件处理器
    document.addEventListener('click', handleGlobalClick, true);
}

function handleGlobalClick(event) {
    console.log("Global click handler triggered");
    
    // 检查是否点击了棋子
    if (event.target.classList.contains('piece')) {
        console.log("Piece clicked");
        event.stopPropagation();
        handlePieceClick(event);
        return;
    }

    // 检查是否点击了棋盘
    const chessboard = document.querySelector('.chessboard');
    if (event.target === chessboard || event.target.classList.contains('board-grid')) {
        console.log("Board clicked");
        handleBoardClick(event);
    }
}

function handlePieceClick(event) {
    console.log("handlePieceClick processing");
    const piece = event.target;
    
    if (selectedPiece === piece) {
        console.log("Deselecting piece");
        deselectPiece();
    } else if (selectedPiece) {
        console.log("Attempting to capture piece");
        const fromPos = selectedPiece.getAttribute('data-position');
        const toPos = piece.getAttribute('data-position');
        makeMove(fromPos, toPos);
    } else {
        console.log("Selecting new piece");
        selectPiece(piece);
    }
}

function handleBoardClick(event) {
    console.log("handleBoardClick processing");
    if (!selectedPiece) return;

    const chessboard = document.querySelector('.chessboard');
    const rect = chessboard.getBoundingClientRect();
    const x = event.clientX - rect.left - BOARD_PADDING;
    const y = event.clientY - rect.top - BOARD_PADDING;

    const col = Math.round(x / GRID_SIZE);
    const row = 9 - Math.round(y / GRID_SIZE);

    if (col >= 0 && col < 9 && row >= 0 && row < 10) {
        const toPos = `${String.fromCharCode(97 + col)}${row}`;
        const fromPos = selectedPiece.getAttribute('data-position');
        makeMove(fromPos, toPos);
    }
}

function selectPiece(piece) {
    if (selectedPiece) {
        selectedPiece.classList.remove('selected');
    }
    selectedPiece = piece;
    piece.classList.add('selected');
}

function deselectPiece() {
    if (selectedPiece) {
        selectedPiece.classList.remove('selected');
        selectedPiece = null;
    }
}

async function makeMove(fromPos, toPos) {
    console.log(`Moving piece from ${fromPos} to ${toPos}`);
    
    // 移动玩家的棋子
    const movingPiece = document.querySelector(`[data-position="${fromPos}"]`);
    const targetPiece = document.querySelector(`[data-position="${toPos}"]`);
    
    if (targetPiece) {
        targetPiece.remove();
    }
    
    movingPiece.setAttribute('data-position', toPos);
    
    const col = toPos.charCodeAt(0) - 97;
    const row = 9 - parseInt(toPos.slice(1));
    
    movingPiece.style.left = `${col * GRID_SIZE + BOARD_PADDING}px`;
    movingPiece.style.top = `${row * GRID_SIZE + BOARD_PADDING}px`;
    
    if (selectedPiece) {
        selectedPiece.classList.remove('selected');
        selectedPiece = null;
    }

    // 发送移动到 elephantfish 引擎并等待 AI 的响应
    try {
        const move = `${fromPos}${toPos}`;  // 例如 "h2e2"
        const response = await fetch('http://localhost:8000/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ move: move })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();  // 解析 JSON 响应
        const aiMove = data.move;  // 从 JSON 响应中获取移动
        
        if (aiMove) {
            // 解析AI的移动 (例如 "h7h6")
            const aiFromPos = aiMove.substring(0, 2);
            const aiToPos = aiMove.substring(2, 4);
            
            console.log(`AI moves from ${aiFromPos} to ${aiToPos}`);
            
            // 延迟一小段时间后执行AI的移动，让玩家能看清楚
            setTimeout(() => {
                const aiPiece = document.querySelector(`[data-position="${aiFromPos}"]`);
                const aiTargetPiece = document.querySelector(`[data-position="${aiToPos}"]`);
                
                if (aiTargetPiece) {
                    aiTargetPiece.remove();
                }
                
                if (aiPiece) {
                    aiPiece.setAttribute('data-position', aiToPos);
                    
                    const aiCol = aiToPos.charCodeAt(0) - 97;
                    const aiRow = 9 - parseInt(aiToPos.slice(1));
                    
                    aiPiece.style.left = `${aiCol * GRID_SIZE + BOARD_PADDING}px`;
                    aiPiece.style.top = `${aiRow * GRID_SIZE + BOARD_PADDING}px`;
                }
            }, 500);  // 500ms 延迟
        }
    } catch (error) {
        console.error('Error:', error);
        alert('与象棋引擎通信时出错，请确保 elephantfish 服务正在运行');
    }
}

function updateStatus(message, color) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.style.color = color;
}

// 页面加载完成后初始化
window.addEventListener('load', () => {
    initializeBoard();
}); 