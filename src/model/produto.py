from pydantic import BaseModel
from typing import List


class Produto(BaseModel):
    id: int
    title: str
    description: str
    price: float
    category: str
    image: str

    def to_dict(self):
        return self.dict()


class ListagemProdutos(BaseModel):
    produtos: List[Produto]

    def to_dict(self):
        return {'produtos': [produto.to_dict() for produto in self.produtos]}
