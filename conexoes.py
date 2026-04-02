import socket
import logging

logger = logging.getLogger(__name__)
from mensagens import build_con_init_msg, build_fin_msg, parse_response, ACK, NACK
from rede import send_and_receive, LIMIT_ATTEMPTS_FIN

def create_socket_udp(timeout: float) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    return sock

# Abre conexão com o servidor e retorna o ID da conexão
def open_connection(sock: socket.socket, server_addr: tuple[str, int]) -> int:
    # Monta binário da mensagem que estabelece a conexão
    msg_handshake = build_con_init_msg()
    
    while True:
        # segundo valor (direita) é a quantidade de timeouts, desnecessário no momento
        raw_resp, _ = send_and_receive(sock, msg_handshake, server_addr)
        
        # Extrai significado da resposta do servidor, já que retorna em binário
        response = parse_response(raw_resp)
        
        if response["tipo"] == ACK:
            logger.info(f"ID de Conexão no Servidor: {response['num_conexao']}")
            return response["num_conexao"]
        else:
            logger.warning("Resposta inesperada ao abrir conexão. Tentando novamente")


def close_connection(sock: socket.socket, num_conexao: int, server_addr: tuple[str, int]) -> None:
    msg_fin = build_fin_msg(num_conexao)
    
    # Para que o cliente não fique tentando fechar conexão infinitamente
    limit_attempts = 0

    while True:
        if limit_attempts > LIMIT_ATTEMPTS_FIN:
            logger.error("Limite de tentativas para fechar conexão excedido. Encerrando socket abruptamente.")
            sock.close()
            return 

        raw_resp, _ = send_and_receive(sock, msg_fin, server_addr)
        response = parse_response(raw_resp)
        
        if response["tipo"] == ACK:
            logger.info("ACK recebido para o encerramento")
            sock.close()

            return
        elif response["tipo"] == NACK: # NACK
            logger.warning("Servidor recusou o encerramento")
        else:
            logger.error("Erro ao encerrar conexão")

        limit_attempts += 1
