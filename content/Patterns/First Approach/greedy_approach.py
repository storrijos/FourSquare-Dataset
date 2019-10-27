#Import
import os, sys
curent_file_abs_path = os.path.abspath(__file__)
current_dir = os.path.dirname(curent_file_abs_path) + "/../../Processing"
carpeta2_abs_path = os.path.abspath(current_dir)
sys.path.insert(0,carpeta2_abs_path)
from pre_process import ProcessData

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

def process_and_get_K_first():
    import time
    start = time.time()
    items = ProcessData.readFileGroupItem("entradas/entrada_corta.txt")
    temp = process_data_counting_ocurrences_hash(items, 15552000)
    result = get_first_K(temp, 2, 1)
    print_result(result)
    end = time.time()
    print("TIEMPO: " + str(end - start))

def process_and_get_accurate_timestamp(items, timestamp):
    import time
    start = time.time()
    print('Timestamp: ' + str(timestamp))
    temp = count_number_of_elements(items, timestamp)
    with open("salidas/salida_timestamps_5_horas.txt", "a") as text_file:
        text_file.write('TIMESTAMP: ' + str(timestamp) + '\n')
        text_file.write(str(temp) + '\n')
    end = time.time()
    print("TIEMPO: " + str(end - start))

def main():
    hour_seconds = 1
    max_hour = 10
    items = ProcessData.readFileGroupItem("entradas/entrada_corta.txt")
    for time_loop in range(hour_seconds, hour_seconds * max_hour, hour_seconds):
        process_and_get_accurate_timestamp(items, time_loop)

def add_or_append(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = []
    dictionary[key].append(value)

def check_difference_in_array(array1, array2, maxDiff):
    counter = 0
    for element1 in array1:
        for element2 in array2:
            diff = abs(int(element1) - int(element2))
            if diff < maxDiff:
                counter += 1
    return counter

def process_data_hash(items_hash, maxDiff):
    users_hash = {}
    for item1_key, item1_value in items_hash.items():
        for user_id1, user1_array in item1_value.items():
            for user_id2, user2_array in item1_value.items():
                if user_id1 != user_id2:
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

def count_number_of_elements(items, maxDiff):
    basic_processed_hash = process_data_hash(items, maxDiff)
    total_count = 0
    items = basic_processed_hash.items()
    items_lenght = len(items)
    for k, v in items:
        total_count += len(v)

    if items_lenght != 0:
        total_count = float(total_count)/float(items_lenght)
    return total_count

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

if __name__ == '__main__':
    main()
