# Usar uma imagem base Python para ARM (compatível com Raspberry Pi e servidores Linux)
FROM python:3.10-slim

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o requirements.txt e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do projeto
COPY . .

# Expor a porta que o Flask usará
EXPOSE 5000

# Comando para iniciar o aplicativo
CMD ["python", "app.py"]