import shutil

class Logger:
    def __init__(self,log_path:str,map_path:str):
        self.path = log_path
        shutil.copyfile(map_path,self.path)
        with open(self.path,mode="a") as f:
            f.write(f"mapend")

    def set_name(self,cool_name:str,hot_name:str):
        with open(self.path,mode="a") as f:
            f.write(f"\n{cool_name} {hot_name}")

    def action(self,character:str,command:str):
        with open(self.path,mode="a") as f:
            f.write(f"\n{character} {command}")

    def result(self,winner:str,reason:str):
        with open(self.path,mode="a") as f:
            f.write(f"\n{winner} win {reason}")
