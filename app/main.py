import argparse
import socket
import re
import threading
from pathlib import Path


HTTP_OK_MESSAGE = "HTTP/1.1 200 OK"
HTTP_NOT_FOUND = "HTTP/1.1 404 Not Found"
HTTP_CREATED = "HTTP/1.1 201 Created"

CRLF = "\r\n\r\n"


class Request:
    def __init__(self, conn: socket.socket):
        """Create new Request instance"""
        self._conn = conn
        self.request_info, self.host, self.accept, self.user_agent, self.content_type, \
            self.body = self.get_data()
        self.method, self.url, _ = self.get_request_info()

    def get_data(self):
        """Split incoming request to variables"""
        host_re = "Host:.*"
        accept_re = "Accept:.*"
        user_agent_re = "User-Agent:.*"
        content_type_re = "Content-Type:.*"
        data = self._recv_all()
        if not data:
            return "", "", "", ""
        splitted_data = data.split("\r\n")
        _request = splitted_data[0] if splitted_data else ""
        _host = self.filer_type(splitted_data, host_re)
        _accept = self.filer_type(splitted_data, accept_re)
        _user_agent = self.filer_type(splitted_data, user_agent_re)
        _user_agent = _user_agent.split(" ")[1] if _user_agent else ""
        _content_type = self.filer_type(splitted_data, content_type_re)
        _content_type = _content_type.split(" ")[1] if _content_type else ""
        # print(_content_type)
        _body = splitted_data[-1] if splitted_data else ""
        return _request, _host, _accept, _user_agent, _content_type, _body

    def get_request_info(self):
        return self.request_info.split(" ") if self.request_info else ""

    def filer_type(self, data, pattern):
        finder = next(filter(None, [re.findall(pattern, _) for _ in data]), "")
        return finder[0] if finder else ""

    def _recv_all(self, buffer_size=1024):
        data = b''
        while True:
            part = self._conn.recv(buffer_size)
            data += part
            if len(part) < buffer_size:
                break
        return data.decode()

def read_file(file_path):
    try:
        return Path(file_path).read_text(encoding='utf-8')
    except FileNotFoundError:
        return f"Файл '{file_path}' не найден."
    except Exception as e:
        return f"Ошибка при чтении файла: {e}"

def write_file(file_path, content):
    try:
        with file_path.open('wb') as file:
            file.write(content.encode("utf-8"))
        return True
    except Exception as e:
        print(f"Ошибка при записи файла: {e}")
        return False

def receive_connection(conn: socket.socket, file_folder):
    new_request = Request(conn)
    response = HTTP_NOT_FOUND + CRLF

    if new_request.url == '/':
        response = HTTP_OK_MESSAGE + CRLF
    elif new_request.url.startswith('/echo/'):
        echo_message = new_request.url[len('/echo/'):]
        headers = f'Content-Type: text/plain\r\nContent-Length: {len(echo_message)}{CRLF}'
        response = f"{HTTP_OK_MESSAGE}\r\n{headers}{echo_message}{CRLF}"
    elif new_request.url.startswith('/user-agent'):
        request_agent = new_request.user_agent
        headers = f'Content-Type: text/plain\r\nContent-Length: {len(request_agent)}{CRLF}'
        response = f"{HTTP_OK_MESSAGE}\r\n{headers}{request_agent}{CRLF}"
    elif new_request.url.startswith('/files/'):
        file_folder = Path(file_folder)
        file_name = new_request.url[len('/files/'):]
        file_path = file_folder / file_name
        if (new_request.method == "POST") & (new_request.content_type == "application/octet-stream"):
            write_file(file_path, new_request.body)
            response = f"{HTTP_CREATED}{CRLF}"
        elif file_path.is_file():
            file_content = read_file(file_path)
            headers = f'Content-Type: application/octet-stream\r\nContent-Length: {file_path.stat().st_size}{CRLF}'
            response = f"{HTTP_OK_MESSAGE}\r\n{headers}{file_content}{CRLF}"

    print(response)
    conn.sendall(response.encode())
    # CodeCrafters fix
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="HTTP сервер")
    parser.add_argument("--directory", default="/tmp/", help="Папка с файлами")
    args = parser.parse_args()
    file_folder = args.directory

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
        while True:
            conn, _ = server_socket.accept()  # wait for client
            thread = threading.Thread(target=receive_connection, args=(conn,file_folder,))
            thread.start() # test

if __name__ == "__main__":
    main()
