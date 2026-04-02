import socket
import time
import logging

logger = logging.getLogger(__name__)

LIMIT_ATTEMPTS_FIN = 10

from mensagens import parse_response, build_data_msg
from response_handler import response_handler, NEXT, RETRY, ABORT

# Envia mensagem e ESPERA por resposta do servidor
# Retorno: dados e quantidade de reenvios, para debug
def send_and_receive(sock: socket.socket, message: bytes, server_addr: tuple[str, int]) -> tuple[bytes, int]:
    timeouts = 0

    # O loop infinito serve para que o cliente continue enviando
    # mesmo que haja algum algo, captado por try-except
    while True:
        try:
            sock.sendto(message, server_addr)
            data, addr = sock.recvfrom(2048)
            return data, timeouts
        except socket.timeout:
            timeouts += 1
            logger.warning("Reenviando")

def transfer_file(sock: socket.socket, num_conexao: int, file_chunks: list[bytearray], server_addr: tuple[str, int]) -> dict:
    start_time = time.time()
    total_timeouts = 0
    total_nacks = 0
    total_file_chunks_sent = len(file_chunks)

    current_msg_num = 1

    for idx, chunk in enumerate(file_chunks):
        current_block_success = False

        while not current_block_success:
            bytes_data = build_data_msg(current_msg_num, num_conexao, chunk)

            raw_response, t_outs = send_and_receive(sock, bytes_data, server_addr)
            total_timeouts += t_outs

            resp_dict = parse_response(raw_response)

            # Retorna número que informa status da resposta.
            action = response_handler(resp_dict, target_msg_num=current_msg_num)

            if action == NEXT:
                logger.info(f"Bloco {idx + 1}/{len(file_chunks)} (msg_num={current_msg_num})")
                current_block_success = True
            elif action == RETRY:
                total_nacks += 1
            elif action == ABORT:
                logger.error("Transferência Abortada")
                return {}

        current_msg_num = 2 if current_msg_num == 1 else 1

    end_time = time.time()

    return {
        "tempo": end_time - start_time,
        "blocos": total_file_chunks_sent,
        "nacks": total_nacks,
        "timeouts": total_timeouts,
        "retransmissoes": total_nacks + total_timeouts
    }
