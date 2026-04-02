## **Equipe**:

- Allan Gabriel da Cunha Vasconcelos, 20240009142
- Vinícius Victor Lopes de Almeida, 20240008181


## **Como rodar o programa**

```bash
python main.py
```

## **Logs**

- **Durante envio do arquivo:**
```
2026-04-02 14:23:01,342 INFO: ID de Conexão no Servidor: 4
2026-04-02 14:23:01,411 INFO: Bloco 1/12 (msg_num=1)
2026-04-02 14:23:01,489 INFO: Bloco 2/12 (msg_num=2)
2026-04-02 14:23:01,532 WARNING: Bloco 3 corrompido de acordo com o servidor. Re-enviando
2026-04-02 14:23:01,601 INFO: Bloco 3/12 (msg_num=1)
2026-04-02 14:23:02,014 INFO: Bloco 12/12 (msg_num=2)
```

- **Após envio do arquivo:**
```
2026-04-02 20:13:15,432 INFO: | Tempo gasto:              44.041813135147095 segundos
2026-04-02 20:13:15,432 INFO: | Blocos despachados:       404 blocos
2026-04-02 20:13:15,433 INFO: | Timeouts:                 17 pacotes perdidos
2026-04-02 20:13:15,433 INFO: | Nacks:                    19 pacotes corrompidos
2026-04-02 20:13:15,433 INFO: | Retransmissoes:           36 retransmitidos
2026-04-02 20:13:15,499 INFO: ACK recebido para o encerramento
```
