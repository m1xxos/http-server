# Uncomment this to pass the first stage
import socket
import re

HTTP_OK_MESSAGE = "HTTP/1.1 200 OK"
HTTP_NOT_FOUND = "HTTP/1.1 404 Not Found"
CRLF = "\r\n\r\n"


class Request:
    def __init__(self, conn: socket):
        self._conn = conn
        self.request_info, self.host, self.accept, self.user_agent = self.get_data()
        self.url = self.get_url()
        
    def get_data(self):
        host_re = "Host:.*"
        accept_re = "Accept:.*"
        user_agent_re = "User-Agent:.*"
        data = self._conn.recv(1024).decode()
        splitted_data = data.split("\r\n")
        
        _request = splitted_data[0] 
        _host = self.filer_type(splitted_data, host_re)
        _accept = self.filer_type(splitted_data, accept_re)
        _user_agent = self.filer_type(splitted_data, user_agent_re)
        return _request, _host, _accept, _user_agent
    
    def get_url(self):
        return self.request_info.split(" ")[1]

    def filer_type(self, data, pattern):
        return next(filter(None, [re.findall(pattern, _) for _ in data]))[0]

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
        conn, _ = server_socket.accept()  # wait for client
        with conn:
            new_request = Request(conn)
            response = HTTP_NOT_FOUND + CRLF
            if new_request.url == '/':
                response = HTTP_OK_MESSAGE + CRLF
            elif '/echo/' in new_request.url:
                echo_message = new_request.url.split('/echo/')[1]
                headers = f'Content-Type: text/plain\r\nContent-Length: {len(echo_message)}{CRLF}'
                response = f"{HTTP_OK_MESSAGE}\r\n{headers}{echo_message}{CRLF}"
            elif '/user-agent' in new_request.url:
                request_agent = new_request.user_agent
                headers = f'Content-Type: text/plain\r\nContent-Length: {len(request_agent)}{CRLF}'
                response = f"{HTTP_OK_MESSAGE}\r\n{headers}{request_agent}{CRLF}"
            print(response)
            conn.sendall(response.encode())
            conn.close()

if __name__ == "__main__":
    main()
