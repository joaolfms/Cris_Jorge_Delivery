# Dockerfile

# Etapa 1: Utilizar uma imagem base oficial e leve do Python.
# A tag 'slim' é uma boa escolha por ser menor que a imagem padrão.
FROM python:3.9-slim

# Etapa 2: Definir o diretório de trabalho dentro do container.
# Todas as operações subsequentes serão executadas a partir deste diretório.
WORKDIR /code

# Etapa 3: Definir variáveis de ambiente para Python.
# PYTHONUNBUFFERED: Garante que os logs (prints) sejam enviados diretamente para o terminal.
# PYTHONDONTWRITEBYTECODE: Impede o Python de criar arquivos .pyc, que não são necessários em containers.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Etapa 4: Copiar o arquivo de dependências e instalá-las.
# Copiar apenas o requirements.txt primeiro aproveita o cache de layers do Docker.
# O Docker só irá reinstalar as dependências se este arquivo mudar.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 5: Copiar o restante do código da aplicação.
# O diretório 'app' local será copiado para o diretório '/code/app' no container.
COPY ./app /code/app

# Etapa 6: Expor a porta em que a aplicação FastAPI irá rodar.
# Esta porta será mapeada para uma porta do host no docker-compose.yml.
EXPOSE 8000

# Etapa 7: Definir o comando para iniciar a aplicação.
# 'uvicorn': O servidor ASGI que irá rodar a aplicação FastAPI.
# 'app.main:app': Localização da instância do FastAPI (arquivo main.py, objeto app).
# '--host 0.0.0.0': Faz o servidor escutar em todas as interfaces de rede,
#                   tornando-o acessível de fora do container.
# '--port 8000': A porta que o Uvicorn usará dentro do container.
# '--reload': Ativa o recarregamento automático em caso de alterações no código (ótimo para desenvolvimento).
#             Para produção, considere remover esta flag para melhor performance.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
