import logging
from typing import Dict, List, Tuple

import requests
from flask import jsonify

from src.repository_cache.produto_db import ProdutoDBService

logger = logging.getLogger(__name__)
ENDPOINT_EXTERNO_URL = "http://pedidos_lojas7:5003/pedidos/criar"
db_path = 'src/model/data/produtos.db'
produto_db_service = ProdutoDBService(db_path)


def _buscar_produtos_do_banco(product_ids: list) -> List[Dict]:
    """Busca produtos no banco de dados pelos IDs fornecidos."""
    logger.info(f"Consultando banco de dados para IDs: {product_ids}")
    with produto_db_service:
        produtos_db: List[Dict] = produto_db_service.buscar_produtos_por_ids(product_ids)
    logger.info(f"Encontrados {len(produtos_db)} produtos no banco de dados.")
    return produtos_db


def _formatar_payload_para_envio(produtos: List[Dict]) -> Dict:
    """Formata a lista de produtos no formato esperado pelo endpoint externo."""
    logger.info(f"Formatando payload para envio com {len(produtos)} produtos.")
    lista_de_produtos_formatada: List[Dict] = []
    for produto in produtos:
        lista_de_produtos_formatada.append({
            "id_produto": produto['id'],
            "title": produto['title'],
            "price": produto['price']
        })
    payload_para_envio = {
        "id_pedido": 0,
        "produtos": lista_de_produtos_formatada
    }
    logger.info(f"Payload para envio: {payload_para_envio}")
    return payload_para_envio


def _enviar_pedido_para_externo(payload: Dict) -> Tuple[jsonify, int]:
    """Envia o payload formatado para o endpoint externo."""
    logger.info(f"Enviando pedido para: {ENDPOINT_EXTERNO_URL}")
    try:
        headers = {'Content-Type': 'application/json'}
        response_externo = requests.post(ENDPOINT_EXTERNO_URL, headers=headers, json=payload)
        response_externo.raise_for_status()
        logger.info(f"Pedido enviado com sucesso. Status da resposta externa: {response_externo.status_code}")
        return jsonify({'message': 'Pedido enviado com sucesso'}), 200
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar pedido para o endpoint externo ({ENDPOINT_EXTERNO_URL}): {e}")
        return jsonify({'error': f'Erro ao enviar pedido para o endpoint externo: {e}'}), 500


def processar_e_enviar_pedidos(product_ids: list):
    """
    Recebe uma lista de IDs de produtos, busca os produtos,
    formata o payload e envia para o endpoint externo.
    """
    logger.info(f"Iniciando processamento e envio de pedidos para IDs: {product_ids}")
    try:
        produtos_db = _buscar_produtos_do_banco(product_ids)

        if not produtos_db:
            logger.warning(f"Nenhum produto encontrado para os IDs: {product_ids}")
            return jsonify({'error': 'Nenhum produto encontrado com os IDs fornecidos'}), 404

        payload_para_envio = _formatar_payload_para_envio(produtos_db)
        return _enviar_pedido_para_externo(payload_para_envio)

    except Exception as e:
        logger.error(f"Erro ao processar e enviar pedido: {e}")
        return jsonify({'error': f'Erro ao processar e enviar pedido: {e}'}), 500
