import logging
from mensagens import read_file
from conexoes import create_socket_udp, open_connection, close_connection
from rede import transfer_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    SERVER_IP = "18.230.108.156"
    SERVER_PORT = 50000
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)
    TIMEOUT_DEFAULT = 1.0

    # Lê o arquivo
    file_chunks = read_file("catita.png")

    # Cria socket UDP
    client_socket = create_socket_udp(timeout=TIMEOUT_DEFAULT)
    
    # Abre conexão e retorna ID da conexão no servidor
    num_conexao = open_connection(client_socket, SERVER_ADDR)
    
    # Transfere arquivo para servidor
    status_req = transfer_file(client_socket, num_conexao, file_chunks, SERVER_ADDR)

    # Encerra a conexão e verifica se o servidor confirmou o recebimento correto
    transfer_ok = close_connection(client_socket, num_conexao, SERVER_ADDR)

    logger.info(" Stats:")
    logger.info(f"| Tempo gasto:              {status_req.get('tempo', 0):.2f} segundos")
    logger.info(f"| Blocos despachados:       {status_req.get('blocos', 0)} blocos")
    logger.info(f"| Timeouts:                 {status_req.get('timeouts', 0)} pacotes perdidos")
    logger.info(f"| Nacks:                    {status_req.get('nacks', 0)} pacotes corrompidos")
    logger.info(f"| Retransmissoes:           {status_req.get('retransmissoes', 0)} retransmitidos")
    logger.info(f"| Resultado final:          {'SUCESSO' if transfer_ok else 'FALHA (servidor rejeitou o arquivo)'}")

if __name__ == "__main__":
    main()
