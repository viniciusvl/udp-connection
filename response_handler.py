import logging

logger = logging.getLogger(__name__)

from mensagens import ACK, NACK, INVALID_CONN, INVALID_MSG_NUM, TOO_SHORT_ERR, TOO_LONG_ERR, BAD_TYPE_ERR

# Informam para o cliente qual o próximo passo a tomar, de acordo com a resposta do servidor.
NEXT  =  1
RETRY =  0
ABORT = -1

# Armazena possíveis erros que o servidor pode enviar.
# Definido globalmente para diminuir o overhead de comparações excessivas com if´s e else´s
ERROR_DISPATCH = {
    TOO_SHORT_ERR:   (RETRY, "Servidor rejeitou por tamanho mínimo (TOO SHORT)"),
    TOO_LONG_ERR:    (RETRY, "O tamanho de 1003 bytes foi superado (TOO LONG)"),
    INVALID_CONN:    (ABORT, "Conexão Inválida (INVALID CONN)"),
    INVALID_MSG_NUM: (ABORT, "Ordem dos pacotes errada (INVALID MSG NUM)"),
    BAD_TYPE_ERR:    (RETRY, "Tipo de mensagem inválido (BAD TYPE)"),
}

"""
Retorno response_handler:

1 -> NEXT, pode continuar
0 -> RETRY, deve reenviar o mesmo bloco
-1 -> ABORT, deve abortar a transferência
"""
def response_handler(response: dict, target_msg_num: int) -> int:
    type = response.get("tipo", -1)
    msg_num = response.get("num_msg", -1)

    if type == ACK:
        # Se recebeu ACK da mensagem que está esperando, então continua envio.
        if msg_num == target_msg_num:
            return NEXT
        else:
            logger.warning(f"ACK de pacote duplicado ou atrasado (esperado {target_msg_num}, recebido {msg_num})")
            return NEXT

    elif type == NACK:
        if msg_num == target_msg_num:
            logger.warning(f"Bloco {msg_num} corrompido de acordo com o servidor. Re-enviando")
            return RETRY
        else:
            logger.warning(f"Erro em pacote ({msg_num})")
            return NEXT

    action, msg = ERROR_DISPATCH.get(type, (ABORT, "Erro inesperado"))

    logger.error(msg)
    
    return action