import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

# --- Configuração Inicial ---
SECRET_FILE_PATH = '/etc/secrets/serviceAccountKey.json'

try:
    if not os.path.exists(SECRET_FILE_PATH):
        raise FileNotFoundError(f"O ficheiro da chave secreta não foi encontrado em {SECRET_FILE_PATH}")

    cred = credentials.Certificate(SECRET_FILE_PATH)
    
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        
    db = firestore.client()
    print("Ligação ao Firestore estabelecida com sucesso.")
except Exception as e:
    print(f"ERRO: Não foi possível ligar ao Firestore. Erro: {e}")
    exit()

PRODUCTS_TO_SCRAPE = [
    {"id": "p1", "search_term": "leite mimosa meio gordo"},
    {"id": "p3", "search_term": "maçã golden"},
    {"id": "p14", "search_term": "coca-cola"},
    {"id": "p13", "search_term": "arroz agulha cigala"},
]

# --- Funções do Robô ---
def scrape_prices(search_term):
    """ Simula a busca de preços nos supermercados. """
    print(f"A simular a procura por '{search_term}'...")
    # Numa versão real, aqui estaria a lógica complexa de web scraping.
    base_price = 2.50 + (len(search_term) % 10) * 0.15
    prices = {
        "Continente": round(base_price * 1.05, 2),
        "Pingo Doce": round(base_price * 1.02, 2),
        "Lidl": round(base_price * 0.98, 2),
        "Auchan": round(base_price * 1.06, 2),
    }
    return prices

def update_product_in_db(product_id, prices_data):
    """ Atualiza um produto na base de dados Firestore. """
    try:
        product_ref = db.collection('products').document(product_id)
        product_ref.update({
            'prices': prices_data,
            'last_updated': firestore.SERVER_TIMESTAMP
        })
        print(f"Produto '{product_id}' atualizado com sucesso na base de dados.")
    except Exception as e:
        print(f"ERRO ao atualizar o produto '{product_id}': {e}")

# --- Execução Principal do Robô ---
def run_scraper():
    print("--- INICIANDO ROBÔ DE ATUALIZAÇÃO DE PREÇOS ---")
    
    for product in PRODUCTS_TO_SCRAPE:
        print(f"\nProcessando produto: {product['search_term']} (ID: {product['id']})")
        
        scraped_prices = scrape_prices(product['search_term'])
        
        updated_prices = [
            {"supermarket": name, "price": price} for name, price in scraped_prices.items()
        ]
        
        update_product_in_db(product['id'], updated_prices)

    print("\n--- ATUALIZAÇÃO DE PREÇOS CONCLUÍDA ---")

if __name__ == "__main__":
    run_scraper()
