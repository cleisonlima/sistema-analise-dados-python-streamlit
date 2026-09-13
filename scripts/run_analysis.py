from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
from src.analysis import load_and_clean_data, monthly_summary, category_summary, product_summary

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    output = root / "outputs"
    output.mkdir(exist_ok=True)
    data, stats = load_and_clean_data()
    monthly, categories, products = monthly_summary(data), category_summary(data), product_summary(data)
    plt.style.use("dark_background")
    figure, axes = plt.subplots(2, 2, figsize=(14, 9), facecolor="#0b1030")
    for axis in axes.flat: axis.set_facecolor("#141a4b")
    axes[0, 0].plot(monthly.month, monthly.revenue, color="#16d9ff", linewidth=2.5)
    axes[0, 1].bar(categories.category, categories.revenue, color="#16d6a4")
    axes[1, 0].barh(products.product.iloc[::-1], products.revenue.iloc[::-1], color="#f52bbf")
    axes[1, 1].scatter(data.loc[data.is_completed, "quantity"], data.loc[data.is_completed, "net_revenue"], alpha=.4, color="#f59e0b")
    figure.tight_layout(); figure.savefig(output / "visao_geral.png", dpi=160, facecolor=figure.get_facecolor())
    print(stats)
