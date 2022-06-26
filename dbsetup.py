import mysql.connector

dataBase: mysql = mysql.connector.connect(
host     = "localhost",
user     = "debian-sys-maint",
password = "SUPtwQgI1bbIrSPv"
)

cursor = dataBase.cursor(dictionary=True)
cursor.execute("use carpark;")

seasonticket = 'j'
for i in range(1,181):
    if(i > 40): 
        seasonticket = 'n'
    cursor.execute(f"insert into space values ({i}, null, 'n', '{seasonticket}');")


dataBase.commit()
dataBase.close()