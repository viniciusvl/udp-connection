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

def build_header(msg_type: int, msg_num: int, conn_id: int) -> bytearray:
    """
    Constrói o cabeçalho fixo de 3 bytes usando operações bit a bit.
    - 4 bits de tipo (nibble alto do byte 0)
    - 4 bits de num_msg (nibble baixo do byte 0)
    - 16 bits de num_conexao em big-endian (bytes 1 e 2)
    """
    byte0 = (msg_type << 4) | (msg_num & 0x0F)
    byte1 = (conn_id >> 8) & 0xFF
    byte2 = conn_id & 0xFF
    
    return bytearray([byte0, byte1, byte2])

def parse_response(data: bytes) -> dict:
    if len(data) < 3:
        return {"tipo": -1, "num_msg": -1, "conn_id": -1}
    
    type = (data[0] >> 4) & 0x0F
    msg_num = data[0] & 0x0F
    conn_id = (data[1] << 8) | data[2]
    
    return {"tipo": type, "num_msg": msg_num, "conn_id": conn_id}

def build_conn_init() -> bytearray:
    
    return build_header(msg_type=CONN_INIT_MSG, msg_num=0, conn_id=0)

def build_data_msg(msg_num: int, conn_id: int, payload: bytearray) -> bytearray:
    header = build_header(msg_type=DATA_MSG, msg_num=msg_num, conn_id=conn_id)
    message = bytearray()
    message.extend(header)
    message.extend(payload)
    return message

def build_conn_fin(conn_id: int) -> bytearray:
    return build_header(msg_type=CONN_FIN_MSG, msg_num=0, conn_id=conn_id)

def read_file(path: str) -> list[bytearray]:
    chunks = []
    with open(path, "rb") as file:
        while True:
            chunk = file.read(1000)
            if not chunk:
                break
            chunks.append(bytearray(chunk))
    return chunks
