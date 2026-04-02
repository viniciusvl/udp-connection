import socket
import os

CONN_INIT_MSG = 0
DATA_MSG = 1
ACK = 2
NACK = 3
CONN_FIN_MSG = 4
TOO_SHORT_ERR = 5
TOO_LONG_ERR = 6
BAD_CONN_ERR = 7
BAD_MSG_ERR = 8
BAD_TYPE_ERR = 9

SERVER_IP = "18.230.108.156"
SERVER_PORT = 50000
SERVER_ADDR = (SERVER_IP, SERVER_PORT)
ARCHIVE = "catita.png"


def build_header(msg_type: int, msg_num: int, conn_id: int) -> bytearray:
    """
    Constrói o cabeçalho fixo de 3 bytes usando operações bit a bit.
    
    Estrutura do cabeçalho (3 bytes / 24 bits):
    - Byte 0: 
        - 4 bits mais significativos: msg_type (tipo da mensagem)
        - 4 bits menos significativos: msg_num (número da mensagem)
    - Byte 1 e Byte 2:
        - 16 bits para o conn_id (número da conexão), em formato big-endian.
    """
    # Para montar o byte 0, pegamos o tipo (ex: 0000 0001) e arrastamos 4 casas 
    # pro lado esquerdo (vira 0001 0000). Depois juntamos com o número da msg 
    # usando o operador lógico OR (|). O & 0x0F serve para garantir que só 4 bits sejam usados.
    byte0 = (msg_type << 4) | (msg_num & 0x0F)
    
    # O conn_id tem 16 bits (ex: 0000 0000 0000 0101).
    # Como o protocolo pede big-endian, o byte da esquerda vai primeiro.
    # Para pegar os 8 bits da esquerda, deslocamos o número 8 vezes para a direita.
    byte1 = (conn_id >> 8) & 0xFF
    
    # O byte da direita são só os 8 bits originais.
    byte2 = conn_id & 0xFF
    
    # O bytearray permite manipular bytes diretamente e retornar um vetor exato de 3 bytes.
    return bytearray([byte0, byte1, byte2])


def parse_response(data: bytes) -> dict:
    """
    Desmonta os bytes que o servidor mandou para extrair o cabeçalho.
    Retorna um dicionário com os campos do cabeçalho.
    """
    # Uma mensagem válida para o nosso caso sempre precisa ter pelo menos 3 bytes.
    # Mas pra segurança se vier mais curto, a gente ignora ou trata como erro.
    if len(data) < 3:
        # Retorna valores inválidos que serão tratados em outra função
        return {"tipo": -1, "num_msg": -1, "conn_id": -1}
    
    # No primeiro byte, os 4 bits da esquerda são o tipo. A gente arrasta eles pra direita.
    tipo = (data[0] >> 4) & 0x0F
    
    # Ainda no primeiro byte, os 4 bits da direita são o numero da msg. 
    num_msg = data[0] & 0x0F
    
    # Os dois bytes seguintes formam o id da conexao. Trazemos o primeiro byte (byte 1)
    # 8 bits pra esquerda e usamos OR pra colar com o segundo byte (byte 2).
    conn_id = (data[1] << 8) | data[2]
    
    return {"tipo": tipo, "num_msg": num_msg, "conn_id": conn_id}


def build_conn_init() -> bytearray:
    """
    Cria a mensagem de inicialização de conexão (CONN_INIT_MSG).
    Tipo = 0, Msg_num = 0, Conn = 0
    """
    return build_header(msg_type=CONN_INIT_MSG, msg_num=0, conn_id=0)


def build_data_msg(msg_num: int, conn_id: int, payload: bytearray) -> bytearray:
    """
    Monta uma mensagem de dados com o arquivo em si (DATA_MSG).
    Tipo = 1, e possui o payload logo depois do cabeçalho de 3 bytes.
    """
    header = build_header(msg_type=DATA_MSG, msg_num=msg_num, conn_id=conn_id)
    message = bytearray()
    
    # Junta os bytes do cabeçalho com os bytes do pedaço de arquivo que vai do lado.
    message.extend(header)
    message.extend(payload)
    
    return message


def build_conn_fin(conn_id: int) -> bytearray:
    """
    Cria a mensagem de finalização de conexão (CONN_FIN_MSG).
    Tipo = 4, Msg_num = 0
    """
    return build_header(msg_type=CONN_FIN_MSG, msg_num=0, conn_id=conn_id)


def read_file(path: str) -> list[bytearray]:
    """
    Abre o nosso catita.png para leitura com regras binárias ("rb").
    Divide e lê o arquivo todo em pedaços de tamanho máximo 1000 bytes.
    """
    chunks = []
    # Usamos o 'with' porque ele com certeza fecha o arquivo sem deixar vazamento
    with open(path, "rb") as file:
        while True:
            # Lê exatos (ou até) 1000 bytes. O read garante isso.
            chunk = file.read(1000)
            
            # Quando a variável 'pedaço' for vazia, significa o fim do arquivo.
            if not chunk:
                break
                
            chunks.append(bytearray(chunk))
            
    return chunks


def error_handler(resp_dict):
    """
    Função simples para avaliar o tipo de resposta caso seja erro, 
    imprimindo os detalhes no console.
    """
    error_type = resp_dict["tipo"]
    
    if error_type == TOO_SHORT_ERR:
        print("Mensagem TOO SHORT (menor que 3 bytes). O tamanho limite foi desrepeitado.")
    elif error_type == TOO_LONG_ERR:
        print("Mensagem TOO LONG (maior que 1003 bytes).")
    elif error_type == BAD_CONN_ERR:
        print("BAD CONNECTION. Você usou um ID de conexão inválido.")
    elif error_type == BAD_MSG_ERR:
        print("BAD MESSAGE. Esperava-se outra numeração ou formato.")
    elif error_type == BAD_TYPE_ERR:
        print("BAD TYPE. Tipo de pacote desconhecido para o servidor.")
    else:
        # Para caso chegue lixo da rede mal formatado ou algo não previsto
        print(f"Erro não mapeado ({error_type})")


def main():
    # Antes de enviar e tentar iniciar, garante que o arquivo exista
    if not os.path.exists(ARCHIVE):
        print("Arquivo não encontrado")
        return

    chunks = read_file(ARCHIVE)
    print(f"Lido em {len(chunks)} partes")

    # Inicia o controle Socket sobre protocolo UDP (SOCK_DGRAM) do IPv4 (AF_INET)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # O timeout de 1 segundo tem que ser setado logo agora. 
    # Passou disso sem dados na leitura, levanta erro Exception (socket.timeout)
    client_socket.settimeout(1.0)
    
    id_connection = 0  
    
    #Handshake
    connected = False
    mensagem_init = build_conn_init()
    
    print("Solicitando conexão")
    while not connected:
        try:
            # Envia em raw bytes
            client_socket.sendto(mensagem_init, SERVER_ADDR)
            
            # Aguarda alguma resposta, permitindo buffer largo porque pode haver lixo.
            bytes_response, addr = client_socket.recvfrom(2048)
            
            response = parse_response(bytes_response)
            
            # Se for sucesso, o servidor enviou tipo == 2 (ACK).
            if response["tipo"] == ACK:
                id_connection = response["conn_id"]
                connected = True
                print(f"ID da conexão: {id_connection}")
            else:
                error_handler(response)
                
        except socket.timeout:
            # Padrão temporizador dispará devido perda do pacote e retransportará a msg.
            print("Timeout foi atingido")


    print("Transferência Stop-and-Wait do arquivo iniciada")
    
    # A numeração de pacotes deve começar em 1 e sempre alternar entre 1 e 2.
    message_number = 1
    
    for idx, chunk in enumerate(chunks):
        send_success = False
        bytes_data = build_data_msg(message_number, id_connection, chunk)
        
        while not send_success:
            try:
                client_socket.sendto(bytes_data, SERVER_ADDR)
                
                bytes_response, addr = client_socket.recvfrom(2048)
                response = parse_response(bytes_response)
                
                # Caso onde deu tudo certo (ACK && o num da MSG é igual ao que enviamos)
                if response["tipo"] == ACK and response["num_msg"] == message_number:
                    #print(f" -> Bloco {indice + 1}/{len(blocos_dados)} Enviado com Sucesso. (Msg Num: {numero_mensagem})")
                    send_success = True
                
                # NACK é caso algo no caminho corrompeu, não paramos o for loop. Tenta reenviar
                elif response["tipo"] == NACK:
                    print(f"NACK Recebido")
                    # Simplesmente rodamos o loop while False novamente e mandamos de novo.
                
                # Evento de ACK recebido porem numero num_msg é != do atual foi descarte (ACK duplicado atrasado)
                elif response["tipo"] == ACK and response["num_msg"] != message_number:
                    pass
                
                else: # Qualquer erro do tipo 5 a 9.
                    error_handler(response)
                    
            except socket.timeout:
                # Disparo de timer - a rede demorou demais
                print(f"TIMEOUT alcançado")
        
        # Alternância mandatória para stop-and-wait do protocolo (0001 -> 0010 -> 0001)
        if message_number == 1:
            message_number = 2
        else:
            message_number = 1


    print("Arquivo transferido")
    end_packet = build_conn_fin(id_connection)
    closed = False
    
    while not closed:
        try:
            client_socket.sendto(end_packet, SERVER_ADDR)
            
            bytes_response, addr = client_socket.recvfrom(2048)
            response = parse_response(bytes_response)
            
            if response["tipo"] == ACK:
                print(" Desconexão bem sucedida")
                closed = True
            elif response["tipo"] == NACK:
                print("Servidor retornou NACK")
                closed = True
            else:
                error_handler(response)
                
        except socket.timeout:
            print("Sem resposta no encerramento")

    client_socket.close()
    print("Conexão Encerrada")


if __name__ == "__main__":
    main()
