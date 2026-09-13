from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = ROOT / "data" / "raw" / "vendas_ecommerce.csv"
PROCESSED_DATA = ROOT / "data" / "processed" / "vendas_tratadas.csv"


def load_and_clean_data(path=RAW_DATA):
    data = pd.read_csv(path)
    raw_rows = len(data)
    missing_ages = int(data["customer_age"].isna().sum())
    duplicated_rows = int(data.duplicated(subset="order_id").sum())
    data = data.drop_duplicates(subset="order_id").copy()
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    for column in ["customer_age", "quantity", "unit_price", "discount", "satisfaction_score"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data["discount"] = data["discount"].fillna(0).clip(0, 1)
    for column in ["gender", "state", "city", "category", "product", "payment_method", "status"]:
        data[column] = data[column].astype("string").str.strip().str.title()
    data["customer_age"] = data["customer_age"].fillna(data["customer_age"].median()).round().astype(int)
    data["gross_revenue"] = data["quantity"] * data["unit_price"]
    data["discount_value"] = data["gross_revenue"] * data["discount"]
    data["net_revenue"] = data["gross_revenue"] - data["discount_value"]
    data["month"] = data["order_date"].dt.to_period("M").dt.to_timestamp()
    data["is_completed"] = data["status"].eq("Concluido")
    data = data.dropna(subset=["order_id", "order_date", "quantity", "unit_price"])
    data = data[(data["quantity"] > 0) & (data["unit_price"] > 0)].sort_values("order_date").reset_index(drop=True)
    PROCESSED_DATA.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(PROCESSED_DATA, index=False, encoding="utf-8")
    return data, {"raw_rows": raw_rows, "clean_rows": len(data), "duplicates_removed": duplicated_rows, "missing_ages_filled": missing_ages}


def completed(data):
    return data[data["is_completed"]]


def calculate_kpis(data):
    sales = completed(data)
    return {"revenue": float(sales["net_revenue"].sum()), "orders": len(sales), "customers": sales["customer_id"].nunique(), "average_ticket": float(sales["net_revenue"].mean()) if len(sales) else 0, "satisfaction": float(sales["satisfaction_score"].mean()) if len(sales) else 0}


def monthly_summary(data):
    return completed(data).groupby("month", as_index=False).agg(revenue=("net_revenue", "sum"), orders=("order_id", "nunique"), customers=("customer_id", "nunique"))


def category_summary(data):
    return completed(data).groupby("category", as_index=False).agg(revenue=("net_revenue", "sum"), orders=("order_id", "nunique"), quantity=("quantity", "sum"), satisfaction=("satisfaction_score", "mean")).sort_values("revenue", ascending=False)


def state_summary(data):
    return completed(data).groupby(["state", "city"], as_index=False).agg(revenue=("net_revenue", "sum"), orders=("order_id", "nunique")).sort_values("revenue", ascending=False)


def product_summary(data, limit=10):
    return completed(data).groupby(["product", "category"], as_index=False).agg(revenue=("net_revenue", "sum"), quantity=("quantity", "sum"), orders=("order_id", "nunique")).sort_values("revenue", ascending=False).head(limit)


def rfm_summary(data):
    sales = completed(data)
    reference = sales["order_date"].max() + pd.Timedelta(days=1)
    rfm = sales.groupby("customer_id").agg(recency=("order_date", lambda x: (reference - x.max()).days), frequency=("order_id", "nunique"), monetary=("net_revenue", "sum")).reset_index()
    for column in ["recency", "frequency", "monetary"]:
        rfm[f"{column}_score"] = pd.qcut(rfm[column].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["segment"] = np.select([(rfm.recency_score >= 3) & (rfm.frequency_score >= 3), (rfm.recency_score >= 3) & (rfm.monetary_score >= 3), (rfm.recency_score <= 2) & (rfm.frequency_score >= 3), rfm.recency_score <= 2], ["Clientes fieis", "Alto valor", "Em risco", "Inativos"], default="Oportunidades")
    return rfm.sort_values("monetary", ascending=False)
