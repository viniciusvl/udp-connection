from mensagens import build_conn_init, build_conn_fin, parse_response, ACK
from rede import send_and_receive

def open_connection(sock, server_addr) -> int:
    msg_handshake = build_conn_init()
    
    while True:
        raw_resp, _ = send_and_receive(sock, msg_handshake, server_addr)
        response = parse_response(raw_resp)
        
        if response["tipo"] == ACK:
            print(f"ID de Conexão no Servidor: {response['conn_id']}")
            return response["conn_id"]
        else:
            print("Resposta inesperada ao abrir conexão. Tentando novamente")


def close_connection(sock, conn_id, server_addr) -> bool:

    msg_fin = build_conn_fin(conn_id)
    
    while True:
        raw_resp, _ = send_and_receive(sock, msg_fin, server_addr)
        response = parse_response(raw_resp)
        
        if response["tipo"] == ACK:
            print("ACK recebido para o encerramento")
            return True
        elif response["tipo"] == 3: # NACK
            print("Servidor recusou o encerramento")
            return False
        else:
            print("Erro ao encerrar conexão")
            return False
