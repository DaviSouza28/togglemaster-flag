# Imagem base com Python
FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia as dependências primeiro
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Porta utilizada pelo flag-service
EXPOSE 8002

# Inicia a aplicação com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8002", "app:app"]