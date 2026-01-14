# Gemini Code Generator

🤖 Uma aplicação que utiliza a API do Google Gemini para gerar código de forma iterativa, com validação e correção automática de erros.

## 🎯 Características

- **Geração de Código por Etapas**: Quebra projetos complexos em etapas gerenciáveis
- **Validação Automática**: Compila/valida o código gerado automaticamente
- **Correção Iterativa**: Envia erros de volta ao Gemini para correção automática
- **Múltiplas Linguagens**: Suporta Python, JavaScript, TypeScript, Java, C#, PHP, Go, Rust, Ruby
- **Configurável**: Paths customizáveis para compiladores e interpretadores via `.env`
- **CLI Interativo**: Interface de linha de comando com feedback visual
- **Retry Logic**: Tenta corrigir erros automaticamente até o limite configurado

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Chave de API do Google Gemini ([obter aqui](https://makersuite.google.com/app/apikey))
- Compiladores/interpretadores das linguagens que deseja usar (Python, Node.js, etc.)

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd alsti
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
python -m src.main init
```

Ou copie manualmente:
```bash
cp .env.example .env
```

4. Edite o arquivo `.env` e adicione sua chave da API do Gemini:
```env
GEMINI_API_KEY=sua_chave_api_aqui
```

5. Configure os paths dos compiladores/interpretadores no `.env` (opcional, usa defaults do sistema):
```env
PYTHON_PATH=/usr/bin/python3
NODE_PATH=/usr/bin/node
# ... outros paths
```

## 💻 Uso

### Modo 1: Gerar projeto a partir de arquivo JSON

Crie um arquivo JSON descrevendo seu projeto (veja `examples/` para referência):

```json
{
  "description": "Descrição geral do projeto",
  "language": "python",
  "steps": [
    {
      "name": "Nome da Etapa",
      "description": "Descrição detalhada do que gerar",
      "language": "python",
      "filename": "output.py",
      "dependencies": []
    }
  ]
}
```

Execute a geração:
```bash
python -m src.main generate examples/simple_calculator.json
```

### Modo 2: Geração Rápida (arquivo único)

Para gerar rapidamente um único arquivo:
```bash
python -m src.main quick \
  --description "Create a REST API with Flask for user management" \
  --language python \
  --filename api.py
```

## 📁 Estrutura do Projeto

```
alsti/
├── .env.example              # Template de configuração
├── .env                      # Configuração (não commitado)
├── requirements.txt          # Dependências Python
├── README.md                # Este arquivo
├── src/                     # Código-fonte
│   ├── __init__.py
│   ├── main.py              # CLI principal
│   ├── config.py            # Gerenciamento de configuração
│   ├── gemini_client.py     # Cliente da API Gemini
│   ├── code_validator.py    # Validador/compilador
│   └── code_generator.py    # Orquestrador
├── examples/                # Projetos de exemplo
│   ├── simple_calculator.json
│   └── sales_control_system.json
└── generated/               # Código gerado (criado automaticamente)
```

## 🎮 Exemplos

### Exemplo 1: Calculadora Simples

```bash
python -m src.main generate examples/simple_calculator.json
```

Este exemplo gera:
- `calculator.py`: Módulo com operações aritméticas
- `test_calculator.py`: Testes unitários
- `calculator_cli.py`: Interface de linha de comando

### Exemplo 2: Sistema de Controle de Vendas

```bash
python -m src.main generate examples/sales_control_system.json
```

Este exemplo gera um sistema completo de controle de vendas com:
- Modelos de banco de dados (usuários, produtos, fornecedores, etc.)
- Serviços de autenticação e CRUD
- API REST com Flask
- Gestão de inventário e vendas

### Exemplo 3: Geração Rápida

```bash
python -m src.main quick \
  -d "Create a FastAPI endpoint for user authentication with JWT" \
  -l python \
  -f auth_api.py
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

#### Configuração da API Gemini
- `GEMINI_API_KEY`: Sua chave da API (obrigatório)
- `GEMINI_MODEL`: Modelo a usar (padrão: `gemini-1.5-pro`)

#### Paths das Linguagens
Configure os paths para os compiladores/interpretadores:
- `PYTHON_PATH`, `PIP_PATH`
- `NODE_PATH`, `NPM_PATH`, `NPX_PATH`
- `JAVA_PATH`, `JAVAC_PATH`, `MAVEN_PATH`, `GRADLE_PATH`
- `DOTNET_PATH`
- `PHP_PATH`, `COMPOSER_PATH`
- `GO_PATH`
- `CARGO_PATH`, `RUSTC_PATH`
- `RUBY_PATH`, `GEM_PATH`, `BUNDLE_PATH`

#### Configuração de Saída
- `GENERATED_CODE_DIR`: Diretório para código gerado (padrão: `./generated`)
- `MAX_RETRY_ATTEMPTS`: Máximo de tentativas de correção (padrão: `5`)
- `VALIDATION_TIMEOUT`: Timeout para validação em segundos (padrão: `30`)

#### Logging
- `LOG_LEVEL`: Nível de log (padrão: `INFO`)
- `LOG_FILE`: Arquivo de log (padrão: `./gemini-code-generator.log`)

## 🔄 Como Funciona

1. **Planejamento**: Você define as etapas do projeto em um arquivo JSON
2. **Geração**: O Gemini gera o código para cada etapa
3. **Validação**: O código é compilado/executado para verificar erros
4. **Correção**: Se houver erros, são enviados de volta ao Gemini
5. **Iteração**: O processo se repete até o código estar válido ou atingir o limite de tentativas
6. **Salvamento**: O código válido é salvo no diretório configurado

## 🛠️ Desenvolvimento

### Estrutura de Módulos

- **config.py**: Carrega e gerencia configurações do `.env`
- **gemini_client.py**: Interage com a API do Gemini
- **code_validator.py**: Valida código compilando/executando
- **code_generator.py**: Orquestra o processo de geração com retry logic
- **main.py**: Interface CLI usando Click

### Adicionar Suporte para Nova Linguagem

1. Adicione a linguagem ao enum `Language` em `code_validator.py`
2. Implemente método `_validate_<language>` em `CodeValidator`
3. Adicione paths necessários no `.env.example`

## 📝 Formato do Arquivo de Projeto

```json
{
  "description": "Descrição geral do projeto",
  "language": "python",
  "steps": [
    {
      "name": "Nome descritivo",
      "description": "O que gerar (quanto mais detalhado, melhor)",
      "language": "python",
      "filename": "caminho/arquivo.py",
      "dependencies": ["arquivo1.py", "arquivo2.py"]
    }
  ]
}
```

### Campos:

- **description**: Descrição geral do projeto (contexto para o Gemini)
- **language**: Linguagem padrão (pode ser sobrescrita por etapa)
- **steps**: Array de etapas a executar em ordem
  - **name**: Nome da etapa (para display)
  - **description**: Prompt detalhado para o Gemini
  - **language**: Linguagem específica desta etapa
  - **filename**: Nome/caminho do arquivo a ser gerado
  - **dependencies**: Arquivos de outras etapas (para contexto)

## 🐛 Troubleshooting

### Erro: "GEMINI_API_KEY not found"
- Verifique se o arquivo `.env` existe
- Verifique se `GEMINI_API_KEY` está definido no `.env`
- Certifique-se de que a chave não está como `your_gemini_api_key_here`

### Erro: "Command not found" ou "Validation failed"
- Verifique se o compilador/interpretador está instalado
- Configure o path correto no `.env`
- Teste manualmente: `python3 --version`, `node --version`, etc.

### Código gerado continua falhando
- Aumente `MAX_RETRY_ATTEMPTS` no `.env`
- Torne a descrição da etapa mais específica e detalhada
- Verifique os logs em `gemini-code-generator.log`
- Considere quebrar a etapa em etapas menores

### Timeout na validação
- Aumente `VALIDATION_TIMEOUT` no `.env`
- Simplifique o código gerado (etapas menores)

## 📄 Licença

Ver arquivo [LICENSE](LICENSE).

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Adicionar suporte para novas linguagens
- Melhorar a documentação

## 🔗 Links Úteis

- [Google Gemini API](https://ai.google.dev/)
- [Obter chave API](https://makersuite.google.com/app/apikey)
- [Documentação do Gemini](https://ai.google.dev/docs)

## ✨ Exemplos de Uso

### Criar um CRUD completo
```bash
python -m src.main quick \
  -d "Create a complete CRUD API with FastAPI for a todo list application, including SQLAlchemy models, Pydantic schemas, and all CRUD endpoints" \
  -l python \
  -f todo_api.py
```

### Gerar testes automatizados
```bash
python -m src.main quick \
  -d "Create comprehensive pytest tests for a user authentication module" \
  -l python \
  -f test_auth.py
```

### Criar um microserviço
```bash
python -m src.main generate examples/microservice.json
```

## 📊 Logs e Debugging

Os logs são salvos em `gemini-code-generator.log` e incluem:
- Tentativas de geração
- Erros de compilação
- Respostas do Gemini
- Validações

Para aumentar o nível de detalhe dos logs, altere no `.env`:
```env
LOG_LEVEL=DEBUG
```

---

Feito com ❤️ usando Google Gemini AI
