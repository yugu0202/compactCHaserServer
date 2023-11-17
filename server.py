#!/usr/bin/python

import sys
import os
import argparse
from concurrent.futures import ThreadPoolExecutor
import signal

import SocketControl
import DumpSystem
import BoardManager

signal.signal(signal.SIGINT, signal.SIG_DFL)

def main():
    parser = argparse.ArgumentParser(
        prog="compact CHaser Server",
        usage="py server.py <MAPPATH> [OPTIONS]",
        description="このプログラムはコマンドライン上で簡単にCHaserの対戦を行うためのものです",
        fromfile_prefix_chars="@"
    )
    """
    py server.py {map_path} --first-port {first_port} --second-port {second_port} --dump-path {dump_path}
    py server.py {map_path} -f {first_port} -s {second_port} -d {dump_path}

    py server.py {map_path} --first-port {first_port} --second-port {second_port} --non-dump
    py server.py {map_path} -f {first_port} -s {second_port} -nd
    """
    parser.add_argument("mappath", help="マップのパス(実行ディレクトリから相対)")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s v2.0.1")
    parser.add_argument("-f", "--first-port", type=int, default=2009, help="先攻のポート (type: %(type)s, default: %(default)s)")
    parser.add_argument("-s", "--second-port", type=int, default=2010, help="後攻のポート (type: %(type)s, default: %(default)s)")
    parser.add_argument("-nd", "--non-dump", action="store_true", help="このオプションがつけられた場合dumpを出力しません")
    parser.add_argument("-d", "--dump-path", default="./chaser.dump", help="dumpの出力先(実行ディレクトリから相対) (default: %(default)s)")

    args = parser.parse_args()
    print(args)

    base_path = os.getcwd()
    map_path = os.path.join(base_path, args.mappath)
    dump_path = os.path.join(base_path, args.dump_path)

    if not os.path.exists(map_path):
        print(f"Error: map file not exists\npath: {map_path}", file=sys.stderr)
        sys.exit(1)

    #ロガーの準備
    dump_system = DumpSystem.DumpSystem(args.non_dump,dump_path,map_path)

    #ゲームマネージャーの初期化
    board_manager = BoardManager.BoardManager(map_path)
    turn = board_manager.turn

    #ソケットの準備
    cool = SocketControl.Socket(args.first_port,"cool")
    hot = SocketControl.Socket(args.second_port,"hot")

    print(f"cool port: {args.first_port}\nhot port: {args.second_port}\nmap path: {map_path}\ndump path: {dump_path}")
    print(f"connect wait...")

    setup(cool,hot)

    #接続完了したので名前を受け取る
    cool_name = cool.recieve()
    hot_name = hot.recieve()

    #名前をログに記録
    dump_system.set_name(cool_name, hot_name)

    print("ready")
    print(f"cool: \"{cool_name}\" vs hot: \"{hot_name}\"\nstart!!")

    #対戦処理
    while turn > 0:
        try:
            if turn & 1 == 1:
                tag = hot.tag
                battle(hot,dump_system,board_manager)
            else:
                tag = cool.tag
                battle(cool,dump_system,board_manager)
        except ConnectionAbortedError:
            print(f"{tag} is lose\nreason: lost connection")
            dump_system.result(character.tag,"lose",f"{tag} lost connection")
            return

        #試合終了の処理
        if board_manager.game_over:
            print(f"{tag} is lose\nreason: {board_manager.go_reason}", file=sys.stderr)
            dump_system.result(tag,"lose",f"{board_manager.go_reason}")
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
        dump_system.result(player,result,f"cool {cool_item} : hot {hot_item}")

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
def battle(character,dump_system,board_manager):
    character.send("@") #開始の合図
    recieve = recieve_action(character)
    if recieve != "gr":
        board_manager.game_over = True
        board_manager.go_reason = "{character.tag} bad request"
        return
    data = board_manager.char_action(character.tag,recieve) #get ready
    result = "".join(map(str,data))
    character.send(result) #行動後のデータ
    if board_manager.game_over:
        return
    recieve = recieve_action(character) # walk look search put
    data = board_manager.char_action(character.tag,recieve)
    dump_system.action(board_manager.get_map_str(),",".join(map(str,reversed(board_manager.cool_position))),",".join(map(str,reversed(board_manager.hot_position))),board_manager.cool_item,board_manager.hot_item)
    result = "".join(map(str,data))
    character.send(result)
    if board_manager.game_over:
        return
    recieve = character.recieve() #ここは終了の合図 #が来る

def recieve_action(character):
    recieve = character.recieve()
    if not recieve:
        print(f"{character.tag} is lose\nreason: lost connection", file=sys.stderr)
        dump_system.result(character.tag,"lose",f"{character.tag} lost connection")
        sys.exit(1)
    if not len(recieve) == 2:
        print(f"{character.tag} is lose\nreason: command {recieve} does not exists", file=sys.stderr)
        dump_system.result(character.tag,"lose",f"{character.tag} sent a command that does not exist. command: {recieve}")
        sys.exit(1)
    return recieve

if __name__ == "__main__":
    main()
