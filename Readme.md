# 📚 Processamento de Bases Bibliométricas para VOSviewer

Este projeto fornece uma solução automatizada para mesclar e preparar bases de dados bibliográficas da Web of Science e Scopus para uso no software VOSviewer.

## 🎯 Objetivo

Mesclar arquivos exportados da Web of Science e Scopus em uma única base de dados formatada corretamente para análise bibliométrica no VOSviewer, resolvendo problemas comuns de formatação de datas e duplicatas.

## 📋 Pré-requisitos

### Software Necessário
- **Python 3.8 ou superior**
- **Pandas** (biblioteca Python)
- **VOSviewer** (para análise final)

### Arquivos de Entrada
- `wos_data.txt` - Exportado da Web of Science (formato Tab-delimited)
- `scopus_data.csv` - Exportado da Scopus (formato CSV)

## 🛠️ Instalação

### 1. Instalar Python
**Windows/Mac:**
- Baixe em: https://www.python.org/downloads/
- **Importante:** Marque "Add Python to PATH" durante a instalação

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Instalar Pandas
Abra o Prompt de Comando/Terminal e execute:
```bash
pip install pandas
```

### 3. Verificar Instalação
```bash
python --version
pip show pandas
```

## 📁 Estrutura de Arquivos

```
pasta_do_projeto/
├── bibliofusion.py          # Script principal
├── wos_data.txt             # Exportado da Web of Science
├── scopus_data.csv          # Exportado da Scopus
├── base_bibliometrica_apenas_ano.csv  # Arquivo final (gerado)
└── README.md                # Este arquivo
```

## 🚀 Como Usar

### 1. Preparar os Arquivos
- Exporte os dados da Web of Science como **"Plain Text"** ou **"Tab-delimited"**
- Exporte os dados da Scopus como **CSV**
- Coloque os arquivos na mesma pasta do script

### 2. Executar o Script

**Opção A - Duplo clique:**
- Salve o código como `bibliofusion.py`
- Dê duplo clique no arquivo

**Opção B - Terminal:**
```bash
cd caminho/para/sua/pasta
python bibliofusion.py
```

### 3. Saída Esperada
```
🔧 Iniciando processo de mesclagem das bases...
📥 Carregando bases de dados...
✅ Web of Science: XXX registros
✅ Scopus: XXX registros
🔄 Combinando bases...
✅ Duplicatas removidas: XX
📊 Total antes da limpeza: XXX registros
📅 Corrigindo formato das datas...
✅ Registros com datas inválidas removidos: X
📊 Total final após limpeza: XXX registros
📅 Anos únicos encontrados: [2019, 2020, 2021, 2022, 2023, 2024]
🎉 Arquivo salvo com sucesso: base_bibliometrica_apenas_ano.csv
```

## 📊 Arquivos Gerados

### Arquivo Final: `base_bibliometrica_apenas_ano.csv`
- **Formato:** CSV compatível com VOSviewer
- **Codificação:** UTF-8 com BOM
- **Colunas principais:**
  - `Title` - Título do artigo
  - `Authors` - Autores
  - `Year` - Ano de publicação (apenas ano inteiro)
  - `Source title` - Nome da revista/fonte
  - `DOI` - Identificador digital
  - `Abstract` - Resumo
  - `Cited by` - Citações
  - `References` - Referências
  - `Fonte` - Origem dos dados (Web of Science/Scopus)

## 🔧 Funcionalidades do Script

### ✅ Processamento Automático
- **Mesclagem** das bases Web of Science e Scopus
- **Remoção de duplicatas** por DOI e título
- **Correção de datas** - extrai apenas o ano (remove decimais)
- **Padronização** de colunas para VOSviewer

### ✅ Resolução de Problemas Comuns
- **Datas decimais:** Converte `2024.6` → `2024`
- **Encoding:** Usa UTF-8 com BOM para caracteres especiais
- **Valores vazios:** Preenche campos missing
- **Formato inconsistente:** Padroniza nomes de colunas

## 🎮 Usando no VOSviewer

### Passo a Passo:
1. Abra o **VOSviewer**
2. **File** → **Create** → **Create a map based on bibliographic data**
3. Selecione **"Read data from reference manager files"**
4. Escolha o arquivo `base_bibliometrica_apenas_ano.csv`
5. No mapeamento de campos, certifique-se que:
   - `Year` está mapeado para o campo de ano
   - `Title` para título
   - `Authors` para autores

### ⚠️ Solução de Problemas no VOSviewer

**Problema:** "Year field not recognized"
**Solução:** Verifique se a coluna Year contém apenas números inteiros

**Problema:** "Encoding error"
**Solução:** O script já usa UTF-8 com BOM, que resolve a maioria dos problemas de acentuação

**Problema:** "Duplicate records"
**Solução:** O script já remove duplicatas automaticamente

## 📈 Estatísticas Geradas

O script fornece relatório completo:
- Total de registros por fonte
- Período temporal coberto
- Duplicatas removidas
- Registros com datas inválidas

## 🔄 Personalização

### Modificar Colunas
Edite a lista `colunas_essenciais_vosviewer` no script para incluir/excluir colunas:

```python
colunas_essenciais_vosviewer = [
    'Title', 'Authors', 'Year', 'Source title', 'DOI', 
    'Abstract', 'Cited by', 'References', 'Fonte'
]
```

### Alterar Período Temporal
Modifique os limites no código:
```python
merged_df = merged_df[merged_df[coluna_ano_encontrada] >= 2000]  # Ano mínimo
merged_df = merged_df[merged_df[coluna_ano_encontrada] <= 2024]  # Ano máximo
```

## 🆘 Troubleshooting

### Erros Comuns e Soluções

**"Arquivo não encontrado"**
- Verifique se os arquivos estão na mesma pasta do script
- Confirme os nomes: `wos_data.txt` e `scopus_data.csv`

**"python não é reconhecido"**
- Reinstale Python marcando "Add Python to PATH"
- Ou use `python3` no lugar de `python`

**"Módulo pandas não encontrado"**
- Execute: `pip install pandas`

**Datas ainda com decimais no VOSviewer**
- Execute o script novamente - ele foi atualizado para resolver este problema

## 📞 Suporte

### Para Dúvidas:
1. Verifique se todos os pré-requisitos estão instalados
2. Confirme que os arquivos de entrada estão no formato correto
3. Execute o script novamente - muitos problemas são resolvidos com nova execução

### Logs de Execução:
O script fornece feedback detalhado durante o processamento. Se encontrar erros, compartilhe a mensagem completa do terminal.

## 📄 Licença

Este script é disponibilizado para uso acadêmico e de pesquisa.

---

**✍️ Desenvolvido para** facilitar análises bibliométricas e revisões sistemáticas da literatura.

**🕐 Última atualização:** Dezembro 2024

**✅ Status:** Testado e validado com bases reais Web of Science e Scopus