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
            if url == b'/':
                conn.sendall(http_ok_message)
            else:
                conn.sendall(http_error_message)


if __name__ == "__main__":
    main()
