import paho.mqtt.client as mqtt
import sqlite3
import time
import tkinter
import os
from datetime import datetime

# Nazwa lub ip brokera
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# Klient MQTT
client = mqtt.Client()

# Główne okno
window = tkinter.Tk()

# Słownik kart i pracowników
card=dict()
employee=dict()

def create_main_window():

    #stworzenie okna

    window.geometry("250x100")
    window.title("SERVER")
    label = tkinter.Label(window, text="Listening to the MQTT")
    exit_button = tkinter.Button(window, text="Stop", command=window.quit)

    label.pack()
    exit_button.pack(side="right")


def add_RFID(employee_id, card_id):

    # dodanie karty pracownikowi

    global card
    global employee

    if(isinstance(card_id, int)):
        card_id=str(card_id)

    if(isinstance(employee_id, int)):
        employee_id = str(employee_id)

    if(employee_id in employee and card_id in card):
        if(employee[employee_id][0] == "-1" and card[card_id][0] == "-1"):
            employee[employee_id][0] = card_id
            card[card_id][0] = employee_id
            return True

    return False

def remove_RFID(employee_id):

    #usuniecie karty pracownikowi

    global card
    global employee

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

    return False

def worktime_report(employee_id):

    # Generowanie raportu czasu pracy dla podanego pracownika wg jego id

    if (isinstance(employee_id, int)):
        employee_id = str(employee_id)

    connection = sqlite3.connect("log.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM employee_log WHERE employee_id=?", (employee_id,))

    rows = cursor.fetchall()

    worktime=None

    if len(rows)>0:
        is_in= False
        worktime=datetime.strptime(rows[0][0], '%a %b %d %H:%M:%S %Y') - datetime.strptime(rows[0][0], '%a %b %d %H:%M:%S %Y')
        acc_worktime=None
        swapper=None

        for row in rows:
            swapper = datetime.strptime(row[0], '%a %b %d %H:%M:%S %Y')

            if is_in:
                acc_worktime=swapper - acc_worktime
                worktime=worktime + acc_worktime
                is_in=False
            else:
                acc_worktime=swapper
                is_in=True
    else:
        worktime="0:00:00"

    connection.close()

    return worktime

def save_worktime_to_database():

    # Zapisanie czasu pracy wszystkich pracowników do bazy danych "worktime.db"

    connection = sqlite3.connect("worktime.db")
    cursor=connection.cursor()

    for i in range(0,len(employee)):
        employee_id=str(i+1)
        worktime=str(worktime_report(employee_id))
        employee_name=employee[employee_id][1]+" "+employee[employee_id][2]
        cursor.execute("INSERT OR REPLACE INTO whole_work_time VALUES (?,?,?)", (worktime, employee_id, employee_name) )
        connection.commit()

    connection.close()

def load_data_from_database(file_name):

    #wczytanie danych z pliku

    #kolejność danych w pracownicy.txt:
    #emp_id, card_id, imie, nazwisko

    #kolejność danych w karty.txt:
    #card_id, emp_id

    curr_data = dict()
    file = open(file_name, "r")

    for line in file:
        temp = line.rstrip('\r\n').split(";")
        id = temp[0]
        curr_data[id] = temp[1:]

    return curr_data

def save_data_to_database(file_name, curr_data):

    #zapis danych do pliku

    #kolejności takie same jak przy wczytywaniu

    line=""
    file = open(file_name, "w+")
    for key, values in curr_data.items():
        line += (key+";")
        line += ";".join(values)
        file.write(line)
        file.write("\n")
        line=""

def save_all_data_to_database(employee_file_name, card_file_name):

    #zapis kart i pracowników

    global card
    global employee

    save_data_to_database(employee_file_name, employee)
    save_data_to_database(card_file_name, card)

def connect_to_database():

    # Sprawdzenie czy baza danych istnieje, a jak nie istnieje to jej utworzenie

    if not os.path.exists("log.db"):
        connection = sqlite3.connect("log.db")
        cursor = connection.cursor()
        cursor.execute(""" CREATE TABLE card_log (
            log_time text,
            card text,
            terminal_id text
        )""")
        connection.commit()
        cursor.execute(""" CREATE TABLE employee_log (
            log_time text,
            employee_id text,
            employee text,
            terminal_id text
        )""")
        connection.commit()

        connection.close()
        print("The new log.db database created.")

    if not os.path.exists("worktime.db"):
        connection = sqlite3.connect("worktime.db")
        cursor = connection.cursor()
        cursor.execute(""" CREATE TABLE whole_work_time (
            worktime text,
            employee_id text,
            employee text
        )""")
        connection.commit()

        connection.close()
        print("The new worktime.db database created.")

def process_message(client, userdata, message):

    # Obsługa wiadomości po jej dotarciu

    # Dekodowanie wiadomości
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")

    global card
    global employee

    if message_decoded[0] != "Client connected" and message_decoded[0] != "Client disconnected":
        card_id = message_decoded[0]
        terminal_id = message_decoded[1]
        curr_time = time.ctime()

        print(curr_time + ", Card: " + card_id + " used at terminal: " + terminal_id)

        connention = sqlite3.connect("log.db")
        cursor = connention.cursor()

        if card_id in card:
            if card[card_id][0]!="-1":
                employee_id=card[card_id][0]
                employee_name=employee[employee_id][1]+" "+employee[employee_id][2]

                # Save to sqlite database
                cursor.execute("INSERT INTO employee_log VALUES (?,?,?,?)", (curr_time, employee_id, employee_name, terminal_id))
                connention.commit()

        cursor.execute("INSERT INTO card_log VALUES (?,?,?)", (curr_time, card_id, terminal_id))
        connention.commit()
        connention.close()

    else:
        print(message_decoded[0] + " : " + message_decoded[1])


def connect_to_broker():

    # Ustanowienie połączenia z brokerem

    # Połącz z brokerem
    client.connect(broker)
    # Wyślij wiadomość o połączeniu
    client.on_message = process_message
    # Uruchom klienta i subskrybcję
    client.loop_start()
    client.subscribe("Card")

def disconnect_from_broker():

    # Rozłączenie z brokerem

    client.loop_stop()
    client.disconnect()

#######################
## STARUP # SHUTDOWN ##
#######################

def start_Up(employee_file, card_file):
    connect_to_database()

    global employee
    global card

    employee = load_data_from_database(employee_file)
    card = load_data_from_database(card_file)

def shut_Down(employee_file, card_file):
    save_all_data_to_database(employee_file, card_file)
    save_worktime_to_database()
    disconnect_from_broker()

##################
##  MAIN LOOP   ##
##################

def main_loop():
    connect_to_broker()
    create_main_window()
    window.mainloop()

##################
##     MAIN     ##
##################

if __name__ == "__main__":
    card_file_name="karty.txt"
    employee_file_name="pracownicy.txt"

    start_Up(employee_file_name, card_file_name)

    #print(add_RFID(data[0], data[1], 2, 3))
    #print(remove_RFID(data[0], data[1], 3))

    main_loop()
    shut_Down(employee_file_name, card_file_name)
