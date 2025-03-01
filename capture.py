import os
import csv
import socket
import mysql.connector

def store_csv(file_name, data):
    file_exists = os.path.exists(file_name) and os.path.getsize(file_name) > 0
    with open(file_name, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

def get_logs(thread_id,ip):
    logs = []
    data = {
        'THREAD_ID': '', 'QUERY_TIME': '',
        'SQL_TEXT': '', 'DATABASE': '',
        'ROWS_AFFECTED': '', 'ROWS_SENT': '',
        'ROWS_EXAMINED': '', 'IP': ip}
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="performance_schema" )
    cursor = conn.cursor()
    query = f"SELECT THREAD_ID, TIMER_WAIT, SQL_TEXT, CURRENT_SCHEMA, ROWS_AFFECTED, ROWS_SENT, ROWS_EXAMINED FROM performance_schema.events_statements_history_long WHERE THREAD_ID = '{thread_id}';"
    cursor.execute(query)
    result = cursor.fetchall()
    for log in result:
        for index,value in enumerate(log):
            clm = list(data.keys())[index]
            data[clm] = int(value) if str(value).isnumeric() else str(value)
            data[clm] = value
        data['QUERY_TIME'] = data['QUERY_TIME'] / 10 ** 9 
        logs.append(data.copy())
    store_csv('logs.csv', logs)
    print("Log file Updated!")
    cursor.close()
    conn.close()

def init_server():
    host = '0.0.0.0'
    port = 9999
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    return sock

def recv_message():
    server = init_server()
    client, addr = server.accept()
    packet = client.recv(1024).decode()
    thread_id,ip = packet.split('<seperator>')[-2].split(',')
    server.close()
    get_logs(thread_id,ip)

if __name__=="__main__":
    print('[!] Capturing Queries\n')
    while True:
        try:
            recv_message()
        except KeyboardInterrupt:
            print('\nAbort....')
            break
