import sys
import socketControl
from concurrent.futures import ThreadPoolExecutor

def main():
    cool = socketControl.Socket(2009)
    hot = socketControl.Socket(2010)

    args = sys.argv
    print(args)

    setup(cool,hot)

    cool_name = cool.recieve()
    hot_name = hot.recieve()

    print(f"cool: {cool_name} vs hot: {hot_name}")

    while True: #ゲームマネージャーからの継続中チェック
        battle(cool)
        battle(hot)

def setup(cool,hot):
    executor = ThreadPoolExecutor(max_workers=2)
    c = executor.submit(cool.wait_connect())
    h = executor.submit(hot.wait_connect())

    while True:
        if c.done() and h.done():
            break

def battle(character):
    character.send("@")
    command = character.recieve()
    #ここでゲームマネージャーにコマンドを送信して返り値として結果を受け取る
    result = ""
    character.send(result)

if __name__ == "__main__":
    main()