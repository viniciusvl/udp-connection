import socket
from mensagens import (
    parse_response, ACK, NACK, INVALID_CONN, INVALID_MSG_NUM, 
    TOO_SHORT_ERR, TOO_LONG_ERR, BAD_TYPE_ERR, build_data_msg
)
import time

def send_and_receive(sock, message, server_addr) -> tuple[bytes, int]:
    timeouts = 0
    while True:
        try:
            sock.sendto(message, server_addr)
            data, addr = sock.recvfrom(2048)
            return data, timeouts
        except socket.timeout:
            timeouts += 1
            print(f"Reenviando")

def response_handler(response: dict, target_msg_num: int) -> str:
    type = response.get("tipo", -1)
    msg_num = response.get("num_msg", -1)
    
    if type == ACK:
        if msg_num == target_msg_num:
            return "next"
        else:
            print(f"ACK de pacote duplicado ou atrasado (esperado {target_msg_num}, recebido {msg_num})")
            return "next"
            
    elif type == NACK:
        if msg_num == target_msg_num:
            print(f"Bloco {msg_num} corrompido de acordo com o servidor. Re-enviando")
            return "retry"
        else:
            print(f"Erro em pacote ({msg_num})")
            return "next"
            
    elif type == TOO_SHORT_ERR:
        print("Servidor rejeitou por tamanho mínimo (TOO SHORT)")
        return "retry"
    elif type == TOO_LONG_ERR:
        print("O tamanho de 1003 bytes foi superado (TOO LONG)")
        return "retry"
    elif type == INVALID_CONN:
        print("Conexão Inválida (INVALID CONN)")
        return "abort"
    elif type == INVALID_MSG_NUM:
        print("Ordem dos pacotes errada (INVALID MSG NUM)")
        return "abort"
    elif type == BAD_TYPE_ERR:
        print("Tipo de mensagem inválido (BAD TYPE)")
        return "retry"
    else:
        print(f"Erro inesperado")
        return "retry"


def transfer_file(sock, conn_id, blocks, server_addr):
    start_time = time.time()
    
    total_timeouts = 0
    total_nacks = 0
    total_blocks_sent = len(blocks)
    
    current_msg_num = 1
    
    for idx, chunk in enumerate(blocks):
        current_block_success = False
        
        while not current_block_success:
            bytes_data = build_data_msg(current_msg_num, conn_id, chunk)
            
            raw_response, t_outs = send_and_receive(sock, bytes_data, server_addr)
            total_timeouts += t_outs
            
            resp_dict = parse_response(raw_response)
            
            action = response_handler(resp_dict, target_msg_num=current_msg_num)
            
            if action == "next":
                print(f"Bloco {idx + 1}/{len(blocks)} (msg_num={current_msg_num})")
                current_block_success = True
            elif action == "retry":
                total_nacks += 1
            elif action == "abort":
                print("Transferência Abortada")
                return False, {}

        current_msg_num = 2 if current_msg_num == 1 else 1

    end_time = time.time()
    
    stats = {
        "tempo": end_time - start_time,
        "blocos": total_blocks_sent,
        "nacks": total_nacks,
        "timeouts": total_timeouts,
        "retransmissoes": total_nacks + total_timeouts
    }
    
    return True, stats
