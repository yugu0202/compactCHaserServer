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
                self.map_size = list(map(int,file_line.split(":")[1].split(",")))
                self.map_size.reverse()
            if file_line.startswith('D'): #Dの行の処理
                self.map_data.append(list(map(int,file_line.split(":")[1].split(","))))
            if file_line.startswith('H'): #Hの行の処理
                #座標系が違うので反転
                self.hot_position = list(map(int,file_line.split(":")[1].split(",")))
                self.hot_position.reverse()
            if file_line.startswith('C'): #Cの行の処理
                #座標系が違うので反転
                self.cool_position = list(map(int,file_line.split(":")[1].split(",")))
                self.cool_position.reverse()

    def get_is_end(self):
        return self.is_end

    def get_turn(self):
        return self.turn

    def get_ready(self, character):
        if character == "hot":
            position = self.hot_position
            enemy_position = self.cool_position
        if character == "cool":
            position = self.cool_position
            enemy_position = self.hot_position

        if self.is_end:
            return [0 for i in range(10)]

        if self.refer_map([position[0] - 1,position[1]]) == 2 and self.refer_map([position[0],position[1] + 1]) == 2 and self.refer_map([position[0] + 1,position[1]]) == 2 and self.refer_map([position[0],position[1] - 1]) == 2:
            print(f"{character} around block ;;")
            self.is_end = True
            return [0 for i in range(10)]

        if position[0] < 0 or position[1] < 0 or position[0] >= self.map_size[0] or position[1] >= self.map_size[1] or self.map_data[position[0]][position[1]] == 2: #2は壁
            print(f"{character} fill up ;;")
            self.is_end = True
            return [0 for i in range(10)]

        return self.around_data(position,enemy_position)

    def around_data(self,position,enemy_position):
        data = [1]
        for y in [-1,0,1]:
            for x in [-1,0,1]:
                data.append(self.refer_map([position[0] + y,position[1] + x],enemy_position))
        return data

    def refer_map(self, position,enemy_position=None):
        if position[0] < 0 or position[1] < 0 or position[0] >= self.map_size[0] or position[1] >= self.map_size[1]:
            return 2
        else:
            if position == enemy_position:
                return 1
            return self.map_data[position[0]][position[1]]

    def walk(self, character, direction):
        if character == "hot":
            position = self.hot_position
            point = self.hot_item
        if character == "cool":
            position = self.cool_position
            point = self.cool_item

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
        if self.map_data[position[0]][position[1]] == 3:
            self.map_data[position[0]][position[1]] = 0
            self.map_data[position[0] - dy][position[1] - dx] = 2
            point += 1

        if character == "hot":
            self.hot_position = position
            self.hot_item = point
        if character == "cool":
            self.cool_position = position
            self.cool_item = point

        return self.get_ready(character)
        
    def look(self, character, direction):
        if character == "hot":
            position = self.hot_position
            enemy_position = self.cool_position
        if character == "cool":
            position = self.cool_position
            enemy_position = self.hot_position

        if direction == "u":
            data = self.around_data([position[0] - 2, position[1]],enemy_position)
        if direction == "d":
            data = self.around_data([position[0] + 2, position[1]],enemy_position)
        if direction == "r":
            data = self.around_data([position[0], position[1] + 2],enemy_position)
        if direction == "l":
            data = self.around_data([position[0], position[1] - 2],enemy_position)

        return data

    def search(self, character, direction):
        if character == "hot":
            position = self.hot_position
            enemy_position = self.cool_position
        if character == "cool":
            position = self.cool_position
            enemy_position = self.hot_position

        x = 0
        y = 0

        if direction == "u":
            x = -1
        if direction == "d":
            x = 1
        if direction == "r":
            y = 1
        if direction == "l":
            y = -1

        data = [1]
        for i in range(1,10):
            data.append(self.refer_map([position[0] + i * x][position[0] + i * y],enemy_position))

        return data


    def put(self, character, direction):
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

        if position[0] + dy < 0 or position[1] + dx < 0 or position[0] + dy >= self.map_size[0] or position[1] >= self.map_size[1] + dx:
            return self.get_ready(character)

        self.map_data[position[0]][position[1] - 1] = 2

        return self.get_ready(character)

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
            return "cool","win",self.cool_item,self.hot_item
        elif self.hot_item > self.cool_item:
            return "hot","win",self.cool_item,self.hot_item
        else:
            return "","draw",self.cool_item,self.hot_item
