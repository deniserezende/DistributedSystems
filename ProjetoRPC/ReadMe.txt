RESUMO SOBRE RPC (REMOTE PROCEDURE CALL):

O RPC é um protocolo de comunicação de software que um programa pode usar para solicitar um serviço
de um programa localizado em outro computador em uma rede sem precisar entender os detalhes da rede.
Isso permite a execução de funções ou procedimentos em um sistema remoto, como se estivessem sendo chamados localmente.
Ele é usado para facilitar a comunicação entre sistemas distribuídos de maneira transparente, como se os componentes
estivessem sendo executados na mesma máquina.


DESCRIÇÃO DA IMPLEMENTAÇÃO:

A implementação foi realizada em python utilizando a biblioteca xmlrpc.server e xmlrpc.client
já embutidas no próprio python.

dados.txt é o arquivo dos dados iniciais
database.txt é o arquivo com os dados do resultado


INSTRUÇÕES PARA COMPILAÇÃO E EXECUÇÃO DO PROJETO:

Abra dois terminais (T1 e T2)

em T1 execute:
python server.py

em T2 execute:
python client.py

