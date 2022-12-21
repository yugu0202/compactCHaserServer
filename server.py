import sys
import os
import argparse
from concurrent.futures import ThreadPoolExecutor
import signal

import SocketControl
import Logger

signal.signal(signal.SIGINT, signal.SIG_DFL)

def main():
    parser = argparse.ArgumentParser(
        prog="compact CHaser Server",
        usage="py server.py <MAPPATH> [OPTIONS]",
        description="このプログラムはコマンドで簡単にCHaserの対戦を行うためのものです"
    )
    """
    py server.py {map_path} --cport {cool_port} --hport {hot_port} --log {log_path}
    py server.py {map_path} -c {cool_port} -h {hot_port} -l {log_path}
    """
    parser.add_argument("mappath", help="マップのパス")
    parser.add_argument("-f", "--firstport", default=2009, help="coolのポート")
    parser.add_argument("-s", "--secondport", default=2010, help="hotのポート")
    parser.add_argument("-l", "--log", default="./chaser.log", help="logのパス")

    args = parser.parse_args()

    map_path = os.path.abspath(args.mappath)
    log_path = os.path.abspath(args.log)

    if not os.path.exists(map_path):
        print(f"Error: map file not exists\npath: {map_path}", file=sys.stderr)
        sys.exit(1)

    #ロガーの準備
    logger = Logger.Logger(log_path,map_path)

    #ゲームマネージャーの初期化

    turn = 100

    #ソケットの準備
    cool = SocketControl.Socket(args.firstport,"cool")
    hot = SocketControl.Socket(args.secondport,"hot")

    print(f"cool port: {args.firstport}\nhot port: {args.secondport}\nmap path: {map_path}\nlog path: {log_path}")
    print(f"connect wait...")

    setup(cool,hot)

    #接続完了したので名前を受け取る
    cool_name = cool.recieve()
    hot_name = hot.recieve()

    #名前をログに記録
    logger.set_name(cool_name,hot_name)

    print("ready")
    print(f"cool: \"{cool_name}\" vs hot: \"{hot_name}\"\nstart!!")

    is_end = False
    character = hot

    while not is_end: #ゲームマネージャーからの継続中チェック
        character = hot if character == cool else cool
        is_end,turn = battle(character,logger,turn)
        is_end = True if is_end else False
    
    #試合終了の処理
    if turn == 0:
        #ゲームマネージャーから対戦結果の受け取り
        pass
    else:
        logger.result(character.get_tag(),f"{character.get_tag()} is error")

    cool.close()
    hot.close()

#接続受付
def setup(cool,hot):
    #スレッディングして接続受付を非同期に行う
    executor = ThreadPoolExecutor(max_workers=2)
    c = executor.submit(cool.wait_connect())
    h = executor.submit(hot.wait_connect())

    #両方が接続完了したらsetup処理終わり
    while True:
        if c.done() and h.done():
            break

#キャラクター行動処理一回分
def battle(character,logger,turn):
    recieve = action("@",character,logger)
    result = "test" #ここでゲームマネージャーにコマンドを送信して返り値として結果を受け取る
    recieve = action(result,character,logger)
    result = "test" #ここでゲームマネージャーにコマンドを送信して返り値として結果を受け取る
    character.send(result)
    recieve = character.recieve() #ここは終了の合図 #\r\nが来る

    turn -= 1

    is_end = True if turn == 0 else False

    return is_end,turn

def action(data:str,character,logger):
    character.send(data) #開始の合図(@) or 行動後のデータ
    recieve = character.recieve().strip()
    if not len(recieve) == 2:
        print(f"Error: this command does not exist\ncommand {recieve}",file=sys.stderr)
        logger.result(character.get_tag(),f"{character.get_tag()} sent a command that does not exist. command: {recieve}")
        sys.exit(1)
    logger.action(character.get_tag(),recieve)
    return recieve

if __name__ == "__main__":
    main()