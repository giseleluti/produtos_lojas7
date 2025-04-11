# API de Produtos

Esta é uma API Flask para gerenciar produtos, integrada com a API EXTERNA Fake Store.

#O objetivo é integrar com a API `Fakestore` para busca de "produtos importados" 
realizar um cache e disponibilizar para que o cliente faça requisições para a API de pedidos.

``
https://fakestoreapi.com/products``
``

## Rotas Disponíveis

* **POST /produtos_enviar**:  envia a requisição para a API de pedidos com a lista de produtos.

* **GET /produtos**: Lista todos os produtos.

* **GET /produtos/category/{category}**: Lista produtos por categoria.
* **GET /produtos/{produto_id}**: Busca um produto por ID.
* **GET /produtos/preco**: Lista produtos por faixa de preço.
    * Parâmetros de consulta: `preco_min`, `preco_max`

* **Documentação Swagger:** O Flasgger foi integrado para gerar automaticamente a documentação da API no formato Swagger UI, acessível em `/apidocs/`. A documentação inclui detalhes sobre os endpoints, parâmetros, corpos de requisição e respostas.
* **Logging:** A biblioteca `logging` do Python foi configurada para registrar informações, avisos e erros durante a execução da API, auxiliando na depuração e monitoramento.


## Requisitos

* Python 3.9 ou superior
* Pip (gerenciador de pacotes do Python)
* Docker (opcional, para execução em contêiner)

## Dependências

As seguintes bibliotecas Python são necessárias para executar a API:
* pydantic~=2.10.6
* requests~=2.32.3
* flask~=3.0.3
* flasgger~=0.9.7.1


## Instalação

1.  Clone o repositório.
e depois acesse em

    ```bash
    cd <produtos_lojas7>
    ```

2.  Crie um ambiente virtual (opcional, mas recomendado):

    ```bash
    python -m venv venv
    ```

3.  Ative o ambiente virtual:

    * No Windows:

        ```bash
        venv\Scripts\activate
        ```

    * No macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

4.  Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

## Execução

1.  Execute a aplicação:

    ```bash
    python app.py
    ```

2.  A API estará disponível em `http://127.0.0.1:5001`.

## Acesso à Documentação Swagger

* Acesse a documentação Swagger em `http://127.0.0.1:5001/apidocs/`.


Construa a imagem Docker:
Bash
Copiar o código
docker build -t produtos_lojas7 .
3. 
Execute o container:
Bash
Copiar o código
docker run -p 5001:5001 produtos_lojas7 
4. 
Acesse a aplicação em http://localhost:5001
