## **Equipe**:

- Allan Gabriel da Cunha Vasconcelos, 20240009142
- Vinícius Victor Lopes de Almeida, 20240008181


## **Como rodar o programa**

```bash
python main.py
```

## **Logs**

- **Abertura de conexão:**
```
2026-04-02 14:23:01,342 INFO: ID de Conexão no Servidor: 4
```

- **Durante envio do arquivo:**
```
2026-04-02 14:23:01,411 INFO: Bloco 1/12 (msg_num=1)
2026-04-02 14:23:01,489 INFO: Bloco 2/12 (msg_num=2)
2026-04-02 14:23:01,532 WARNING: Bloco corrompido de acordo com o servidor. Re-enviando
2026-04-02 14:23:01,601 INFO: Bloco 3/12 (msg_num=1)
2026-04-02 14:23:01,610 WARNING: ACK de pacote duplicado ou atrasado (esperado 2, recebido 1). Reenviando.
2026-04-02 14:23:01,700 WARNING: NACK: servidor esperava msg_num=2, cliente enviou 1. Avançando.
2026-04-02 14:23:01,800 WARNING: Reenviando
2026-04-02 14:23:02,014 INFO: Bloco 12/12 (msg_num=2)
```

- **Erros durante envio:**
```
2026-04-02 14:23:01,900 ERROR: Servidor rejeitou por tamanho mínimo (TOO SHORT)
2026-04-02 14:23:01,901 ERROR: O tamanho de 1003 bytes foi superado (TOO LONG)
2026-04-02 14:23:01,902 ERROR: Tipo de mensagem inválido (BAD TYPE)
2026-04-02 14:23:01,903 ERROR: Conexão Inválida (INVALID CONN)
2026-04-02 14:23:01,904 ERROR: Ordem dos pacotes errada (INVALID MSG NUM)
2026-04-02 14:23:01,905 ERROR: Transferência Abortada
```

- **Encerramento de conexão:**
```
2026-04-02 14:23:02,100 WARNING: Servidor sinalizou NACK ao finalizar. Tentando novamente.
2026-04-02 14:23:02,200 INFO: Conexão encerrada. Arquivo recebido corretamente pelo servidor.
```

- **Estatísticas finais:**
```
2026-04-02 20:13:15,432 INFO:  Stats:
2026-04-02 20:13:15,432 INFO: | Tempo gasto:              44.04 segundos
2026-04-02 20:13:15,432 INFO: | Blocos despachados:       404 blocos
2026-04-02 20:13:15,433 INFO: | Timeouts:                 17 pacotes perdidos
2026-04-02 20:13:15,433 INFO: | Nacks:                    19 pacotes corrompidos
2026-04-02 20:13:15,433 INFO: | Retransmissoes:           36 retransmitidos
2026-04-02 20:13:15,434 INFO: | Resultado final:          SUCESSO
```
