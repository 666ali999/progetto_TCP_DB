import socket
import json
import ujson
from datetime import datetime

HOST = socket.gethostbyname(socket.gethostname())
PORT = 50007

def password(s):
    while True:
        # "Inserisci la password: "
        data = s.recv(1024).decode()
        print(data, end='')

        password = input()
        s.send(password.encode())
        
        # "CORRETTA" o "SBAGLIATA"
        risp = s.recv(1024).decode()
        print(risp)

        if risp == "CORRETTA":
            break

    return risp


def switch_case(sock):
    scelta = sock.recv(1024).decode()
    print(scelta, end='')
    numero = input()
    # controlli sul numero
    while True:
        if numero.isdigit():
            numero = int(numero)
            if numero > 0 and numero <= 4:
                break
            else:
                numero = input("Reinserisci: ")
        else:
               numero = input("Reinserisci: ")

    sock.send(str(numero).encode())

    # 1, 2, 3, 4
    numero = int(sock.recv(1024).decode())

    if numero == 1:
        inserire(sock)
    # select
    elif numero == 2:
        leggere(sock)
    # update
    elif numero == 3:
        modificare(sock)
    # delete
    elif numero == 4:
        eliminare(sock)


# ['dipendenti_ali_ishtiaq', 'zone_di_lavoro']
def calcola_nomi_tabelle(s):
    lista = s.recv(1024).decode()
    lista_tabelle = json.loads(lista)

    return lista_tabelle


# funzione per controllare la validità di una data nel formato 'AAAA-MM-GG'
def controllo_data(data):
    try:
        datetime.strptime(data, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# controllo sulla tabella/e scelta
def controllo_tabelle(lista_tabelle, tabella_scelta):
    while True:
        # se sceglie tutte e due le tabelle
        if lista_tabelle[0] in tabella_scelta.split() and lista_tabelle[1] in tabella_scelta.split():
            tabella_scelta = lista_tabelle[0] + ' , ' + lista_tabelle[1]
            break
        # se sceglie una tabella
        elif lista_tabelle[0] in tabella_scelta.split() or lista_tabelle[1] in tabella_scelta.split():
            if(lista_tabelle[0] in tabella_scelta.split()):
                tabella_scelta = lista_tabelle[0]
            else:
                tabella_scelta = lista_tabelle[1]
            break
        else:
            tabella_scelta = input("Reinserisci: ")

    return tabella_scelta


def inserire(s):
    # "Su quale tabella vuoi operare? "
    risp = s.recv(1024).decode()
    print(risp, end='')

    # ['dipendenti_ali_ishtiaq', 'zone_di_lavoro']
    lista_tabelle = calcola_nomi_tabelle(s)
    print(lista_tabelle)

    tabella_scelta = input()
    while tabella_scelta not in lista_tabelle:
        tabella_scelta = input("Reinserisci: ")

    s.send(tabella_scelta.encode())

    # lista attributi tabella scelta
    lista = s.recv(1024).decode()
    lista_attributi = json.loads(lista)
    print(f"Attributi di {tabella_scelta} : {lista_attributi}")

    # spedisco nulla
    s.send('nulla'.encode())

    # "---------INSERISCI---------"
    risp = s.recv(1024).decode()
    print(risp)

    # ricevo la lista delle PK di 'dipendenti_ali_ishtiaq'
    lista = s.recv(1024).decode()
    lista_PK_dipendenti = json.loads(lista)
    lista_PK_dipendenti = sorted(lista_PK_dipendenti, reverse=True)

    # spedisco nulla
    s.send('nulla'.encode())

    # ricevo la lista delle PK di 'zone_di_lavoro'
    lista = s.recv(1024).decode()
    lista_PK_zone = json.loads(lista)
    lista_PK_zone = sorted(lista_PK_zone, reverse=True)

    # faccio inserire gli attributi all'utente
    diz_inserimenti = {}
    for attributo in lista_attributi:

        # controllo sulle primary keys
        if attributo == 'id':
            if len(lista_PK_dipendenti) == 0:
                dato = '1'
            else:
                dato = str(int(lista_PK_dipendenti[0]) + 1)
            print(f'id : {dato}')
        elif attributo == 'id_zona':
            if len(lista_PK_zone) == 0:
                dato = '1'
            else:
                dato = str(int(lista_PK_zone[0]) + 1)
            print(f'id_zona : {dato}')

        # controllo su 'id_dipendente'
        elif attributo == 'id_dipendente':
            print(f'{attributo} fra {sorted(lista_PK_dipendenti)} : ', end='')
            dato = input()
            if dato.lower() == 'null':
                dato = 'NULL'
            else:
                lista_PK_dipendenti = [str(numero) for numero in lista_PK_dipendenti]
                while dato not in lista_PK_dipendenti or not dato.isdigit(): 
                    dato = input("Reinserisci: ")

        else:
            dato = input(attributo + ' : ')

            # controllo su 'numero_clienti'
            if attributo == 'numero_clienti':
                while not dato.isdigit():
                    dato = input("Reinserisci: ")
            
            # controllo su 'data_assunzione'
            if attributo == 'data_assunzione':
                while not controllo_data(dato):
                    dato = input("Reinserisci nel formato [AAAA-MM-GG]: ")

        diz_inserimenti[attributo] = dato
    
    # spedisco il dizionario con attributo : valore inserito dall'utente
    lista = json.dumps(diz_inserimenti)
    s.send(lista.encode())


def leggere(s):
    lista_tabelle = calcola_nomi_tabelle(s)
    # "Scegli su quale tabella/e operare "
    risp = s.recv(1024).decode()
    print(risp, end=' ')
    tabella_scelta = input()

    # controllo sulla tabella scelta
    tabella_scelta = controllo_tabelle(lista_tabelle, tabella_scelta)
    
    s.send(tabella_scelta.encode())

    # "lista degli attributi"
    lista = s.recv(1024).decode()
    lista_attributi = json.loads(lista)

    # "Scegli i nomi degli attributi fra [[...]]: "
    risp = s.recv(1024).decode()
    print(risp, end='\n')
    print('------|QUIT per uscire|------')

    attributi_scelti = []
    contatore = 0
    while True:
        attributo = input()

        if attributo.lower() == 'quit':
            break
        elif(attributo not in lista_attributi) or (attributo in attributi_scelti):
            attributo = input("Reinserisci: ")
            if attributo.lower() == 'quit':
                break
    
        attributi_scelti.append(attributo)
        

    lista = json.dumps(attributi_scelti)
    s.send(lista.encode())

    # lista risultato della query finale
    risultato = s.recv(1024).decode()
    lista_risultato = json.loads(risultato)
    print('---------|RISULTATO|---------')
    print(lista_risultato)


def modificare(s):
    # ['dipendenti_ali_ishtiaq', 'zone_di_lavoro']
    lista_tabelle = calcola_nomi_tabelle(s)
    
    # "Scegli su quale tabella operare "
    risp = s.recv(1024).decode()
    print(risp, end=' ')
    tabella_scelta = input()

    # controllo e spedisco la tabella scelta
    tabella_scelta = controllo_tabelle(lista_tabelle, tabella_scelta)
    s.send(tabella_scelta.encode())

    # ricevo i dati della tabella scelta
    lista = s.recv(1024).decode()
    lista_tabella = ujson.loads(lista)
    print("--------------------Contenuto della tabella--------------------")
    for elem in lista_tabella:
        print(elem)
    print("---------------------------------------------------------------")

    # spedisco nulla
    s.send('nulla'.encode())

    # ricevo la lista dei valori della PK
    lista = s.recv(1024).decode()
    lista_PK = json.loads(lista)
    
    # "Scegli l'ID della riga da modificare "
    risp = s.recv(1024).decode()
    print(risp, end=f'fra {sorted(lista_PK)}: ')
    id_riga = input()
    while id_riga not in lista_PK:
        id_riga = input("Reinserisci: ")
    # spedisco l'ID scelto
    s.send(id_riga.encode())

    # ricevo la lista degli attributi
    lista = s.recv(1024).decode()
    lista_attributi = json.loads(lista)

    # "Scegli l'attributo da modificare fra ... "
    risp = s.recv(1024).decode()
    print(risp, end='')
    attributo = input()
    # controllo e spedisco l'attributo scelto
    while attributo not in lista_attributi:
        attributo = input("Reinserisci: ")

    s.send(attributo.encode())

    # "Nuovo valore = "
    risp = s.recv(1024).decode()
    print(risp, end='')

    # controllo se l'attributo scelto è numero_clienti
    if attributo == 'numero_clienti':
        new_valore = input()
        while not new_valore.isdigit():
            new_valore = input("Reinserisci un intero: ")
    
    # controllo se l'attributo scelto è 'data_assunzione'
    elif attributo == 'data_assunzione':
        new_valore = input()
        while not controllo_data(new_valore):
            new_valore = input("Reinserisci nel formato [AAAA-MM-GG]: ")

    # controllo se l'attributo scelto è 'id_dipendente'
    elif attributo == 'id_dipendente':
        # ricevo la lista degli id di 'dipendenti_ali_ishtiaq'
        lista = s.recv(1024).decode()
        lista_id = json.loads(lista)

        new_valore = input(f"fra {lista_id}: ")
        while new_valore not in lista_id:
            new_valore = input("Reinserisci: ")

    # faccio inserire un valore a tutti gli altri  
    else:
        new_valore = input()

    s.send(new_valore.encode())


def eliminare(s):
    # ['dipendenti_ali_ishtiaq', 'zone_di_lavoro']
    lista_tabelle = calcola_nomi_tabelle(s)
    
    # "Scegli su quale tabella operare "
    risp = s.recv(1024).decode()
    print(risp, end=' ')
    tabella_scelta = input()

    # controllo e spedisco la tabella scelta
    tabella_scelta = controllo_tabelle(lista_tabelle, tabella_scelta)
    s.send(tabella_scelta.encode())

    # se ricevo "VUOTA" significa che la tabella è vuota
    risp = s.recv(1024).decode()
    if risp == "VUOTA":
        print("La tabella è VUOTA")
    else:
        # ricevo la lista delle PK
        lista = risp
        lista_PK = json.loads(lista)

        # ricevo e stampo il contenuto di tutta la tabella
        print("--------------------Contenuto della tabella--------------------")
        lista = s.recv(1024).decode()
        contenuto_tabella = ujson.loads(lista)
        for elem in contenuto_tabella:
            print(elem)
        print("---------------------------------------------------------------")

        # spedisco nulla
        s.send("nulla".encode())

        # "Quale ID vuoi eliminare fra : "
        risp = s.recv(1024).decode()
        print(risp, end='')
        PK_scelta = input()

        # controllo su 'PK_scelta'
        while PK_scelta not in lista_PK:
            PK_scelta = input("Reinserisci: ")

        # spedisco 'PK_scelta' al server
        s.send(PK_scelta.encode())

        # ricevo la risposta finale
        risp = s.recv(1024).decode()
        print(risp)


# MAIN
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    risp = password(s)
    if risp == "SBAGLIATA":
        # "Password errata. Accesso negato"
        data = s.recv(1024).decode()
        print(data)
        s.close()
    else:
        switch_case(s)
        
        s.close()