import sqlite3
from typing import List, Dict

from src.model.produto import Produto, ListagemProdutos


class ProdutoDBService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        with open('src/model/data/schema.sql', 'r') as f:
            self.conn.executescript(f.read())

    def insert_or_replace_produto(self, produto: Produto):
        self.conn.execute(
            'INSERT OR REPLACE INTO produtos (id, title, description, price, category, image) VALUES (?, ?, ?, ?, ?, ?)',
            (produto.id, produto.title, produto.description, produto.price, produto.category, produto.image))
        self.conn.commit()

    def insert_or_replace_produtos(self, produtos: ListagemProdutos):
        for produto in produtos.produtos:
            self.insert_or_replace_produto(produto)

    def buscar_produtos_por_ids(self, product_ids: List[int]) -> List[Dict]:
        """
        Busca produtos no banco de dados pelos IDs fornecidos,
        retornando uma lista de dicionários com id, title e price.
        Retorna uma lista vazia se nenhum produto for encontrado ou
        se a lista de product_ids estiver vazia.
        """
        produtos_encontrados: List[Produto] = []
        if not product_ids:
            return []

        with self:
            cursor = self.conn.cursor()
            placeholders = ', '.join('?' * len(product_ids))
            query = f"SELECT id, title, description, price, category, image FROM produtos WHERE id IN ({placeholders})"
            cursor.execute(query, product_ids)
            rows = cursor.fetchall()
            if not rows:
                return []
            for row in rows:
                produto_data = dict(zip(['id', 'title', 'description', 'price', 'category', 'image'], row))
                produto = Produto(**produto_data)
                produtos_encontrados.append(produto)

        # Serializa a lista de objetos Produto para uma lista de dicionários
        produtos_dict = [
            {
                "id": produto.id,
                "title": produto.title,
                "price": produto.price
            }
            for produto in produtos_encontrados
        ]
        return produtos_dict
