class Logger:
    def __init__(self,log_path:str,map_path:str):
        self.path = log_path
        with open(map_path, mode="r") as f:
            data = "".join(list(map(lambda x: x[2:],f.readlines())))

        with open(self.path, mode="w") as f:
            f.write(data);

    def set_name(self,cool_name:str,hot_name:str):
        with open(self.path,mode="a") as f:
            f.write(f"{cool_name},{hot_name}")

    def action(self,map_data:str,cool_pos:str,hot_pos:str,cool_item:int,hot_item:int):
        with open(self.path,mode="a") as f:
            f.write(f"\n{map_data}\n{cool_pos}\n{hot_pos}\n{cool_item},{hot_item}")

    def result(self,player:str,result:str,reason:str):
        winner = None
        if result == "lose":
            winner = "cool" if player == "hot" else "hot"
            result = "win"
        elif result == "win":
            winner = player

        if winner:
            with open(self.path,mode="a") as f:
                f.write("\ngameend")
                f.write(f"\n{winner},{result},{reason}")
        else:
            with open(self.path,mode="a") as f:
                f.write("\ngameend")
                f.write(f"\n{result},{reason}")
