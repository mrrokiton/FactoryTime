import time
import keyboard

def add_RFID(employee, card, employee_id, card_id):
    if(isinstance(card_id, int)):
        card_id=str(card_id)
    if(isinstance(employee_id, int)):
        employee_id = str(employee_id)
    if(employee_id in employee and card_id in card):
        if(employee[employee_id][0] == "-1" or card[card_id][0] == "-1"):
            return False
        else:
            employee[employee_id][0] = card_id
            card[card_id][0] = employee_id
            return True
    else:
        return False

def remove_RFID(employee, card, employee_id):
    if(isinstance(employee_id, int)):
        employee_id = str(employee_id)
    card_id = employee[employee_id][0]
    if(isinstance(card_id, int)):
        card_id = str(card_id)
    if(employee_id in employee):
        if(employee[employee_id][0] == "-1"):
            return True
        else:
            employee[employee_id][0] = "-1"
            card[card_id][0] = "-1"
            return True
    else:
        return False

def time_to_add(card, card_id):
    if(isinstance(card_id, int)):
        card_id=str(card_id)
    print("kolejne wejscie tego dnia karty "+card_id +", stare godziny wejscia to: " +str(card[card_id][1])+":"+str(card[card_id][2])+" "+str(card[card_id][3])+":"+str(card[card_id][4]))
    card[card_id][5]= work_time(card, card_id)[0]
    card[card_id][6] = work_time(card, card_id)[1]
    card[card_id][1]="-1"
    card[card_id][2]="-1"
    card[card_id][3]="-1"
    card[card_id][4]="-1"


def register_card(card, card_id):
    if(isinstance(card_id, int)):
        card_id=str(card_id)
    if(card[card_id][1]=="-1"):
        entry_time(card, card_id)
    else:
        if(card[card_id][3]=="-1"):
            leave_time(card,card_id)
        else:
            time_to_add(card, card_id)
            entry_time(card, card_id)

def entry_time(card, card_id):
    czas=time.localtime()
    if(isinstance(card_id, int)):
        card_id = str(card_id)
    print("zarejestrowano wejscie karty <" + card_id + "> o godzinie " + str(czas.tm_hour) + ":" + str(czas.tm_min))
    card[card_id][1]=str(czas.tm_hour)
    card[card_id][2]=str(czas.tm_min)

def leave_time(card, card_id):
    czas=time.localtime()
    if(isinstance(card_id, int)):
        card_id = str(card_id)
    print("zarejestrowano wyjscie karty <" + card_id + "> o godzinie " + str(czas.tm_hour) + ":" + str(czas.tm_min))
    card[card_id][3]=str(czas.tm_hour)
    card[card_id][4]=str(czas.tm_min)

def work_time_all(card):
    for i in card:
        work_time(card, i)

def work_time(card, card_id):
    if(isinstance(card_id, int)):
        card_id = str(card_id)
    result_hour=0
    result_min=0
    if(card[card_id][1]!="-1" and card[card_id][3]!="-1"):
        entry_hour = int(card[card_id][1])
        entry_min = int(card[card_id][2])
        leave_hour = int(card[card_id][3])
        leave_min = int(card[card_id][4])
        hour_to_add = int(card[card_id][5])
        min_to_add = int(card[card_id][6])

        if(entry_min>leave_min):
            entry_hour+=1
            result_min=60-entry_min+leave_min+min_to_add
            if(entry_hour>leave_hour):
                result_hour=24-entry_hour+leave_hour+hour_to_add
            else:
                result_hour=leave_hour-entry_hour+hour_to_add
        else:
            result_min=leave_min-entry_min+min_to_add
            if(entry_hour>leave_hour):
                result_hour = 24 - entry_hour + leave_hour+hour_to_add
            else:
                result_hour = leave_hour - entry_hour+hour_to_add
    else:
        return (card[card_id][5], card[card_id][6])

    if(result_min>59):
        result_hour+=1
        result_min-=60

    return (str(result_hour), str(result_min))

def print_time_raport(employee, card):
    print("======================================================")
    print("Raport czasu pracy:\n")
    for i in employee:
        worktime = ("0", "0")
        card_id = employee[i][0]
        if(card_id != "-1"):
            worktime=work_time(card, card_id)
        print(employee[i][1] + " " + employee[i][2] + ": " + worktime[0] + "h " + worktime[1] + "min")
    print("======================================================")


def load_data_from_database(file_name):
    #kolejność danych w pracownicy.txt: emp_id, card_id, imie, nazwisko
    #kolejność danych w dane.txt: card_id, emp_id, wejscie_godzina, wejscie_minuta, wyjscie_godzina, wyjscie_minuta, godziny pracy, minuty pracy

    data_dictionary = dict()
    file = open(file_name, "r")

    for line in file:
        temp = line.rstrip('\r\n').split(";")
        id = temp[0]
        data_dictionary[id] = temp[1:]


    return data_dictionary

def save_data_to_database(file_name, data):
    line=""
    file = open(file_name, "w+")
    for key, values in data.items():
        line += (key+";")
        line += ";".join(values)
        file.write(line)
        file.write("\n")
        line=""

def save_all_data_to_database(employee_file_name, card_file_name, data):
    save_data_to_database(employee_file_name, data[0])
    save_data_to_database(card_file_name, data[1])

def startUp(employee_file, card_file):
    employee = load_data_from_database(employee_file)
    card = load_data_from_database(card_file)

    return (employee, card)

def shutDown(employee_file, card_file, data):
    save_all_data_to_database(employee_file_name, card_file_name, data)

    employee=data[0]
    card=data[1]

    print_time_raport(employee, card)

def loop(data):
    employee = data[0]
    card = data[1]
    key=None

    print("sprawdzanie dzialania:")
    print("q-wyjdz")
    print("p-pokaz raport pracy")
    print("1-zeskanuj krate o id <1>")

    while(key!='q'):
        key = ""
        key=keyboard.read_key()
        time.sleep(1)
        if(key=='p'):
            print_time_raport(employee, card)
        if(key=='1'):
            register_card(card, 1)




if __name__ == "__main__":
    card_file_name="karty.txt"
    employee_file_name="pracownicy.txt"
    data = startUp(employee_file_name, card_file_name)

    #print(add_RFID(data[0], data[1], 2, 3))
    #print(remove_RFID(data[0], data[1], 3))

    loop(data)

    shutDown(employee_file_name, card_file_name, data)




