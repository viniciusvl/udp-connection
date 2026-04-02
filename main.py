import socket
from mensagens import read_file
from conexoes import open_connection, close_connection
from rede import transfer_file

def main():
    SERVER_IP = "18.230.108.156"
    SERVER_PORT = 50000
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)
    
    try:
        blocks = read_file("catita.png")
    except FileNotFoundError:
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)
    
    conn_id = open_connection(client_socket, SERVER_ADDR)
    
    transfered, logs = transfer_file(client_socket, conn_id, blocks, SERVER_ADDR)
    
    if transfered:
        correctly_closed = close_connection(client_socket, conn_id, SERVER_ADDR)
        
        if not correctly_closed:
            print("NACK recebido.")
    else:
        print("Servidor rejeitou a conexão.")

    client_socket.close()

    print(" Stats:")
    print(f"| Tempo gasto:              {logs.get('tempo', 0)} segundos")
    print(f"| Blocos despachados:       {logs.get('blocos', 0)} blocos")
    print(f"| Timeouts:                 {logs.get('timeouts', 0)} pacotes perdidos")
    print(f"| Nacks:                    {logs.get('nacks', 0)} pacotes corrompidos")
    print(f"| Retransmissoes:           {logs.get('retransmissoes', 0)} retransmitidos")

if __name__ == "__main__":
    main()
