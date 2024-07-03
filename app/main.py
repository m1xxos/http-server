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
            data = conn.recv(4096).decode()
            request = data.split("\r\n")[0]
            url = request.split(' ')[1]
            print("url:", url)
            if url == '/':
                conn.sendall(http_ok_message)
            if '/echo/' in url:
                echo_message = str(url).split('/echo/')[1]
                headers = f'Content-Type: text/plain\r\nContent-Length: {len(echo_message)}\r\n\r\n'
                response = f"HTTP/1.1 200 OK\r\n{headers}{echo_message}\r\n\r\n".encode()
                print(response)
                conn.sendall(response)
            else:
                conn.sendall(http_error_message)


if __name__ == "__main__":
    main()
