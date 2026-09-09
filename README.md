# Gestão de Equipamentos — CRUD em Flask

Site simples em Python (Flask + SQLite) para **Criar, Ver, Editar e Apagar** registros.

## Como rodar localmente (sem container)

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Rode o servidor:
   ```
   python app.py
   ```

3. Abra no navegador: http://localhost:5000

O banco de dados (`dados.db`) é criado automaticamente na primeira execução.

## Como rodar em container (local)

```
docker build -t equipamentos-app .
docker run -p 8000:8000 equipamentos-app
```

Acesse em http://localhost:8000

## Deploy no Azure

### Opção 1 — Azure Container Registry (ACR) + Container Apps (recomendado)

```bash
# 1. Login
az login

# 2. Criar grupo de recursos (se ainda não tiver)
az group create --name rg-equipamentos --location brazilsouth

# 3. Criar o Container Registry
az acr create --resource-group rg-equipamentos --name acrequipamentos --sku Basic

# 4. Buildar e enviar a imagem direto para o ACR (não precisa de docker local)
az acr build --registry acrequipamentos --image equipamentos-app:v1 .

# 5. Criar o Container App
az containerapp env create --name env-equipamentos --resource-group rg-equipamentos --location brazilsouth

az containerapp create \
  --name equipamentos-app \
  --resource-group rg-equipamentos \
  --environment env-equipamentos \
  --image acrequipamentos.azurecr.io/equipamentos-app:v1 \
  --target-port 8000 \
  --ingress external \
  --registry-server acrequipamentos.azurecr.io
```

### Opção 2 — Azure Container Instances (mais simples, sem escalonamento)

```bash
az acr build --registry acrequipamentos --image equipamentos-app:v1 .

az container create \
  --resource-group rg-equipamentos \
  --name equipamentos-container \
  --image acrequipamentos.azurecr.io/equipamentos-app:v1 \
  --registry-login-server acrequipamentos.azurecr.io \
  --ports 8000 \
  --dns-name-label equipamentos-app \
  --cpu 1 --memory 1
```

### ⚠️ Importante — persistência de dados

O SQLite (`dados.db`) fica dentro do container. **Sempre que o container reiniciar
ou for recriado, os dados são perdidos**, pois o sistema de arquivos é efêmero.

Para persistir os dados em produção, escolha uma opção:

- **Mais simples:** montar um Azure Files como volume no Container App/ACI e apontar
  o `DB_PATH` para esse volume.
- **Mais robusto (recomendado para produção real):** trocar o SQLite por um banco
  gerenciado, como **Azure Database for PostgreSQL**. Isso exige trocar `sqlite3`
  por uma biblioteca como `psycopg2` no `app.py` — posso te ajudar a fazer essa
  migração se quiser.

## Estrutura

- `app.py` — servidor Flask com as rotas de CRUD
- `templates/` — páginas HTML (listagem, formulário)
- `dados.db` — banco SQLite (criado automaticamente, não persiste no container)
- `Dockerfile` — build da imagem para deploy
- `.dockerignore` — arquivos ignorados no build da imagem

## Como adaptar para outro tema

O tema atual é "equipamentos" (nome, tipo, localização, status, última leitura),
mas a estrutura é genérica. Para mudar de assunto (ex: clientes, produtos, tarefas):

1. Em `app.py`, altere o nome da tabela `equipamentos` e os campos no `CREATE TABLE`.
2. Ajuste os campos nos formulários (`INSERT`, `UPDATE`) para bater com as novas colunas.
3. Em `templates/index.html` e `templates/form.html`, troque os nomes dos campos exibidos.

Toda a lógica de criar/ler/editar/apagar continua igual — só os campos mudam.
