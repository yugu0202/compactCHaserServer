import SocketControl
import time

def main():
    cool = SocketControl.Socket(2009)
    print(cool.wait_connect())
    time.sleep(1)
    cool.send("test")
    print(cool.recieve())

if __name__ == "__main__":
    main()
