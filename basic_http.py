import socket
import json
import random


def roll_biased_dice(probabilities, number_of_random):
    faces = [1, 2, 3, 4, 5, 6]
    rolls = random.choices(faces, weights=probabilities, k=number_of_random)
    return rolls


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 8081))
server_socket.listen(1)
print("Server is listening on port 8081...")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} established.")

    request = client_socket.recv(4096).decode('utf-8')
    print(f"Request received ({len(request)}):")
    print("*" * 50)
    print(request)
    print("*" * 50)

    try:
        request_line = request.splitlines()[0] if request else ""

        if request_line.startswith("GET /myjson"):
            response_data = {
                "status": "success",
                "message": "Hello, KU!"
            }
            response_json = json.dumps(response_data)
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n\r\n"
                f"{response_json}"
            )

        elif request_line.startswith("POST /roll_dice"):
            body = request.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in request else "{}"
            payload = json.loads(body)

            probabilities = payload.get("probabilities", [])
            number_of_random = payload.get("number_of_random", 1)

            if len(probabilities) != 6 or abs(sum(probabilities) - 1.0) > 1e-9:
                response_data = {
                    "status": "error",
                    "message": "probabilities must contain 6 values and sum to 1"
                }
                response = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    "Content-Type: application/json\r\n\r\n"
                    f"{json.dumps(response_data)}"
                )
            else:
                rolls = roll_biased_dice(probabilities, number_of_random)
                response_data = {
                    "status": "success",
                    "results": rolls,
                    "count": number_of_random,
                }
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n\r\n"
                    f"{json.dumps(response_data)}"
                )

        elif request_line.startswith("GET"):
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n\r\n"
                f"<html><body><h1>Hello, World!</h1><hr>{request}</body></html>"
            )
        else:
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    except Exception as e:
        response_data = {"status": "error", "message": str(e)}
        response = (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: application/json\r\n\r\n"
            f"{json.dumps(response_data)}"
        )

    client_socket.sendall(response.encode('utf-8'))
    client_socket.close()
    print("Waiting for the next TCP request...")