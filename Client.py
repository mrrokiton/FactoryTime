#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import tkinter

# ID terminala domyślnie T0
terminal_id = "T0"
# Nazwa lub IP brokera
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# Klient MQTT
client = mqtt.Client()

# Główne okno symulujące przyłożenie karty RIFD
window = tkinter.Tk()

def call_card(card_id):

    # Wyślij dane o karcie

    client.publish("Card", card_id + "." + terminal_id,)


def create_main_window():

    # Utworzenie okna do symulacji

    window.geometry("300x200")
    window.title("SENDER " + terminal_id)

    intro_label = tkinter.Label(window, text="Select Card:")
    intro_label.grid(row=0, columnspan=5)

    button_1 = tkinter.Button(window, text="Card 1",
                              command=lambda: call_card("1"))
    button_1.grid(row=1, column=0)
    button_2 = tkinter.Button(window, text="Card 2",
                              command=lambda: call_card("2"))
    button_2.grid(row=2, column=0)
    button_3 = tkinter.Button(window, text="Card 3",
                              command=lambda: call_card("3"))
    button_3.grid(row=3, column=0)
    button_4 = tkinter.Button(window, text="Card 4",
                              command=lambda: call_card("4"))
    button_4.grid(row=1, column=1)
    button_5 = tkinter.Button(window, text="Card 5",
                              command=lambda: call_card("5"))
    button_5.grid(row=2, column=1)
    button_6 = tkinter.Button(window, text="Card 6",
                              command=lambda: call_card("6"))
    button_6.grid(row=3, column=1)
    button_stop = tkinter.Button(window, text="Stop", command=window.quit)
    button_stop.grid(row=4, columnspan=2)


def connect_to_broker():

    # Stwórz połączenie z brokerem

    # Połącz z brokerem
    client.connect(broker)
    # Wyślij wiadomość o połączeniu
    call_card("Client connected")


def disconnect_from_broker():

    # Rozłącz z brokerem

    # Wyślij wiadmość o rozłączeniu
    call_card("Client disconnected")
    # Rozłącz klienta
    client.disconnect()


def run_sender():

    # Uruchom klienta

    connect_to_broker()
    create_main_window()

    window.mainloop()

    disconnect_from_broker()


if __name__ == "__main__":
    terminal_id = input('Prompt String: ')
    run_sender()
