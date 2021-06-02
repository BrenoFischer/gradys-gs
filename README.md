## README para auxiliar ambiente de desenvolvimento

### Pré-requisitos
<!--ts-->
  * Ter python3 instalado na máquina
<!--te-->

### Clonando o repositório:
<!--ts-->
  * Clonar repositório do github para máquina local
  * Criar virtual env (passos no Windows (prompt) abaixo)
    * python -m venv C:\path-até-root-desse projeto/venv
    * Mais info em "https://docs.python.org/3/library/venv.html"
  * Ativar venv
    * C:\path-até-root-desse-projeto\venv\Scripts\activate
  * Instalar bibliotecas do projeto dentro do venv
    * Na pasta root do projeto, rodar "pip install -r requirements.txt"
<!--te-->

### Acessando variaveis secretas:
<!--ts-->
  * Criar file com nome .env na pasta "config" em root/config
  * Colocar as variáveis secretas dentro do arquivo .env:
    * Digitar a chave: SECRET_KEY='xxxx'
    * Digitar a chave: GOOGLE_MAPS_API_KEY='xxxx'
<!--te-->

### Rodando servidor conexão arduino:
<!--ts-->
  * Rodar python manage.py runserver
<!--te-->

### Acessando página home:
<!--ts-->
  * Acessar localhost:8000
<!--te-->