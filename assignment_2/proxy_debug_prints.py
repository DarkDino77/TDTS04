import socket
import re
import sys

class HTTP_Message:
    def __init__(self, raw_response):
        # Extract relevant parts from the raw HTTP response
        self.first_line, self.headers, self.body = self.extract_http_response(raw_response)
        self.body_length = len(self.body)

    def extract_http_response(self, response):
        # Split the response into header and body
        split_response = response.split(b"\r\n\r\n")
        head = split_response[0]
        body = split_response[1]

        # Decode the header and split it into lines
        lines = head.decode().split("\r\n")
        first_line = lines[0]

        # Extract headers into a dictionary
        headers = {}
        for line in lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value

        return first_line, headers, body

# Replace the targeted content of the HTTP response body, update the content-length if necessary.
def replace_content(data, body_length):
    modified_data = re.sub(b'Smiley', b'Trolly', data)
    modified_data = re.sub(b'(?<![\w-])Stockholm(?![\w-])', 'Linköping'.encode("utf-8"), modified_data)
    
    modified_data = re.sub(rb'Content-Length:\s(\d+)', b'{str(body_length)}', modified_data)
    return modified_data

# Modifies the client request
def handle_client(client_socket):
    request_data = client_socket.recv(4096)
    if not request_data: return
    
    print("------------------------------------------------------------------------------------------")
    request_message = HTTP_Message(request_data)
    print(f"Client Request: \033[92m{request_message.first_line}\033[0m")

    try:
        print(f"{request_data.decode()}")
    except:
        print("Could not decode message body") 

    # Extract the URL from the GET request
    url_match = re.search(rb'GET\s+([^ ]+)', request_data)
    if url_match:
        url = url_match.group(1)

        host_name = re.search('\/\/([a-zA-Z\.]+)\/', url.decode('utf-8')).group(1)

        # If the GET request contains an image URL (.jpg or .png), change the requested image URL.
        image_match = re.search(b'\/(smiley).jpg', url)
        if image_match:
            request_data = re.sub(rb'smiley', rb'trolly', request_data)

        handle_server_response(request_data, host_name, client_socket)

# Sends the modified HTTP request to the server, manipulates the HTTP response and sends it to the client.
def handle_server_response(request_data, host_name, client_socket):
    # Connect proxy to target server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.connect((host_name, 80))
        server_socket.sendall(request_data)
        response_data = server_socket.recv(4096)

        # Parse the HTTP response
        message = HTTP_Message(response_data)
        total_data_received = len(response_data)
        content_length_header = message.headers.get("Content-Length")

        # Print the status code
        print(f"Server Response: \033[92m{message.first_line}\033[0m")
        try:
            print(f"{response_data.decode()}")
        except:
            print("An exception occurred") 

        packet_counter = 1
        if content_length_header:
            total_content_length = int(content_length_header)
            while total_data_received < total_content_length:
                packet_counter += 1
                temp_response_data = server_socket.recv(4096)
                if not temp_response_data:
                    break
                response_data += temp_response_data
                total_data_received += len(temp_response_data)

        # Modify the response content and send it to the client
        modified_response = replace_content(response_data, message.body_length)
        client_socket.sendall(modified_response)
        client_socket.close()
        print(f"Received \033[92m{packet_counter}\033[0m packets from \033[01m{host_name}\033[0m")
    print("------------------------------------------------------------------------------------------")
    

    


def start_proxy(proxy_host_ip = "127.0.0.1", proxy_host_port = 8888):
    print("--- Welcome to proxy-py ---")
    proxy_host = proxy_host_ip
    proxy_port = proxy_host_port

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((proxy_host, proxy_port))
    proxy_socket.listen(5)

    print(f"Proxy listening on {proxy_host}:{proxy_port}")

    try:
        while True:
            client_socket, addr = proxy_socket.accept()
            print(f"Accepted a connection from \033[01m{addr[0]}:{addr[1]}\033[0m")
        
            handle_client(client_socket)
    except (KeyboardInterrupt, SystemExit):
        # This block will be executed when a KeyboardInterrupt (e.g., Ctrl+C) is received
        print("Proxy server is shutting down...")
        proxy_socket.close()
    finally:
        proxy_socket.close()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        proxy_host_ip = sys.argv[1]
        proxy_host_port = int(sys.argv[2])
        start_proxy(proxy_host_ip, proxy_host_port)
    else:
        start_proxy()