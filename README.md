## README para auxiliar ambiente de desenvolvimento

### Pré-requisitos
1. Ter python3 instalado na máquina

### Clonando o repositório:
1. Clonar repositório do github para máquina local
2. Criar virtual env (passos no Windows (prompt) abaixo)
	2.1. python -m venv C:\path-até-root-desse projeto/venv
	2.2. Mais info em "https://docs.python.org/3/library/venv.html"
3. Ativar venv
	3.1. C:\path-até-root-desse-projeto\venv\Scripts\activate
4. Instalar bibliotecas do projeto dentro do venv
	4.1. Na pasta root do projeto, rodar "pip install -r requirements.txt"

### Acessando variaveis secretas:
1. Criar file com nome .env na pasta "config" em root/config
2. Colocar a variável secreta dentro do arquivo .env


### Rodando servidor conexão arduino:
1. Rodar python manage.py runserver


### Acessando página home:
1. Acessar localhost:8000