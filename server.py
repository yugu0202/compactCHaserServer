#!/usr/bin/python

import sys
import os
import argparse
from concurrent.futures import ThreadPoolExecutor
import signal

import SocketControl
import Logger
import BoardManager

signal.signal(signal.SIGINT, signal.SIG_DFL)

def main():
    parser = argparse.ArgumentParser(
        prog="compact CHaser Server",
        usage="py server.py <MAPPATH> [OPTIONS]",
        description="このプログラムはコマンドライン上で簡単にCHaserの対戦を行うためのものです"
    )
    """
    py server.py {map_path} --cport {cool_port} --hport {hot_port} --log {log_path}
    py server.py {map_path} -c {cool_port} -h {hot_port} -l {log_path}
    """
    parser.add_argument("mappath", help="マップのパス(実行ディレクトリから相対)")
    parser.add_argument("-f", "--firstport", default=2009, help="先攻のポート")
    parser.add_argument("-s", "--secondport", default=2010, help="後攻のポート")
    parser.add_argument("-l", "--log", default="./chaser.log", help="logの出力先(実行ディレクトリから相対)")

    args = parser.parse_args()

    base_path = os.getcwd()
    map_path = os.path.join(base_path, args.mappath)
    log_path = os.path.join(base_path, args.log)

    if not os.path.exists(map_path):
        print(f"Error: map file not exists\npath: {map_path}", file=sys.stderr)
        sys.exit(1)

    #ロガーの準備
    logger = Logger.Logger(log_path,map_path)

    #ゲームマネージャーの初期化
    board_manager = BoardManager.BoardManager(map_path)
    turn = board_manager.turn

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
    logger.set_name(cool_name, hot_name)

    print("ready")
    print(f"cool: \"{cool_name}\" vs hot: \"{hot_name}\"\nstart!!")

    #対戦処理
    while turn > 0:
        try:
            if turn & 1 == 1:
                tag = hot.tag
                battle(hot,logger,board_manager)
            else:
                tag = cool.tag
                battle(cool,logger,board_manager)
        except ConnectionAbortedError:
            print(f"{tag} is lose\nreason: lost connection")
            logger.result(character.tag,"lose",f"{tag} lost connection")
            return

        #試合終了の処理
        if board_manager.game_over:
            print(f"{tag} is lose\nreason: {board_manager.go_reason}", file=sys.stderr)
            logger.result(tag,"lose",f"{board_manager.go_reason}")
            break

        turn -= 1

    if turn == 0:
        print("turn end!!")
        #ゲームマネージャーから対戦結果の受け取り
        player,result = board_manager.result()
        cool_item = board_manager.cool_item
        hot_item = board_manager.hot_item
        if player:
            print(f"{player} {result}\nreason: score cool {cool_item} : hot {hot_item}")
        else:
            print(f"{result}\nreason: score cool {cool_item} : hot {hot_item}")
        logger.result(player,result,f"cool {cool_item} : hot {hot_item}")

        hot.send("@") #開始の合図
        hot.recieve()
        hot.send("".join(map(str,[0 for i in range(10)])))
        cool.send("@") #開始の合図
        cool.recieve()
        cool.send("".join(map(str,[0 for i in range(10)])))
    elif turn & 1 == 1:
        cool.send("@") #開始の合図
        cool.recieve()
        cool.send("".join(map(str,[0 for i in range(10)])))
    else:
        hot.send("@") #開始の合図
        hot.recieve()
        hot.send("".join(map(str,[0 for i in range(10)])))

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
def battle(character,logger,board_manager):
    character.send("@") #開始の合図
    recieve = recieve_action(character,logger)
    if recieve != "gr":
        board_manager.game_over = True
        board_manager.go_reason = "{character.tag} bad request"
        return
    data = board_manager.char_action(character.tag,recieve) #get ready
    result = "".join(map(str,data))
    character.send(result) #行動後のデータ
    if board_manager.game_over:
        return
    recieve = recieve_action(character,logger) # walk look search put
    data = board_manager.char_action(character.tag,recieve)
    result = "".join(map(str,data))
    character.send(result)
    if board_manager.game_over:
        return
    recieve = character.recieve() #ここは終了の合図 #が来る

def recieve_action(character,logger):
    recieve = character.recieve()
    if not recieve:
        print(f"{character.tag} is lose\nreason: lost connection", file=sys.stderr)
        logger.result(character.tag,"lose",f"{character.tag} lost connection")
        sys.exit(1)
    if not len(recieve) == 2:
        print(f"{character.tag} is lose\nreason: command {recieve} does not exists", file=sys.stderr)
        logger.result(character.tag,"lose",f"{character.tag} sent a command that does not exist. command: {recieve}")
        sys.exit(1)
    logger.action(character.tag,recieve)
    return recieve

if __name__ == "__main__":
    main()
