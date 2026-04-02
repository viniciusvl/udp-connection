import logging

logger = logging.getLogger(__name__)

CONN_INIT_MSG = 0
DATA_MSG = 1
ACK = 2
NACK = 3
CONN_FIN_MSG = 4
TOO_SHORT_ERR = 5
TOO_LONG_ERR = 6
INVALID_CONN = 7
INVALID_MSG_NUM = 8
BAD_TYPE_ERR = 9

def build_header(tipo: int, num_msg: int, num_conexao: int) -> bytearray:
    """
    Constrói o cabeçalho fixo de 3 bytes usando operações bit a bit.
    - 4 bits de tipo (nibble alto do byte 0)
    - 4 bits de num_msg (nibble baixo do byte 0)
    - 16 bits de num_conexao em big-endian (bytes 1 e 2)
    """
    byte0 = (tipo << 4) | (num_msg & 0x0F)
    byte1 = (num_conexao >> 8) & 0xFF
    byte2 = num_conexao & 0xFF
    
    return bytearray([byte0, byte1, byte2])

def parse_response(data: bytes) -> dict:
    if len(data) < 3:
        return {"tipo": -1, "num_msg": -1, "num_conexao": -1}

    tipo = (data[0] >> 4) & 0x0F
    num_msg = data[0] & 0x0F
    num_conexao = (data[1] << 8) | data[2]

    return {"tipo": tipo, "num_msg": num_msg, "num_conexao": num_conexao}

# Constroi a mensagem de conexão
def build_con_init_msg() -> bytearray:
    return build_header(tipo=CONN_INIT_MSG, num_msg=0, num_conexao=0)

# Constroi mensagem para envio de dados, com header + payload
def build_data_msg(msg_num: int, num_conexao: int, payload: bytearray) -> bytearray:
    header = build_header(tipo=DATA_MSG, num_msg=msg_num, num_conexao=num_conexao)
    message = bytearray()
    message.extend(header)
    message.extend(payload)
    return message

# Constroi mensagem de encerramento de conexão
def build_fin_msg(num_conexao: int) -> bytearray:
    return build_header(tipo=CONN_FIN_MSG, num_msg=0, num_conexao=num_conexao)

def read_file(path: str) -> list[bytearray]:
    try:
        chunks = []
        with open(path, "rb") as file:
            while True:
                chunk = file.read(1000)
                if not chunk:
                    break
                chunks.append(bytearray(chunk))
        return chunks
    except FileNotFoundError as e:
        logger.error(f"Arquivo '{path}' não encontrado. {e}")
        raise FileNotFoundError(f"Arquivo '{path}' não encontrado.")
