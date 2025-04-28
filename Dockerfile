# Usar imagem base com Python
FROM python:3.11-slim

# Criar diretório de trabalho
WORKDIR /app

# Copiar os arquivos do projeto
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta que o Flask usa
EXPOSE 5000
