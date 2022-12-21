from numpy import around


class GameManager:

    def __init__(self, map_path:str):
        with open(map_path, 'r') as map:
            file_date = map.readlines()

        self.set_map(file_date)

        self.is_end:bool = False
        self.hot_item = 0
        self.cool_item = 0

    def set_map(self,file_date):
        self.map_data = []
        for file_line in file_date:
            if file_line.startswith('N'): #Nの行の処理
                pass
            if file_line.startswith('T'): #Tの行の処理
                self.turn = int(file_line.split(":")[1])
            if file_line.startswith('S'): #Sの行の処理
                #座標系が違うので反転
                self.map_size = list(map(int,file_line.split(":")[1].split(","))).reverse()
            if file_line.startswith('D'): #Dの行の処理
                self.map_data.append(list(map(int,file_line.split(":")[1].split(","))))
            if file_line.startswith('H'): #Hの行の処理
                #座標系が違うので反転
                self.hot_position = list(map(int,file_line.split(":")[1].split(","))).reverse()
            if file_line.startswith('C'): #Cの行の処理
                #座標系が違うので反転
                self.cool_position = list(map(int,file_line.split(":")[1].split(","))).reverse()

    def get_is_end(self):
        return self.is_end

    def get_turn(self):
        return self.turn

    def get_ready(self, character):
        if character == "hot":
            position = self.hot_position
        if character == "cool":
            position = self.cool_position

        if position[0] < 0 or position[1] < 0 or position[0] >= self.map_size[0] or position[1] >= self.map_size[1] or self.map_data[position[0], position[1]] == 2: #2は壁
            self.is_end = True
            return [0 for i in range(10)]

        return self.around_data(position)

    def around_data(self,position):
        data = [1]
        for y in [-1,0,1]:
            for x in [-1,0,1]:
                data.append(self.refer_map([position[0] + y,position[1] + x]))
        return data

    def refer_map(self, position):
        if position[0] < 0 or position[1] < 0 or position[0] >= self.map_size[0] or position[1] >= self.map_size[1]:
            return 1
        else:
            return self.map_data[position[0], position[1]]

    def walk(self, character, direction):
        if character == "hot":
            position = self.hot_position
        if character == "cool":
            position = self.cool_position

        dx = 0
        dy = 0

        if direction == "u":
            dy = -1
        if direction == "d":
            dy = 1
        if direction == "r":
            dx = 1
        if direction == "l":
            dx = -1

        position = [position[0] + dy, position[1] + dx]
        if self.map_data[position] == 3:
            self.map_data[position] = 0
            self.map_data[position[0] - dy, position[1] - dx] = 2

        if character == "hot":
            self.hot_position = position
        if character == "cool":
            self.cool_position = position

        return self.get_ready(character)
        
    def look(self, character, direction):
        if character == "hot":
            position = self.hot_position
        if character == "cool":
            position = self.cool_position

        if direction == "u":
            data = self.around_data(position[0] - 2, position[1])
        if direction == "d":
            data = self.around_data(position[0] + 2, position[1])
        if direction == "r":
            data = self.around_data(position[0], position[1] + 2)
        if direction == "l":
            data = self.around_data(position[0], position[1] - 2)

        return data

    def search(self, character, direction):
        if character == "hot":
            position = self.hot_position
        if character == "cool":
            position = self.cool_position

        if direction == "u":
            x = -1
            y = 0
        if direction == "d":
            x = 1
            y = 0
        if direction == "r":
            x = 0
            y = 1
        if direction == "l":
            x = 0
            y = -1

        data = [1]
        for i in range(1,10):
            data.append(self.map_data[position[0] + i * x, position[0] + i * y])

        return data


    def put(self, character, direction):
        if character == "hot":
            position = self.hot_position
        if character == "cool":
            position = self.cool_position

        if direction == "u":
            self.map_data[position[0] - 1, position[1]] = 2
        if direction == "d":
            self.map_data[position[0] + 1, position[1]] = 2
        if direction == "r":
            self.map_data[position[0], position[1] + 1] = 2
        if direction == "l":
            self.map_data[position[0], position[1] - 1] = 2

    def char_action(self, character:str, action:str):
        if action.startswith("w"):
            data = self.walk(character, action[1])
        elif action.startswith("l"):
            data = self.look(character, action[1])
        elif action.startswith("s"):
            data = self.search(character, action[1])
        elif action.startswith("p"):
            data = self.put(character, action[1])
        else:
            data = self.get_ready(character)

        return data

    def result(self):
        if self.cool_item > self.hot_item:
            return "hot",self.cool_item,self.hot_item
        else:
            return "cool",self.cool_item,self.hot_item