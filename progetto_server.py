import socket
import mysql.connector
import threading
import json
import ujson

HOST = socket.gethostbyname(socket.gethostname())
PORT = 50007
PASSWORD = "12345"
MAX_TENTATIVI = 3
DATABASE = 'ufficio_risorse_umane'

def password(conn_sql, conn, cur, lock):
    lock.acquire()
    tentativi = 0
    flag = False

    while tentativi<MAX_TENTATIVI:
        conn.send("Inserisci la password: ".encode())
        passw = conn.recv(1024).decode()
        print("Password: Tentativo N*", tentativi+1)

        if (PASSWORD == passw):
            conn.send("CORRETTA".encode())
            flag = True
            break
        else:
            conn.send("SBAGLIATA".encode())
            tentativi += 1

    if flag == False:
        print("Client uscito")
        conn.send("Password errata. Accesso negato".encode())
        conn.close()
    else:
        print("-------------------Client entrato nel DB-------------------")
        # switch_case
        switch_case(conn_sql, conn, cur)

    lock.release()


# controlla se una stringa contiene solamente numeri o no
def controllo_interi(stringa):
    try:
        if int(stringa) >= 0 or int(stringa) < 0:
            return "CORRETTO"
    except ValueError:
        return "SBAGLIATO"


def switch_case(conn, sock, cur):
    sock.send("Scegli fra:\n\t1. Creare\n\t2. Leggere\n\t3. Modificare\n\t4. Eliminare\n\t  : ".encode())
    risp = sock.recv(1024).decode()
    numero = int(risp)
    sock.send(str(numero).encode())

    print("Il client ha scelto l'opzione numero ", numero)
    # insert
    if numero == 1:
        inserire(conn, cur, sock)
    # select
    elif numero == 2:
        leggere(cur, sock)
    # update
    elif numero == 3:
        modificare(conn, cur, sock)
    # delete
    elif numero == 4:
        eliminare(conn, cur, sock)


# calcola i nomi delle tabelle del DB e le invia al client in una lista
def calcola_nomi_tabelle(cur, client_sock):
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = %s"
    cur.execute(query, (DATABASE, ))
    tabelle = cur.fetchall()

    lista_tabelle = []
    for tabella in tabelle:
        lista_tabelle.append(tabella[0])

    lista = json.dumps(lista_tabelle)
    client_sock.send(lista.encode())

    return lista_tabelle


# calcola i nomi degli attributi di una tabella
def calcola_attributi(cur, lista_tabelle, tabella_scelta):
    lista_attributi = []

    # se sceglie tutte e due le tabelle
    if lista_tabelle[0] in tabella_scelta and lista_tabelle[1] in tabella_scelta:
        query1 = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{lista_tabelle[0]}'"
        cur.execute(query1)
        lista1 = [row[0] for row in cur]

        query2 = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{lista_tabelle[1]}'"
        cur.execute(query2)
        lista2 = [row[0] for row in cur]
        
        lista_attributi.extend(lista1)
        lista_attributi.extend(lista2)

    # se sceglie una tabella
    else:
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{tabella_scelta}'"
        cur.execute(query)
        lista = [row[0] for row in cur]

        lista_attributi.extend(lista)
    

    return lista_attributi


# calcola i valori delgi ID di una tabella specificata e restituisce la lista
def calcola_primary_keys(cur, nome_tabella, id):
    query = f"SELECT {id} FROM {nome_tabella}"
    cur.execute(query)
    lista_id = [str(row[0]) for row in cur]

    return lista_id


# calcola il contenuto di tutta la tabella
def stampa_tabella(nome_tabella):
    query = f"SELECT * FROM {nome_tabella}"
    cur.execute(query)
    lista_tabella = cur.fetchall()

    # trasformo tutti gli elementi di 'lista_tabella' in stringhe
    new_lista_tabella = []
    for tupla in lista_tabella:
        new_tupla = ()
        for elem in tupla:
            new_elem = str(elem)
            new_tupla += (new_elem, )
        new_lista_tabella.append(new_tupla)

    return new_lista_tabella


def inserire(conn, cur, client_sock):
    client_sock.send("Su quale tabella vuoi operare? ".encode())
    lista_tabelle = calcola_nomi_tabelle(cur, client_sock)

    # ricevo la tabella scelta dall'utente
    tabella_scelta = client_sock.recv(1024).decode()
    print("tabella scelta: ", tabella_scelta)

    # lista attributi tabella/e scelta
    lista_attributi = calcola_attributi(cur, lista_tabelle, tabella_scelta)
    lista = json.dumps(lista_attributi)
    client_sock.send(lista.encode())

    # ricevo nulla
    nulla = client_sock.recv(1024)

    client_sock.send("---------INSERISCI---------".encode())

    # spedisco i valori delle PK di 'dipendenti_ali_ishtiaq'
    lista_PK_dipendenti = calcola_primary_keys(cur, lista_tabelle[0], 'id')
    lista_PK_dipendenti = [int(numero) for numero in lista_PK_dipendenti]
    lista = json.dumps(lista_PK_dipendenti)
    client_sock.send(lista.encode())

    # ricevo nulla
    nulla = client_sock.recv(1024)
    
    # spedisco i valori delle PK di 'zone_di_lavoro'
    lista_PK_zone = calcola_primary_keys(cur, lista_tabelle[1], 'id_zona')
    lista_PK_zone = [int(numero) for numero in lista_PK_zone]
    lista = json.dumps(lista_PK_zone)
    client_sock.send(lista.encode())

    # stampo il dizionario con attributo : inserimento utente
    lista = client_sock.recv(1024).decode()
    diz_inserimenti = json.loads(lista)
    print('Valori scelti: ', diz_inserimenti)

    # unisco gli attributi scelti in una stringa
    stringa_attr = ', '.join(lista_attributi)

    # unisco i valori scelti dal client in una stringa
    if tabella_scelta == lista_tabelle[0]:
        stringa_values = ', '.join([value if key=='id' else f"'{value}'" for key, value in diz_inserimenti.items()])
    else:
        stringa_values = ', '.join([f"'{value}'" if key=='nome_zona' or key=='citta' else value for key, value in diz_inserimenti.items()])

    # calcoli finali
    query_finale = f"INSERT INTO {tabella_scelta} ({stringa_attr}) VALUES ({stringa_values})"
    
    cur.execute(query_finale)
    conn.commit()


def leggere(cur, client_sock):
    # ['dipendenti_ali_ishtiaq', 'zone_di_lavoro']
    lista_tabelle = calcola_nomi_tabelle(cur, client_sock)
    client_sock.send(f"Scegli su quale tabella/e operare {lista_tabelle}: ".encode())

    # ricevo la tabella/e scelta dall'utente
    tabella_scelta = client_sock.recv(1024).decode()
    print("tabella/e scelte : ", tabella_scelta)

    # calcolo gli attributi della tabella/e scelte
    lista_attributi = calcola_attributi(cur, lista_tabelle, tabella_scelta)

    # spedisco la lista degli attributi al client
    lista = json.dumps(lista_attributi)
    client_sock.send(lista.encode())
    client_sock.send(f"Scegli i nomi degli attributi fra {lista_attributi}: ".encode())
    
    # ricevo la lista attributi scelti dall'utente
    lista = client_sock.recv(1024).decode()
    attributi_scelti = json.loads(lista)
    print("attributo/i scelti: ", attributi_scelti)

    # unisco tutti gli attributi in una stringa
    stringa_attributi = ', '.join(attributi_scelti)
    
    # calcoli finali
    query_finale = f"SELECT {stringa_attributi} FROM {tabella_scelta}"
    cur.execute(query_finale)
    lista_risultato = cur.fetchall()
    print(query_finale)

    risultato = json.dumps(lista_risultato)
    client_sock.send(risultato.encode())


def modificare(conn, cur, client_sock):
    # calcolo i nomi delle tabelle del DB
    lista_tabelle = calcola_nomi_tabelle(cur, client_sock)
    client_sock.send(f"Scegli su quale tabella operare {lista_tabelle}: ".encode())
    
    # ricevo la tabella scelta dall'utente
    tabella_scelta = client_sock.recv(1024).decode()
    print("Tabella scelta: ", tabella_scelta)

    # spedisco la lista dei dati contenuti nella tabella scelta
    lista_tabella = stampa_tabella(tabella_scelta)
    lista = ujson.dumps(lista_tabella)
    client_sock.send(lista.encode())

    # ricevo nulla
    nulla = client_sock.recv(1024).decode()

    # se sceglie 'dipendenti_ali_ishtiaq'
    if tabella_scelta == lista_tabelle[0]:
        id = 'id'
    # se sceglie 'zone_di_lavoro'
    else:
        id = 'id_zona'
    # calcolo e spedisco i valori delle PK
    lista_PK = calcola_primary_keys(cur, tabella_scelta, id)
    lista = json.dumps(lista_PK)
    client_sock.send(lista.encode())

    # faccio scegliere al client l'ID della riga da modificare
    client_sock.send("Scegli l'ID della riga da modificare ".encode())
    id_riga = client_sock.recv(1024).decode()
    print("Il client ha scelto l'ID ", id_riga)

    # calcolo gli attributi della tabelle scelta
    lista_attributi = calcola_attributi(cur, lista_tabelle, tabella_scelta)
    # rimuovo l'attributo ID dalla lista degli attributi
    lista_attributi.remove(id)
    # spedisco la lista degli attributi al client
    lista = json.dumps(lista_attributi)
    client_sock.send(lista.encode())

    client_sock.send(f"Scegli l'attributo da modificare fra {lista_attributi}: ".encode())
    # ricevo l'attributo da modificare
    attributo = client_sock.recv(1024).decode()
    print("attributo scelto : ", attributo)

    # faccio scegliere il nuovo valore dell'attributo
    client_sock.send("Inserisci il nuovo valore: ".encode())

    # spedisco la lista dei valori della PK id di 'dipendenti_ali_ishtiaq' se sceglie l'attributo 'id_dipendente'
    if attributo == 'id_dipendente':
        lista_id = calcola_primary_keys(cur, 'dipendenti_ali_ishtiaq', 'id')
        lista = json.dumps(lista_id)
        client_sock.send(lista.encode())

    # ricevo il nuovo valore dell'attributo scelto
    new_valore = client_sock.recv(1024).decode()
    print("nuovo valore :", new_valore)

    # calcoli finali
    query_finale = f"UPDATE {tabella_scelta} SET {attributo} = '{new_valore}' WHERE {id} = '{id_riga}'"
    print(query_finale)
    cur.execute(query_finale)
    conn.commit()


def eliminare(conn, cur, client_sock):
    # calcolo i nomi delle tabelle del DB
    lista_tabelle = calcola_nomi_tabelle(cur, client_sock)
    client_sock.send(f"Scegli su quale tabella operare {lista_tabelle}: ".encode())
    
    # ricevo la tabella scelta dall'utente
    tabella_scelta = client_sock.recv(1024).decode()
    print("Tabella scelta: ", tabella_scelta)

    # calcolo la lista delle PK
    if tabella_scelta == lista_tabelle[0]:
        id = 'id'
    else:
        id = 'id_zona'
    lista_PK = calcola_primary_keys(cur, tabella_scelta, id)

    # se la tabella è vuota spedisco "VUOTA"
    if len(lista_PK) == 0:
        client_sock.send("VUOTA".encode())
        print("La tabella è VUOTA")
    else:
        # spedisco la lista delle PK
        lista = json.dumps(lista_PK)
        client_sock.send(lista.encode())

        # calcolo e spedisco il contenuto di tutta la tabella
        contenuto_tabella = stampa_tabella(tabella_scelta)
        lista = ujson.dumps(contenuto_tabella)
        client_sock.send(lista.encode())

        # ricevo nulla
        nulla = client_sock.recv(1024)

        # faccio scegliere al client l'ID da eliminare
        client_sock.send(f"Quale ID vuoi eliminare: ".encode())

        # ricevo la PK scelta dal client
        PK_scelta = client_sock.recv(1024).decode()
        print('ID scelto : ', PK_scelta)

        # calcolo i valori nel campo 'id_dipendente' di 'zone_di_lavoro'
        query = "SELECT id_dipendente FROM zone_di_lavoro"
        cur.execute(query)
        lista_ID_dipendenti = [str(row[0]) for row in cur]

        if tabella_scelta == lista_tabelle[0] and PK_scelta in lista_ID_dipendenti:
            stringa = f"Impossibile eliminare ID '{PK_scelta}' poiché presente in 'zone_di_lavoro'"
            client_sock.send(stringa.encode())
            print(stringa)

        else:
            # calcoli finali
            query_finale = f"DELETE FROM {tabella_scelta} WHERE {id} = {PK_scelta}"
            cur.execute(query_finale)
            conn.commit()

            client_sock.send("Eliminazione effettuata con successo".encode())
            print(query_finale)

            # rimuovo il valore dell'ID scelto dal client
            lista_PK.remove(PK_scelta)
            
            # riordinazione degli ID
            if len(lista_PK) > 0:
                for i in range(len(lista_PK)):
                    query = f"UPDATE {tabella_scelta} SET {id} = '{i+1}' WHERE {id} = '{lista_PK[i]}'"
                    cur.execute(query)
                    conn.commit()


# MAIN
if __name__ == '__main__':

    # parte di SQL
    conn_sql = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        database=DATABASE,
        port=3306, 
        )

    cur = conn_sql.cursor()

    # parte dei SOCKET
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)
    print("Server in ascolto...")

    # parte dei THREAD
    thread = []
    i = 0
    lista_connessioni = []
    lock = threading.Lock()
    while True:
        lista_connessioni.append(s.accept())
        print("Connesso da ", lista_connessioni[i][1])
        thread.append(threading.Thread(target=password, args=(conn_sql, lista_connessioni[i][0], cur, lock, )))
        thread[i].start()
        i += 1