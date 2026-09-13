from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "vendas_ecommerce.csv"


def generate_dataset(rows: int = 720, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    states = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA", "GO", "PE", "CE"]
    cities = {
        "SP": "Sao Paulo", "RJ": "Rio de Janeiro", "MG": "Belo Horizonte",
        "PR": "Curitiba", "RS": "Porto Alegre", "SC": "Florianopolis",
        "BA": "Salvador", "GO": "Goiania", "PE": "Recife", "CE": "Fortaleza",
    }
    products = {
        "Eletronicos": [("Fone Bluetooth", 149.90), ("Smartwatch", 399.90), ("Teclado Mecanico", 289.90)],
        "Casa": [("Cafeteira", 229.90), ("Aspirador Vertical", 599.90), ("Jogo de Panelas", 349.90)],
        "Moda": [("Tenis Casual", 279.90), ("Mochila Urbana", 189.90), ("Jaqueta", 319.90)],
        "Beleza": [("Kit Skincare", 159.90), ("Perfume", 249.90), ("Secador", 199.90)],
        "Esportes": [("Corda de Pular", 59.90), ("Colchonete", 99.90), ("Garrafa Termica", 129.90)],
    }
        
    categories = rng.choice(list(products), size=rows, p=[0.29, 0.22, 0.20, 0.15, 0.14])
    selected_products = [products[category][rng.integers(0, len(products[category]))] for category in categories]
    states_selected = rng.choice(states, size=rows, p=[0.25, 0.14, 0.13, 0.11, 0.09, 0.08, 0.07, 0.05, 0.05, 0.03])
    quantities = rng.choice([1, 2, 3, 4], size=rows, p=[0.58, 0.27, 0.11, 0.04])
    statuses = rng.choice(["Concluido", "Concluido", "Concluido", "Cancelado", "Em processamento"], size=rows)
    discounts = rng.choice([0, 0.05, 0.10, 0.15, 0.20], size=rows, p=[0.32, 0.24, 0.27, 0.12, 0.05])
    customer_ids = rng.integers(1001, 1241, size=rows)
    ages = rng.integers(18, 71, size=rows).astype(float)
    ages[rng.choice(rows, size=28, replace=False)] = np.nan

    data = pd.DataFrame({
        "order_id": [f"PED-{100000 + index}" for index in range(rows)],
        "order_date": rng.choice(dates, size=rows),
        "customer_id": [f"CLI-{value}" for value in customer_ids],
        "customer_age": ages,
        "gender": rng.choice(["F", "M", "Outro"], size=rows, p=[0.48, 0.45, 0.07]),
        "state": states_selected,
        "city": [cities[state] for state in states_selected],
        "category": categories,
        "product": [item[0] for item in selected_products],
        "quantity": quantities,
        "unit_price": [item[1] for item in selected_products],
        "discount": discounts,
        "payment_method": rng.choice(["Cartao", "Pix", "Boleto", "Carteira digital"], size=rows, p=[0.47, 0.31, 0.12, 0.10]),
        "status": statuses,
        "satisfaction_score": rng.choice([1, 2, 3, 4, 5], size=rows, p=[0.03, 0.07, 0.20, 0.40, 0.30]),
    })
    data["order_date"] = pd.to_datetime(data["order_date"]).dt.strftime("%Y-%m-%d")

    # Simula problemas comuns de uma base recebida de um sistema legado.
    data.loc[[4, 11, 19], "category"] = [" eletronicos ", "CASA", "moda"]
    data.loc[[7, 22], "state"] = [" sp ", "rj"]
    data.loc[[30, 31], "status"] = ["cancelado", "CONCLUIDO"]
    data = pd.concat([data, data.iloc[[8, 41, 108]]], ignore_index=True)
    return data


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_dataset()
    frame.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"Dataset gerado em {OUTPUT} com {len(frame)} linhas brutas.")
