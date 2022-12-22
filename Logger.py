import shutil

class Logger:
    def __init__(self,log_path:str,map_path:str):
        self.path = log_path
        shutil.copyfile(map_path,self.path)
        with open(self.path,mode="a") as f:
            f.write("mapend")

    def set_name(self,cool_name:str,hot_name:str):
        with open(self.path,mode="a") as f:
            f.write(f"\n{cool_name},{hot_name}")

    def action(self,character:str,command:str):
        with open(self.path,mode="a") as f:
            f.write(f"\n{character},{command}")

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
