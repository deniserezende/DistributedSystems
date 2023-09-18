RESUMO SOBRE RMI (REMOTE METHOD INVOCATION) vs RPC (REMOTE PROCEDURE CALL):

RMI: É uma abstração específica do ecossistema Java. Ele permite que objetos Java chamem métodos em objetos remotos, tornando a comunicação entre JVMs transparente.
Foca em invocar métodos em objetos remotos. Essa abordagem é mais orientada a objetos.

RPC: É uma abstração mais geral e independente da linguagem. Ele permite que funções ou procedimentos em uma máquina remota sejam chamados como se fossem locais.
É mais orientado a procedimentos ou funções, onde as chamadas remotas se assemelham a chamadas de função.

*Mesmo sendo uma abstração específica de Java, algumas outras linguagens criaram bibliotecas para utilizar a mesma ideia. 


DESCRIÇÃO DA IMPLEMENTAÇÃO:

A implementação foi realizada em python utilizando a biblioteca Pyro4.

Verificar se já está instalada:
python -m Pyro4.version
Ou
python3 -m Pyro4.version

Instalar:
pip install Pyro4
Ou 
pip3 install Pyro4

O arquivo da imagem final será salvo na própria pasta.


INSTRUÇÕES PARA COMPILAÇÃO E EXECUÇÃO DO PROJETO:

Abra três terminais (T1 e T2 e T3)

em T1 execute:
python Bin1Server.py

em T2 execute:
python Bin1Server.py

em T3 execute:
python Bin1Client.py

