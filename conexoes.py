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
    # se não conseguir resposta do servidor, o cliente irá tentar limit_attempts vezes
    # evitar ficar preso infinitamente no estado de "espera"
    limit_attempts = 0

    while True:
        if limit_attempts > LIMIT_ATTEMPTS_FIN:
            logger.error("Limite de tentativas para abrir conexão excedido. Encerrando socket abruptamente.")
            sock.close()
            raise RuntimeError("Falha ao abrir conexão com o servidor.")

        # segundo valor (direita) é a quantidade de timeouts, desnecessário no momento
        raw_resp, _ = send_and_receive(sock, msg_handshake, server_addr)

        # Extrai significado da resposta do servidor, já que retorna em binário
        response = parse_response(raw_resp)

        if response["tipo"] == ACK: # conexão estabelecida
            logger.info(f"ID de Conexão no Servidor: {response['num_conexao']}")
            return response["num_conexao"]
        else:
            logger.warning("Erro ao abrir conexão. Tentando novamente")
            limit_attempts += 1


def close_connection(sock: socket.socket, num_conexao: int, server_addr: tuple[str, int]) -> bool:
    # Encerra a conexão e retorna True se o arquivo foi recebido corretamente, False se não
    msg_fin = build_fin_msg(num_conexao)

    # Para que o cliente não fique tentando fechar conexão infinitamente
    limit_attempts = 0

    while True:
        if limit_attempts > LIMIT_ATTEMPTS_FIN:
            logger.error("Limite de tentativas para fechar conexão excedido. Encerrando socket abruptamente.")
            sock.close()
            return False

        raw_resp, _ = send_and_receive(sock, msg_fin, server_addr)
        response = parse_response(raw_resp)

        if response["tipo"] == ACK:
            logger.info("Conexão encerrada. Arquivo recebido corretamente pelo servidor.")
            sock.close()
            return True
        elif response["tipo"] == NACK:
            logger.warning("Servidor sinalizou NACK ao finalizar. Tentando novamente.")
            limit_attempts += 1
            continue
        else:
            logger.error("Resposta inesperada ao encerrar conexão. Tentando novamente.")

        limit_attempts += 1
