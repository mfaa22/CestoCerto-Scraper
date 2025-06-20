import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# --- Configuração Inicial ---

# CORREÇÃO: Vamos ler a chave diretamente do ficheiro, que é um método mais robusto no Render.
SECRET_FILE_PATH = '/etc/secrets/serviceAccountKey.json'

try:
    # Verifica se o ficheiro da chave secreta existe
    if not os.path.exists(SECRET_FILE_PATH):
        raise FileNotFoundError(f"O ficheiro da chave secreta não foi encontrado em {SECRET_FILE_PATH}")

    cred = credentials.Certificate(SECRET_FILE_PATH)
    
    # Evita inicializar a app múltiplas vezes se o script for chamado mais de uma vez
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        
    db = firestore.client()
    print("Ligação ao Firestore estabelecida com sucesso.")
except Exception as e:
    print(f"ERRO: Não foi possível ligar ao Firestore. Verifique a configuração do Secret File. Erro: {e}")
    exit()

# Lista de produtos a procurar (pode ser expandida)
# Numa versão avançada, esta lista poderia vir da própria base de dados.
PRODUCTS_TO_SCRAPE = [
    {"id": "p1", "search_term": "leite mimosa meio gordo"},
    {"id": "p3", "search_term": "maçã golden"},
    {"id": "p14", "search_term": "coca-cola"},
    {"id": "p13", "search_term": "arroz agulha cigala"},
]

# --- Funções do Robô ---

def scrape_continente(search_term):
    """ Simula a busca de um preço no Continente. """
    print(f"A procurar '{search_term}' no Continente...")
    # Lógica de scraping para o Continente iria aqui.
    # Como exemplo, retornamos um preço simulado.
    price = 1.99 + (len(search_term) % 10) * 0.1 # Varia o preço para simulação
    return round(price, 2)

def scrape_pingodoce(search_term):
    """ Simula a busca de um preço no Pingo Doce. """
    print(f"A procurar '{search_term}' no Pingo Doce...")
    # Lógica de scraping para o Pingo Doce iria aqui.
    price = 1.95 + (len(search_term) % 10) * 0.11
    return round(price, 2)

def update_product_in_db(product_id, prices_data):
    """ Atualiza um produto na base de dados Firestore. """
    try:
        product_ref = db.collection('products').document(product_id)
        product_ref.update({
            'prices': prices_data,
            'last_updated': datetime.utcnow()
        })
        print(f"Produto '{product_id}' atualizado com sucesso na base de dados.")
    except Exception as e:
        print(f"ERRO ao atualizar o produto '{product_id}': {e}")

# --- Execução Principal do Robô ---

def run_scraper():
    print("--- INICIANDO ROBÔ DE ATUALIZAÇÃO DE PREÇOS ---")
    
    for product in PRODUCTS_TO_SCRAPE:
        print(f"\nProcessando produto: {product['search_term']} (ID: {product['id']})")
        
        # Simula a recolha de preços dos vários supermercados
        price_continente = scrape_continente(product['search_term'])
        price_pingodoce = scrape_pingodoce(product['search_term'])
        
        # Prepara a estrutura de dados para guardar na base de dados
        # Adicione outros supermercados aqui conforme necessário
        updated_prices = [
            {"supermarket": "Continente", "price": price_continente},
            {"supermarket": "Pingo Doce", "price": price_pingodoce},
            # Exemplo estático para outros supermercados
            {"supermarket": "Lidl", "price": round(price_continente * 0.98, 2)},
            {"supermarket": "Auchan", "price": round(price_pingodoce * 1.02, 2)},
        ]
        
        # Envia os preços atualizados para a base de dados
        update_product_in_db(product['id'], updated_prices)

    print("\n--- ATUALIZAÇÃO DE PREÇOS CONCLUÍDA ---")

if __name__ == "__main__":
    run_scraper()
