import json, time, re
from http.server import HTTPServer, SimpleHTTPRequestHandler

import elephantfish

class ChessRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        SimpleHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        print(f"get option req, path={self.path}")
        self.send_response(200, "ok")
        # self.send_header('Access-Control-Allow-Credentials', 'true')
        # self.send_header('Access-Control-Allow-Origin', '*')
        # self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        # self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()

    def do_POST(self):
        print(f"get post req, path={self.path}")
        if self.path == '/move':
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            move_data = json.loads(post_data.decode('utf-8'))

            # 获取移动步骤
            move = move_data.get('move')
            if not move:
                self.send_error(400, "Missing move parameter")
                return

            try:
                # 这里调用象棋引擎的代码处理移动并获取 AI 的响应
                print(f"key log: To Process move: {move}")
                ai_move = process_move(move)  # 这个函数需要实现
                # print(f"key log: AI move: {ai_move}")

                # 发送响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'move': ai_move}).encode('utf-8'))
            except Exception as e:
                self.send_error(500, str(e))

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ChessRequestHandler)
    print(f"Starting chess server on port {port}...")
    httpd.serve_forever()

hist = [elephantfish.Position(elephantfish.initial, 0)]
searcher = elephantfish.Searcher()

def process_move(input_move):
    """
    处理玩家的移动并返回 AI 的响应
    :param input_move: 字符串，格式如 "h2e2"
    :return: 字符串，AI 的移动，格式如 "h7h6"
    """

    elephantfish.print_pos(hist[-1])

    if hist[-1].score <= -elephantfish.MATE_LOWER:
        return ("You lost")

    print(f"key log: input_move: {input_move}")
    match = re.match('([a-i][0-9])'*2, input_move)
    if not match:
        return ("Please enter a move like h2e2") # taylor use error code
    move = elephantfish.parse(match.group(1)), elephantfish.parse(match.group(2))
    if move not in hist[-1].gen_moves():
        return "ErrInvalidMove"

    print(f"key log: input move is valid")
    hist.append(hist[-1].move(move))

    # After our move we rotate the board and print it again.
    # This allows us to see the effect of our move.
    elephantfish.print_pos(hist[-1].rotate())

    if hist[-1].score <= -elephantfish.MATE_LOWER:
        return ("You won")

    # Fire up the engine to look for a move.
    start = time.time()
    for _depth, move, score in searcher.search(hist[-1], hist):
        if time.time() - start > elephantfish.THINK_TIME:
            break

    if score == elephantfish.MATE_UPPER:
        print("Checkmate!")

    # The black player moves from a rotated position, so we have to
    # 'back rotate' the move before printing it.
    ai_move = elephantfish.render(255-move[0] - 1) + elephantfish.render(255-move[1]-1)
    print("Think depth: {} My move: {}".format(_depth, ai_move))
    hist.append(hist[-1].move(move))
    elephantfish.print_pos(hist[-1])
    return ai_move

if __name__ == '__main__':
    run_server()
