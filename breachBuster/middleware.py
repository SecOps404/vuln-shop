import socket
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from time import sleep
from django.db import connection

class Monitor:
    BLOCKED_IPS = []
    def __init__(self, get_response):
        self.get_response = get_response

    
    def __call__(self, request):
        ip = self.get_client_ip(request)
        thread_id = self.get_thread_id()
        msg = thread_id + ',' + ip
        self.send_msg(msg)
        if ip in self.BLOCKED_IPS:
            return HttpResponseForbidden("<h1>You're Blocked</h1>")
        return self.get_response(request)

    def get_client_ip(self, request):
        """ Extracts IP address from request headers """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]  # Get first IP in case of multiple
        else:
            ip = request.META.get("REMOTE_ADDR")  # Direct IP if no proxy
        if not ip:
            ip = ''
        return str(ip)

    def get_thread_id(self):
        cursor = connection.cursor()
        qe = "SELECT THREAD_ID FROM performance_schema.threads WHERE PROCESSLIST_ID = CONNECTION_ID();"
        cursor.execute(qe)
        thread_id = cursor.fetchone()[0]
        return str(thread_id)

    def init_client(self):
        host = '127.0.0.1'
        port = 9999
    
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock

    def send_msg(self, msg):
        try:
            client = self.init_client()
            enc = ('<seperator>' + msg + '<seperator>').encode()
            client.send(enc)
            client.close()
        except Exception as e:
            print(e)
