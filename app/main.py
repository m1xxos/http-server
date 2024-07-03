# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
        conn, _ = server_socket.accept()  # wait for client
        http_ok_message = b'HTTP/1.1 200 OK\r\n\r\n'
        http_error_message = b'HTTP/1.1 404 Not Found\r\n\r\n'
        with conn:
            data = conn.recv(4096)
            url = data.split()[1]
            conn.sendall
            if url == b'/':
                conn.sendall(http_ok_message)
            if b'/echo/' in url:
                conn.sendall(http_ok_message)
                echo_message = str(url).split('/echo/')[1].strip("'")
                print(echo_message)
                headers = f'Content-Type: text/plain\r\nContent-Length: {len(echo_message)}\r\n\r\n'
                conn.sendall(bytes(headers, encoding='utf8'))
                conn.sendall(bytes(echo_message, encoding='utf-8'))
            else:
                conn.sendall(http_error_message)


if __name__ == "__main__":
    main()
