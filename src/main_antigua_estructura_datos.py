class UserInteractions:

    def __init__(self, user_id):
        self.timestamps = []
        self.user_id = user_id
        self.user_hash = {user_id: self.timestamps}

    def __repr__(self):
        return str(self.user_hash)

class Item:
    def __init__(self,item_id):
        self.users_hash = {}
        self.item_id = item_id

    def add_user(self, user_id, timestamp):
        user_interaction = UserInteractions(user_id)
        user_interaction.timestamps.append(timestamp)
        self.users_hash[user_id] = user_interaction.timestamps

    def add_timestamp_existing_user(self, user_id, timestamp):
        self.users_hash[user_id].append(timestamp)

    def keys(self):
        return self.users_hash.keys()

    def items(self):
        return self.users_hash.items()

    def __repr__(self):
        return str(self.users_hash)


def print_result(data_hash):
    for k, v in data_hash.items():
        print(k, v)

def main():
    import time
    start = time.time()
    items = readFileGroupItem("entradas/US_NewYorkAggrTrain.txt")
    resultado = process_data_hash(items, 155520000)
    resultado_agrupado = process_data_counting_ocurrences_hash(items, 155520000)
    print(resultado_agrupado)
#print(process_data_counting_ocurrences_hash(items, 15552000))
    #temp = process_data_counting_ocurrences(items, 15552000)
    #result = get_first_K(temp, 2, 1)
    #print_result(result)
    #end = time.time()
    #print("TIEMPO: " + str(end - start))

def readFileGroupItem(txt_file):
    token = open(txt_file, "r")
    linestoken = token.readlines()
    items_map = {}

    for line in linestoken:
        print(line)
        item_id = str(line.split()[1])
        user_id = line.split()[0]
        timestamp = line.split()[3]
        if item_id not in items_map:
            item_iteration = Item(item_id)
            item_iteration.add_user(user_id, timestamp)
            items_map[item_id] = item_iteration
        else:
            if user_id not in items_map[item_id].keys():
                items_map[item_id].add_user(user_id, timestamp)
            else:
                items_map[item_id].add_timestamp_existing_user(user_id, timestamp)
    return items_map


def check_difference_in_array(array1, array2, maxDiff):
    counter = 0
    for element1 in array1:
        for element2 in array2:
            print('calculando diferencia ' + element1 + '-' + element2)
            diff = abs(int(element1) - int(element2))
            if diff < maxDiff:
                print('entra')
                counter += 1
    return counter

def process_data_hash(items_hash, maxDiff):
    users_hash = {}
    for item1_key, item1_value in items_hash.items():
        for user_id1, user1_array in item1_value.items():
            for user_id2, user2_array in item1_value.items():
                if user_id1 != user_id2:
                    print('comprobando ' + user_id1 + ' - ' +  user_id2)
                    counter = check_difference_in_array(user1_array, user2_array, maxDiff)
                    if counter != 0:
                        for i in range(counter):
                            add_or_append(users_hash, user_id1, user_id2)
    return users_hash

def process_data_counting_ocurrences_hash(items, maxDiff):
    basic_processed_hash = process_data_hash(items, maxDiff)
    for k, v in basic_processed_hash.items():
        temp = count_ocurrences(v)
        basic_processed_hash[k] = sort_dict_result(temp)
    return basic_processed_hash



def sort_dict_result(dict):
    from operator import itemgetter
    temp_sorted = sorted(dict.items(), key=itemgetter(1), reverse=True)
    return temp_sorted

def count_ocurrences(array):
    temp = {x: array.count(x) for x in set(array)}
    return temp


def get_first_K(data, K, only_name):
    for key, v in data.items():
        data[key] = get_only_name(v[:K]) if only_name else v[:K]
    return data

def get_only_name(data):
    result = []
    for x in data:
        result.append(x[0])
    return result

def readFile(txt_file):
    token = open(txt_file, "r")
    linestoken = token.readlines()
    items_objects = []
    for x in linestoken:
        items_objects.append(Item(x.split()[0], x.split()[1], x.split()[3]))
    token.close()
    return items_objects

def add_or_append(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = []
    dictionary[key].append(value)

def process_data_basic(items, maxDiff):
    users_hash = {}
    already_processed = []
    for item1 in items:
        user1 = item1.user_id
        for item2 in items:
            user2 = item2.user_id
            if (user1 != user2) and user2 not in already_processed and item1.item_id == item2.item_id:
                diff = abs(int(item1.timestamp) - int(item2.timestamp))
                if diff < maxDiff:
                    add_or_append(users_hash, user1, user2)
        already_processed.append(user1)
    return users_hash

def process_data_counting_ocurrences(items, maxDiff):
    basic_processed_hash = process_data_basic(items, maxDiff)
    for k, v in basic_processed_hash.items():
        temp = count_ocurrences(v)
        basic_processed_hash[k] = sort_dict_result(temp)
    return basic_processed_hash



if __name__ == '__main__':
    main()
