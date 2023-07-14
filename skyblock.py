import requests
from main import *

hypixel_api_url = "https://api.hypixel.net"


class Produto:
    def __init__(self, nome, mediaVenda, mediaCompra):
        self.nome = nome
        self.mediaVenda = mediaVenda
        self.mediaCompra = mediaCompra
        self.diferenca = mediaCompra - mediaVenda
        if mediaVenda != 0:
            self.porcDiferenca = (100 * self.diferenca) / mediaVenda
        else:
            self.porcDiferenca = 0


def update_bazaar_entries():
    key = {'API-Key': hypixel_api}
    x = requests.get(hypixel_api_url + "/skyblock/bazaar", json=key).json()

    controle = 0
    lista_produtos = []
    for product in x['products']:
        mediaVendaVar = x['products'][product]['quick_status']['sellPrice']
        mediaCompraVar = x['products'][product]['quick_status']['buyPrice']
        produto = Produto(product, mediaVendaVar, mediaCompraVar)

        cursor = my_database.cursor()
        cursor.execute(f"SELECT * FROM public.\"Produtos\" WHERE nome=\'{product}\'")
        for row in cursor.fetchall():
            lista_produtos.append(row[0])
        cursor.close()

        if product.split('_')[0] == "ENCHANTMENT":
            controle += 1
            print(f"Produto N° {controle} ({product}) ignorado.")
            continue

        if not lista_produtos.__contains__(product):
            cursor = my_database.cursor()
            cursor.execute(
                f"INSERT INTO public.\"Produtos\" (nome, \"mediaCompra\", \"mediaVenda\", diferenca, \"porcDiferenca\") VALUES (\'{product}\', {mediaCompraVar}, {mediaVendaVar}, {produto.diferenca}, {produto.porcDiferenca})")
            cursor.close()
        else:
            cursor = my_database.cursor()
            cursor.execute(
                f"UPDATE public.\"Produtos\" SET \"mediaCompra\"={mediaCompraVar}, \"mediaVenda\"={mediaVendaVar}, diferenca={produto.diferenca}, \"porcDiferenca\"={produto.porcDiferenca} WHERE nome=\'{product}\'")
            cursor.close()
            controle += 1
            print(f"Produto N° {controle} ({product}) atualizado.")


    my_database.commit()
    cursor.close()


update_bazaar_entries()
