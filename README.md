# Uma aplicação de Web Scraping para o processo seletivo
Uma aplicação desktop com interface gráfica (GUI) para coletar dados públicos de repositórios do GitHub.

## Recursos
* **GUI:** Uma interface intuitiva construída com a biblioteca nativa `tkinter` do Python.
* **Métodos Duplos de Coleta:**
   * **Web Scraping:** Utiliza Selenium e BeautifulSoup para analisar páginas web.
   * **API REST:** Aproveita a API oficial do GitHub para coletar de dados.
* **Processamento Concorrente:** Emprega multi-threading para buscar dados de múltiplos repositórios simultaneamente sem travar a interface.
* **Atualizações em Tempo Real:** A tabela de resultados é preenchida instantaneamente com marcadores "carregando..." e atualizada conforme cada thread completa sua tarefa.
* **Exportação para CSV:** Salve os dados coletados diretamente em um arquivo CSV com um único clique.

## Instalação
Para executar esta aplicação em sua máquina local, siga estes passos.

### Pré-requisitos
* Python 3.7+
* Navegador Google Chrome instalado (para o web scraper Selenium)

### Instruções de Configuração
1. **Clone o repositório:**

```
git clone <url-do-seu-repositório>
cd <pasta-do-repositório>
```

2. **Crie e ative um ambiente virtual:**
   * **Windows:**

```
python -m venv venv
.\venv\Scripts\activate
```

   * **macOS / Linux:**

```
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências necessárias:**

   * **Windows:**

```
python requirements.py
```

   * **macOS / Linux:**

```
python3 requirements.py
```

Ou faça de forma manual executando o seguinte comando no seu terminal:

```
pip install -r requirements.txt
```

## Como Usar
1. **Execute a aplicação:**

```
python github_scraper_gui.py
```

2. **Adicione Repositórios:**
   * Cole uma URL completa do repositório GitHub (ex: `https://github.com/python/cpython`) no campo de entrada.
   * Clique no botão **"Adicionar à Fila"** ou pressione `Enter`. O caminho do repositório (`proprietário/repo`) aparecerá na lista "Fila de Processamento".
   * Adicione quantos repositórios precisar.

3. **Busque Dados:**
   * Clique em **"Iniciar Busca por API"** para usar a API do GitHub, que é rápida e confiável.
   * Clique em **"Iniciar Scraping"** para usar o web scraper baseado em Selenium.
   * A fila será limpa e a tabela "Resultados" será instantaneamente preenchida com marcadores "carregando...". Conforme os dados de cada repositório são coletados, sua linha será atualizada.

4. **Gerenciar Resultados:**
   * **Salvar em CSV:** Uma vez que a coleta esteja completa, clique em **"Salvar em CSV"** para exportar os dados da tabela de resultados. Uma caixa de diálogo aparecerá, permitindo que você escolha o local e nome do arquivo.
   * **Limpar Resultados:** Clique em **"Limpar Resultados"** para apagar todos os dados da tabela de resultados.
   * **Limpar Fila:** Clique em **"Limpar Fila"** para remover todos os itens da lista antes de iniciar um processo.

## Stack
* **Python:** Linguagem de programação principal.
* **Tkinter:** Para construir a interface gráfica do usuário.
* **Selenium:** Para automação do navegador e web scraping.
* **BeautifulSoup4:** Para análise de conteúdo HTML.
* **Requests:** Para fazer requisições HTTP à API do GitHub.
* **Threading:** Para execução concorrente de tarefas.
