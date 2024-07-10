import argparse
import socket
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
        self.method, self.url, self.headers, self.body = self.get_data()
        self.host = self.headers["Host"] if "Host" in self.headers else ""
        self.user_agent = self.headers["User-Agent"] if "User-Agent" in self.headers else ""
        self.content_type = self.headers["Content-Type"] if "Content-Type" in self.headers else ""
    def get_data(self) -> tuple[str, str, dict, str]:
        """Split incoming request to variables"""
        data = self._recv_all()
        if not data:
            return "", "", {}, ""
        header_data, body = data.split(CRLF, 1)
        header_lines = header_data.split("\r\n")

        # Extract request line (method and URL)
        request_line = header_lines[0] if header_lines else ""
        method, url, _ = request_line.split(" ")
        headers = {}
        for line in header_lines[1:]:
            key, value = line.split(": ", 1)
            headers[key] = value

        return method, url, headers, body

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
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="HTTP сервер")
    parser.add_argument("--directory", default="/tmp/", help="Папка с файлами")
    args = parser.parse_args()
    file_folder = args.directory

    with socket.create_server(("localhost", 4221), reuse_port=True) as server_socket:
        while True:
            conn, _ = server_socket.accept()  # wait for client
            thread = threading.Thread(target=receive_connection, args=(conn,file_folder,))
            thread.start() # test

if __name__ == "__main__":
    main()
