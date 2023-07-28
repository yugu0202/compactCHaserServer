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
    game_manager = BoardManager.BoardManager(map_path)
    turn = game_manager.turn

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

    character = hot

    #対戦処理
    while True:
        character = hot if character == cool else cool
        try:
            turn = battle(character,logger,game_manager,turn)
        except ConnectionAbortedError:
            print(f"{character.tag} is lose\nreason: lost connection")
            logger.result(character.tag,"lose",f"{character.tag} lost connection")
            return

        #試合終了の処理
        if game_manager.game_over:
            print(f"{character.tag} is lose\nreason: error")
            logger.result(character.tag,"lose",f"{character.tag} is error")
            break
        elif turn == 0:
            print("turn end!!")
            #ゲームマネージャーから対戦結果の受け取り
            player,result = game_manager.result()
            cool_item = game_manager.cool_item
            hot_item = game_manager.hot_item
            if player:
                print(f"{player} {result}\nreason score cool {cool_item} : hot {hot_item}")
            else:
                print(f"{result}\nreason score cool {cool_item} : hot {hot_item}")
            logger.result(player,result,f"cool {cool_item} : hot {hot_item}")
            break

    character = hot if character == cool else cool
    character.send("@")
    recieve = character.recieve()

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
def battle(character,logger,game_manager,turn):
    recieve = action("@",character,logger)
    data = game_manager.char_action(character.tag,recieve) #get ready
    if game_manager.game_over:
        return turn
    result = "".join(map(str,data))
    recieve = action(result,character,logger) # walk look search put
    data = game_manager.char_action(character.tag,recieve)
    if game_manager.game_over:
        return turn
    result = "".join(map(str,data))
    character.send(result)
    recieve = character.recieve_unstrip() #ここは終了の合図 #\r\nが来る

    turn -= 1

    return turn

def action(data:str,character,logger):
    character.send(data) #開始の合図(@) or 行動後のデータ
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
