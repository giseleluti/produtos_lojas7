import requests
import logging
from src.model.produto import Produto, ListagemProdutos

# Configuração do logger (se necessário, mova para app.py)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProdutoService:
    def __init__(self, url: str):
        self.url = url

    def _buscar_produtos(self, url: str) -> ListagemProdutos:
        """Função auxiliar para buscar produtos da API."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            produtos_json = response.json()
            return ListagemProdutos(produtos=[Produto(**produto) for produto in produtos_json])
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return ListagemProdutos(produtos=[])
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return ListagemProdutos(produtos=[])

    def _buscar_produto(self, url: str) -> Produto:
        """Função auxiliar para buscar um produto da API."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            produto_json = response.json()
            return Produto(**produto_json)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None

    def listar_produtos(self) -> ListagemProdutos:
        return self._buscar_produtos(self.url)

    def buscar_produto_por_id(self, id: int) -> Produto:
        url_id = f'{self.url}/{id}'
        return self._buscar_produto(url_id)

    def listar_produtos_por_categoria(self, category: str) -> ListagemProdutos:
        url_categoria = f'{self.url}/category/{category}'
        return self._buscar_produtos(url_categoria)

    def listar_produtos_por_preco(self, preco_min: float, preco_max: float) -> ListagemProdutos:
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            produtos_json = response.json()
            todos_produtos = [Produto(**produto) for produto in produtos_json]
            produtos_filtrados = [
                produto for produto in todos_produtos
                if preco_min <= produto.price <= preco_max
            ]
            return ListagemProdutos(produtos=produtos_filtrados)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return ListagemProdutos(produtos=[])
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return ListagemProdutos(produtos=[])
