#!/usr/bin/python3

from time import sleep
import mysql.connector
import pprint
import threading
import tkinter as tk
import sys

class MainWindow:
    def __init__(self, main) -> None:
        self.main = main
        self.main['bg'] = '#909090'
        self.lightColor = '#909090'
        self.threadRunning = True
        self.pricePerSec = 0.5
        self.seasonPricePerSec = 0.2
        self.main.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.main.geometry("600x300")
        self.userButton      = tk.Button(self.main, text ="Ticket", command = self.user)
        self.sUserButton     = tk.Button(self.main, text ="Dauer Ticket", command = self.seasonUser)
        self.removeButton    = tk.Button(self.main, text ="Ende Ticket", command = self.removeUser)
        self.plate           = tk.Label (self.main, text='Nummernschild')
        self.plateEntry      = tk.Entry (self.main)
        self.space           = tk.Label (self.main, text='Parkplatznummer')
        self.spaceEntry      = tk.Entry (self.main)
        self.freeSpaces      = tk.Label (self.main, text='')
        self.sFreeSpaces     = tk.Label (self.main, text='')
        self.price           = tk.Label (self.main, text='')

        self.sFreeSpaces.pack()
        self.freeSpaces.pack()
        self.space.place(x=10, y=10)
        self.spaceEntry.place(x=8, y=40)
        self.plate.place(x=10, y=70)
        self.plateEntry.place(x=8, y=100)
        self.userButton.place(x=8, y=130)
        self.sUserButton.place(x=87, y=130)
        self.removeButton.place(x=8, y=160)
        self.price.pack()

        self.sFreeSpaces['bg'] = self.lightColor
        self.freeSpaces['bg'] = self.lightColor
        self.space['bg'] = self.lightColor
        self.spaceEntry['bg'] = self.lightColor
        self.plate['bg'] = self.lightColor
        self.plateEntry['bg'] = self.lightColor
        self.userButton['bg'] = self.lightColor
        self.sUserButton['bg'] = self.lightColor
        self.removeButton['bg'] = self.lightColor
        self.price['bg'] = self.lightColor
    
        self.dataBase: mysql = mysql.connector.connect(
            host     = "localhost",
            user     = "debian-sys-maint",
            password = "SUPtwQgI1bbIrSPv"
        )

        self.cursor = self.dataBase.cursor(dictionary=True)
        self.cursor.execute("use carpark;")
        self.threadCursor = self.dataBase.cursor(dictionary=True)
        self.threadCursor.execute("use carpark;")

        self.countUnocc = "select count(*) as unoccupied from space where occupied = 'n' and seasonticket = 'n';"
        self.countSeasonUnocc = "select count(*) as unoccupied from space where occupied = 'n' and seasonticket = 'j';"

        self.thread = threading.Thread(target=self.refresh)
        self.thread.start()

    def refresh(self):
        while(self.threadRunning):
            self.threadCursor.execute( self.countUnocc )
            self.freeSpaces['text'] = "Verfügbare Parkplätze: " + str(self.threadCursor.fetchall()[0]['unoccupied'])
            self.freeSpaces.pack()
            self.threadCursor.execute( self.countSeasonUnocc )
            self.sFreeSpaces['text'] = "Verfügbare Dauerparkplätze: " + str(self.threadCursor.fetchall()[0]['unoccupied'])
            self.sFreeSpaces.pack()
            sleep( 1 )

    def user(self):
        plate = self.plateEntry.get()
        space_id: int = int(self.spaceEntry.get())
        self.cursor.execute( self.countUnocc )
        countUnocc: int = int(self.cursor.fetchall()[0]['unoccupied'])

        self.cursor.execute(f"select user_id, seasonticket from user where plate = '{plate}'")
        data = self.cursor.fetchall()
        plateExist: int = len(data)
        seasonticket: str
        if plateExist == 1:
            seasonticket = data[0]['seasonticket']

        self.cursor.execute(f"select occupied from space where space_id = '{space_id}'")
        occupied: str = self.cursor.fetchall()[0]['occupied']

        if occupied == 'n' and len(plate) > 0 and countUnocc > 4 and space_id > 40 and space_id <= 180:
            if plateExist == 0:
                self.cursor.execute(f"insert into user values (null, '{plate}', 'n', now(), null, null);")
            elif plateExist == 1 and seasonticket == 'j':
                return
            elif plateExist == 1:
                self.cursor.execute(f"update user set entrydate = now() where plate = '{plate}';")

            self.dataBase.commit()

            self.cursor.execute(f"select user_id from user where plate = '{plate}'")
            user_id: int = self.cursor.fetchall()[0]['user_id']

            self.cursor.execute(f"update space set occupied = 'j', user_id = {user_id} where space_id = {space_id};")
            self.dataBase.commit()

    def seasonUser(self):
        plate = self.plateEntry.get()
        space_id: int = int(self.spaceEntry.get())
        self.cursor.execute( self.countUnocc )
        countUnocc: int = int(self.cursor.fetchall()[0]['unoccupied'])

        self.cursor.execute( self.countSeasonUnocc )
        countSeasonUnocc: int = int(self.cursor.fetchall()[0]['unoccupied'])

        self.cursor.execute(f"select user_id, seasonticket from user where plate = '{plate}'")
        data = self.cursor.fetchall()
        plateExist: int = len(data)
        seasonticket: str
        if plateExist == 1:
            seasonticket = data[0]['seasonticket']

        self.cursor.execute(f"select occupied from space where space_id = '{space_id}'")
        occupied: str = self.cursor.fetchall()[0]['occupied']

        if occupied == 'n' and len(plate) > 0 and space_id > 0 and space_id <= 180 \
            and ((countUnocc <= 4 
            and countSeasonUnocc > 0 
            and space_id > 0 
            and space_id <= 40)
            or (countUnocc > 4)):
                if plateExist == 0:
                    self.cursor.execute(f"insert into user values (null, '{plate}', 'j', now(), null, 0);")
                elif plateExist == 1 and seasonticket == 'n':
                    return    
                elif plateExist == 1:
                    self.cursor.execute(f"update user set entrydate = now() where plate = '{plate}';")
                
                self.dataBase.commit()

                self.cursor.execute(f"select user_id from user where plate = '{plate}'")
                user_id: int = self.cursor.fetchall()[0]['user_id']

                self.cursor.execute(f"update space set occupied = 'j', user_id = {user_id} where space_id = {space_id};")
                self.dataBase.commit()

    def removeUser(self):
        plate = self.plateEntry.get()
        self.cursor.execute(f"select user_id from user where plate = '{plate}'")
        plateExist: int = len(self.cursor.fetchall())

        if len(plate) > 0 and plateExist == 1:
            self.cursor.execute(f"update user set leavedate = now() where plate = '{plate}'")
            self.dataBase.commit()

            self.cursor.execute(f"select seasonticket from user where plate = '{plate}'")
            seasonticket = self.cursor.fetchall()[0]['seasonticket']
            sleep(0.5)
            self.cursor.execute(f"select (leavedate - entrydate) as time from user where plate = '{plate}';")
            seconds: int = int(self.cursor.fetchall()[0]['time'])
            print(seconds)
            sys.stdout.flush()
            if seasonticket == 'n':
                pricePerSec = seconds * self.pricePerSec
                self.price['text'] = "Ticketpreis: " + str(round(pricePerSec, 2)) + "€"
            elif seasonticket == 'j':
                self.cursor.execute(f"update user set totaltime = totaltime + {seconds} where plate = '{plate}';")
                self.dataBase.commit()
                pricePerSec = seconds * self.seasonPricePerSec
                self.price['text'] = "Dauerticketpreis: " + str(round(pricePerSec, 2)) + "€"

            self.cursor.execute(f"update space set occupied = 'n', user_id = null where user_id in ( select user_id from user where plate = '{plate}');")
            self.dataBase.commit()

            #self.cursor.execute(f"delete from user where plate = '{plate}' and seasonticket = 'n';")
            #self.dataBase.commit()

    def on_closing(self):
        self.threadRunning = False
        self.dataBase.close()
        self.main.destroy()

if __name__ == '__main__':
    main = tk.Tk()
    mainWindow = MainWindow( main )
    main.mainloop()