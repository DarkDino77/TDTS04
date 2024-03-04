import socket
import re
import sys

# Represents an HTTP message, allows for the extraction of header-information.
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


# Replace the targeted content of the HTTP response body, 
# update the content-length if necessary.
def replace_content(data, body_length):
    modified_data = re.sub(b'Smiley', b'Trolly', data)
    modified_data = re.sub(b'(?<![\w-])Stockholm(?![\w-])', 
                           'Linköping'.encode("utf-8"), modified_data)
    
    modified_data = re.sub(rb'Content-Length:\s(\d+)', 
                           b'{str(body_length)}', modified_data)
    return modified_data


# Modifies the client request to the server.
def handle_client(client_socket):
    request_data = client_socket.recv(4096)
    if not request_data: return

    # Extract the URL from the GET request.
    url_match = re.search(rb'GET\s+([^ ]+)', request_data)

    if url_match:
        url = url_match.group(1)
        host_name = re.search('\/\/([a-zA-Z\.]+)\/', url.decode('utf-8')).group(1)

        # If an image is requested, change the requested URL.
        image_match = re.search(b'\/(smiley).jpg', url)
        if image_match:
            request_data = re.sub(rb'smiley', rb'trolly', request_data)

        handle_server_response(request_data, host_name, client_socket)


# Sends the modified HTTP request to the server, manipulates the HTTP response 
# and sends it to the client.
def handle_server_response(request_data, host_name, client_socket):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.connect((host_name, 80))
        server_socket.sendall(request_data)
        response_data = server_socket.recv(4096)

        # Parse the HTTP response
        message = HTTP_Message(response_data)
        total_data_received = len(response_data)
        content_length_header = message.headers.get("Content-Length")

        # Continue receiving data from the server socket, untill the received 
        # data amounts to the content-length header.
        total_content_length = int(content_length_header)
        while total_data_received < total_content_length:
            temp_response_data = server_socket.recv(4096)
            if not temp_response_data:
                break
            response_data += temp_response_data
            total_data_received += len(temp_response_data)

        # Modify the response content and send it to the client.
        modified_response = replace_content(response_data, message.body_length)
        client_socket.sendall(modified_response)
        client_socket.close()


# Starts a socket listening to the sent in address and port.
def start_proxy(proxy_host_ip = "127.0.0.1", proxy_host_port = 8888):
    proxy_host = proxy_host_ip
    proxy_port = proxy_host_port

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((proxy_host, proxy_port))
    proxy_socket.listen(5)

    # Handle any incoming client GET requests.
    try:
        while True:
            client_socket = proxy_socket.accept()[0]
    
            handle_client(client_socket)
    except (KeyboardInterrupt):
        proxy_socket.close()


# Start the proxy when running the program.
if __name__ == "__main__":
    if len(sys.argv) == 3:
        proxy_host_ip = sys.argv[1]
        proxy_host_port = int(sys.argv[2])
        start_proxy(proxy_host_ip, proxy_host_port)
    else:
        start_proxy()