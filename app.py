import json
import logging

from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request, redirect

from src.repository_cache.produto_db import ProdutoDBService
from src.services.integracao_pedidos_service import processar_e_enviar_pedidos
from src.services.produto_integracao_fakestore_service import ProdutoService

app = Flask(__name__)

app.config['SWAGGER_UI_JSONEDITOR'] = True  # Ativa o editor JSON no Swagger UI
app.config['SWAGGER'] = {
    'title': 'API Produtos_Lojas7 integração com a fakestore',
    'uiversion': 3
}
swagger = Swagger(app)

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

produto_service = ProdutoService(url='https://fakestoreapi.com/products')
DB_PATH = 'src/model/data/produtos.db'
produto_db_service = ProdutoDBService(DB_PATH)

# Carrega o schema do arquivo JSON
with open('src/model/data/produto_schema.json', 'r') as f:
    produto_schemas = json.load(f)

# Carrega o schema do arquivo JSON de envio de product_ids
with open('src/model/data/product_ids_schema.json', 'r') as f:
    product_ids_schema = json.load(f)


@app.route('/produtos/category/<string:category>', methods=['GET'])
@swag_from({
    'summary': 'Lista produtos por categoria',
    'parameters': [
        {
            'name': 'category',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Categoria dos produtos'
        }
    ],
    'responses': {
        '200': {
            'description': 'Lista de produtos por categoria',
            'schema': produto_schemas['ListagemProdutos']
        },
        '404': {
            'description': 'Categoria não encontrada'
        }
    }
})
def listar_produtos_por_categoria(category: str):
    """Rota para listar produtos por categoria."""
    try:
        logger.info(f'Listando produtos da categoria: {category}')
        lista_produtos = produto_service.listar_produtos_por_categoria(category)
        if lista_produtos:
            with produto_db_service:
                produto_db_service.insert_or_replace_produtos(lista_produtos)
            return jsonify(lista_produtos.dict())
        else:
            return jsonify({'message': 'Categoria não encontrada ou erro na requisição.'}), 404
    except Exception as e:
        logger.error(f'Erro ao listar produtos da categoria {category}: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/produtos', methods=['GET'])
@swag_from({
    'summary': 'Lista todos os produtos',
    'responses': {
        '200': {
            'description': 'Lista de produtos',
            'schema': produto_schemas['ListagemProdutos']
        }
    }
})
def listar_produtos():
    """Rota para listar todos os produtos."""
    try:
        logger.info('Listando todos os produtos.')
        lista_produtos = produto_service.listar_produtos()
        if lista_produtos:
            with produto_db_service:
                produto_db_service.insert_or_replace_produtos(lista_produtos)
                return jsonify(lista_produtos.dict())
        else:
            return jsonify({'message': 'Erro na requisição.'}), 500

    except Exception as e:
        logger.error(f'Erro ao listar produtos: {e}')
    return jsonify({'error': str(e)}), 500


@app.route('/produtos/<int:produto_id>', methods=['GET'])
@swag_from({
    'summary': 'Busca um produto por ID',
    'parameters': [
        {
            'name': 'produto_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID do produto'
        }
    ],
    'responses': {
        '200': {
            'description': 'Produto encontrado',
            'schema': produto_schemas['Produto']
        },
        '404': {
            'description': 'Produto não encontrado'
        }
    }
})
def buscar_produto(produto_id: int):
    """Rota para buscar um produto por ID."""
    try:
        logger.info(f'Buscando produto com ID: {produto_id}')
        produto = produto_service.buscar_produto_por_id(produto_id)
        if produto:
            with produto_db_service:
                produto_db_service.insert_or_replace_produto(produto)
            return jsonify(produto.dict())
        else:
            return jsonify({'message': 'Produto não encontrado ou erro na requisição.'}), 404
    except Exception as e:
        logger.error(f'Erro ao buscar produto com ID {produto_id}: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/produtos/preco', methods=['GET'])
@swag_from({
    'summary': 'Lista produtos por faixa de preço',
    'parameters': [
        {
            'name': 'preco_min',
            'in': 'query',
            'type': 'number',
            'required': True,
            'description': 'Preço mínimo'
        },
        {
            'name': 'preco_max',
            'in': 'query',
            'type': 'number',
            'required': True,
            'description': 'Preço máximo'
        }
    ],
    'responses': {
        '200': {
            'description': 'Lista de produtos por faixa de preço',
            'schema': produto_schemas['ListagemProdutos']
        }
    }
})
def listar_produtos_por_preco():
    """Rota para listar produtos por faixa de preço."""
    try:
        preco_min = request.args.get('preco_min', type=float)
        preco_max = request.args.get('preco_max', type=float)

        logger.info(f'Listando produtos com preço entre {preco_min} e {preco_max}')
        lista_produtos = produto_service.listar_produtos_por_preco(preco_min, preco_max)

        if lista_produtos:
            with produto_db_service:
                produto_db_service.insert_or_replace_produtos(lista_produtos)
            return jsonify(lista_produtos.dict())
        else:
            return jsonify({'message': 'Nenhum produto encontrado na faixa de preço especificada.'}), 404

    except Exception as e:
        logger.error(f'Erro ao listar produtos por faixa de preço: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/')
def redirect_to_swagger():
    """Redireciona para a página do Swagger UI."""
    return redirect('/apidocs/')


@app.route('/produtos_enviar', methods=['POST'])
@swag_from({
    'summary': 'Cria um novo pedido',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'content': {
                'application/json': {
                    'schema': product_ids_schema.get('Product_ids', {}),  # Usa o schema carregado
                    'example': product_ids_schema.get('example', {})  # Adiciona a chave 'example'
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Produtos selecionados e enviados com sucesso',
            'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}},
            'examples': {
                'application/json': {'message': 'Produtos selecionados e enviados com sucesso.'}
            }
        },
        '400': {
            'description': 'Corpo da requisição inválido ou IDs não encontrados',
            'schema': {'type': 'object', 'properties': {'error': {'type': 'string'}}},
            'examples': {
                'application/json': {'error': 'Corpo da requisição JSON inválido.'}
            }
        },
        '500': {
            'description': 'Erro ao acessar o banco de dados ou ao enviar para o endpoint externo',
            'schema': {'type': 'object', 'properties': {'error': {'type': 'string'}}},
            'examples': {
                'application/json': {'error': 'Erro ao acessar o banco de dados.'}
            }
        }
    }
})
def enviar_produtos_selecionados():
    """
    Recebe uma lista de IDs de produtos e inicia o processo de consulta e envio.
    """
    logger.info("Recebida requisição POST em /enviar_produtos_selecionados")
    logger.debug(f"Headers da requisição: {request.headers}")  # Adicione esta linha
    data = request.get_json()
    logger.debug(f"Dados da requisição: {data}")
    if not data or 'product_ids' not in data or not isinstance(data['product_ids'], list):
        logger.warning("Corpo da requisição JSON inválido.")
        return jsonify({'error': 'Corpo da requisição JSON inválido'}), 400

    product_ids = data['product_ids']
    logger.debug(f"IDs de produtos recebidos: {product_ids}")
    if not all(isinstance(pid, int) for pid in product_ids):
        logger.warning("IDs de produtos devem ser inteiros.")
        return jsonify({'error': 'IDs de produtos devem ser inteiros'}), 400

    return processar_e_enviar_pedidos(product_ids)


if __name__ == '__main__':
    with app.app_context():
        with produto_db_service:
            produto_db_service.create_tables()
        app.run(host='0.0.0.0', port=5001)
