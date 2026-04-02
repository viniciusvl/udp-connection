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

    # Primeiro procura na tabela de erros, para evitar comparações desnecessárias com if´s e else´s
    dispatch = ERROR_DISPATCH.get(type)
    if dispatch:
        action, msg = dispatch
        logger.error(msg)
        return action

    # Verifica respostas ACK ou NACK
    if type == ACK:
        if msg_num != target_msg_num:
            # ACK atrasado ou duplicado de pacote anterior ignorar e aguardar o correto
            logger.warning(f"ACK de pacote duplicado ou atrasado (esperado {target_msg_num}, recebido {msg_num}). Reenviando.")
            return RETRY
        return NEXT

    if type == NACK:
        if msg_num == target_msg_num:
            # Servidor recebeu o número correto mas o conteúdo estava corrompido
            logger.warning(f"Bloco {msg_num} corrompido de acordo com o servidor. Re-enviando")
            return RETRY
        else:
            # Servidor esperava outro número de mensagem — duplicata detectada, avançar
            logger.warning(f"NACK: servidor esperava msg_num={msg_num}, cliente enviou {target_msg_num}. Avançando.")
            return NEXT

    # Se não identificar, o sistema não sabe lidar com essa resposta.
    logger.error(f"Tipo de resposta desconhecido: {type}")
    return ABORT