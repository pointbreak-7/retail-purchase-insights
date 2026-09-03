"""
Generates PNG chart exports for the Retail Purchase Insights project, standing
in for the Tableau dashboard. Recreates the same cleaning steps as
Retail_Purchase_insight.ipynb and answers the 10 business questions from
customer_behavior:PostgreSQL.sql using matplotlib/seaborn.

Run: python3 generate_visuals.py
Output: PNG files written to ./visuals/
"""

import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------------------
# Palette (validated categorical + status colors)
# ---------------------------------------------------------------------------
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
MAGENTA = "#e87ba4"
GREEN = "#008300"
VIOLET = "#4a3aa7"
RED = "#e34948"
CATEGORICAL = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visuals")
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "text.color": INK_PRIMARY,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_SECONDARY,
        "xtick.color": INK_MUTED,
        "ytick.color": INK_MUTED,
        "axes.grid": False,
        "font.size": 11,
    }
)


def style_axes(ax, y_grid=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    if y_grid:
        ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines["bottom"].set_visible(True)


def bar_labels(ax, bars, fmt="{:,.0f}", offset_frac=0.01, horizontal=False):
    ymax = ax.get_ylim()[1] if not horizontal else ax.get_xlim()[1]
    for b in bars:
        if horizontal:
            w = b.get_width()
            ax.text(
                w + ymax * offset_frac,
                b.get_y() + b.get_height() / 2,
                fmt.format(w),
                va="center",
                ha="left",
                fontsize=10,
                color=INK_PRIMARY,
            )
        else:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + ymax * offset_frac,
                fmt.format(h),
                va="bottom",
                ha="center",
                fontsize=10,
                color=INK_PRIMARY,
            )


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {path}")


# ---------------------------------------------------------------------------
# Load + clean (mirrors the notebook)
# ---------------------------------------------------------------------------
df = pd.read_csv("customer_shopping_behavior.csv")

df["Review Rating"] = df.groupby("Category")["Review Rating"].transform(
    lambda x: x.fillna(x.median())
)

df.columns = df.columns.str.lower().str.replace(" ", "_")
df = df.rename(columns={"purchase_amount_(usd)": "purchase_amount"})
df = df.drop(columns=["promo_code_used"])

labels = ["Young Adult", "Adult", "Middle Aged", "Senior"]
df["age_group"] = pd.qcut(df["age"], q=4, labels=labels)

frequency_mapping = {
    "Fortnightly": 14,
    "Weekly": 7,
    "Monthly": 30,
    "Quarterly": 90,
    "Bi-Weekly": 14,
    "Annually": 365,
    "Every 3 Months": 90,
}
df["purchase_frequency_days"] = df["frequency_of_purchases"].map(frequency_mapping)

age_order = labels

# ---------------------------------------------------------------------------
# Q1. Total revenue: Male vs Female
# ---------------------------------------------------------------------------
rev_gender = df.groupby("gender")["purchase_amount"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6, 4.5))
bars = ax.bar(rev_gender.index, rev_gender.values, color=[BLUE, ORANGE], width=0.55)
style_axes(ax)
ax.set_ylabel("Total revenue (USD)")
ax.set_title("Total Revenue by Gender", fontsize=13, fontweight="bold", loc="left")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:,.0f}K"))
bar_labels(ax, bars, fmt="${:,.0f}")
save(fig, "01_revenue_by_gender.png")

# ---------------------------------------------------------------------------
# Q2. Discount customers spending above average
# ---------------------------------------------------------------------------
avg_amount = df["purchase_amount"].mean()
above_avg_discount = df[
    (df["discount_applied"] == "Yes") & (df["purchase_amount"] >= avg_amount)
]
counts = pd.Series(
    {
        "All discount users": (df["discount_applied"] == "Yes").sum(),
        "...spending >= average": len(above_avg_discount),
    }
)
fig, ax = plt.subplots(figsize=(6, 4.5))
bars = ax.barh(counts.index[::-1], counts.values[::-1], color=[AQUA, BLUE], height=0.5)
style_axes(ax, y_grid=False)
ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
ax.set_axisbelow(True)
ax.set_xlabel("Customers")
ax.set_title(
    "Discount Users Spending at/above Average Purchase\n"
    f"(overall average purchase = ${avg_amount:,.2f})",
    fontsize=13,
    fontweight="bold",
    loc="left",
)
bar_labels(ax, bars, fmt="{:,.0f}", horizontal=True)
save(fig, "02_discount_above_average_spend.png")

# ---------------------------------------------------------------------------
# Q3. Top 5 products by average review rating
# ---------------------------------------------------------------------------
top_rated = (
    df.groupby("item_purchased")["review_rating"].mean().sort_values(ascending=False).head(5)
)
fig, ax = plt.subplots(figsize=(6, 4.5))
bars = ax.barh(top_rated.index[::-1], top_rated.values[::-1], color=BLUE, height=0.55)
style_axes(ax, y_grid=False)
ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
ax.set_axisbelow(True)
ax.set_xlim(0, 5)
ax.set_xlabel("Average review rating (out of 5)")
ax.set_title("Top 5 Products by Average Review Rating", fontsize=13, fontweight="bold", loc="left")
bar_labels(ax, bars, fmt="{:.2f}", horizontal=True)
save(fig, "03_top5_rated_products.png")

# ---------------------------------------------------------------------------
# Q4. Standard vs Express average purchase amount
# ---------------------------------------------------------------------------
shipping = (
    df[df["shipping_type"].isin(["Standard", "Express"])]
    .groupby("shipping_type")["purchase_amount"]
    .mean()
)
fig, ax = plt.subplots(figsize=(6, 4.5))
bars = ax.bar(shipping.index, shipping.values, color=[BLUE, ORANGE], width=0.5)
style_axes(ax)
ax.set_ylabel("Average purchase amount (USD)")
ax.set_title(
    "Average Purchase Amount: Standard vs Express Shipping",
    fontsize=13,
    fontweight="bold",
    loc="left",
)
bar_labels(ax, bars, fmt="${:,.2f}")
save(fig, "04_shipping_type_avg_purchase.png")

# ---------------------------------------------------------------------------
# Q5. Subscribers vs non-subscribers: count, avg spend, total revenue
# ---------------------------------------------------------------------------
sub = df.groupby("subscription_status").agg(
    total_customers=("customer_id", "count"),
    avg_spend=("purchase_amount", "mean"),
    total_revenue=("purchase_amount", "sum"),
)
sub = sub.reindex(["Yes", "No"])
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
metrics = [
    ("total_customers", "Customers", "{:,.0f}"),
    ("avg_spend", "Avg spend (USD)", "${:,.2f}"),
    ("total_revenue", "Total revenue (USD)", "${:,.0f}"),
]
for ax, (col, title, fmt) in zip(axes, metrics):
    bars = ax.bar(["Subscriber", "Non-subscriber"], sub[col].values, color=[BLUE, ORANGE], width=0.55)
    style_axes(ax)
    ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
    bar_labels(ax, bars, fmt=fmt)
fig.suptitle("Subscriber vs Non-Subscriber Behavior", fontsize=14, fontweight="bold", x=0.02, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.93])
save(fig, "05_subscriber_comparison.png")

# ---------------------------------------------------------------------------
# Q6. Top 5 products by discount rate
# ---------------------------------------------------------------------------
discount_rate = (
    df.assign(discount_flag=(df["discount_applied"] == "Yes").astype(int))
    .groupby("item_purchased")["discount_flag"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
    .head(5)
)
fig, ax = plt.subplots(figsize=(6, 4.5))
bars = ax.barh(discount_rate.index[::-1], discount_rate.values[::-1], color=ORANGE, height=0.55)
style_axes(ax, y_grid=False)
ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
ax.set_axisbelow(True)
ax.set_xlabel("% of purchases with a discount applied")
ax.set_title("Top 5 Products by Discount Rate", fontsize=13, fontweight="bold", loc="left")
bar_labels(ax, bars, fmt="{:.1f}%", horizontal=True)
save(fig, "06_top5_discount_rate_products.png")

# ---------------------------------------------------------------------------
# Q7. Customer segmentation: New / Returning / Loyal
# ---------------------------------------------------------------------------
def segment(prev):
    if prev == 1:
        return "New"
    if 2 <= prev <= 10:
        return "Returning"
    return "Loyal"


seg_counts = df["previous_purchases"].apply(segment).value_counts().reindex(
    ["Loyal", "Returning", "New"]
)
fig, ax = plt.subplots(figsize=(6, 4.5))
bars = ax.bar(seg_counts.index, seg_counts.values, color=[BLUE, ORANGE, AQUA], width=0.5)
style_axes(ax)
ax.set_ylabel("Customers")
ax.set_title("Customer Segmentation by Purchase History", fontsize=13, fontweight="bold", loc="left")
bar_labels(ax, bars, fmt="{:,.0f}")
save(fig, "07_customer_segmentation.png")

# ---------------------------------------------------------------------------
# Q8. Top 3 products per category
# ---------------------------------------------------------------------------
item_counts = (
    df.groupby(["category", "item_purchased"])["customer_id"]
    .count()
    .rename("total_orders")
    .reset_index()
)
item_counts["item_rank"] = item_counts.groupby("category")["total_orders"].rank(
    method="first", ascending=False
)
top3 = item_counts[item_counts["item_rank"] <= 3].sort_values(["category", "item_rank"])

categories = sorted(top3["category"].unique())
fig, axes = plt.subplots(1, len(categories), figsize=(4 * len(categories), 4.5), sharey=False)
for ax, cat, color in zip(axes, categories, CATEGORICAL):
    sub_df = top3[top3["category"] == cat].sort_values("total_orders")
    bars = ax.barh(sub_df["item_purchased"], sub_df["total_orders"], color=color, height=0.5)
    style_axes(ax, y_grid=False)
    ax.xaxis.grid(True, color=GRIDLINE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_title(cat, fontsize=11, fontweight="bold", loc="left")
    bar_labels(ax, bars, fmt="{:,.0f}", horizontal=True)
fig.suptitle("Top 3 Most Purchased Products per Category", fontsize=14, fontweight="bold", x=0.02, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.92])
save(fig, "08_top3_products_per_category.png")

# ---------------------------------------------------------------------------
# Q9. Repeat buyers (previous_purchases > 5) — subscription split
# ---------------------------------------------------------------------------
repeat = df[df["previous_purchases"] > 5]
repeat_sub = repeat["subscription_status"].value_counts().reindex(["Yes", "No"])
fig, ax = plt.subplots(figsize=(6, 4.5))
bars = ax.bar(["Subscriber", "Non-subscriber"], repeat_sub.values, color=[BLUE, ORANGE], width=0.5)
style_axes(ax)
ax.set_ylabel("Repeat buyers (previous purchases > 5)")
ax.set_title("Are Repeat Buyers More Likely to Subscribe?", fontsize=13, fontweight="bold", loc="left")
bar_labels(ax, bars, fmt="{:,.0f}")
save(fig, "09_repeat_buyers_subscription.png")

# ---------------------------------------------------------------------------
# Q10. Revenue by age group
# ---------------------------------------------------------------------------
rev_age = df.groupby("age_group", observed=True)["purchase_amount"].sum().reindex(age_order)
fig, ax = plt.subplots(figsize=(7, 4.5))
bars = ax.bar(rev_age.index, rev_age.values, color=BLUE, width=0.55)
style_axes(ax)
ax.set_ylabel("Total revenue (USD)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:,.0f}K"))
ax.set_title("Revenue Contribution by Age Group", fontsize=13, fontweight="bold", loc="left")
bar_labels(ax, bars, fmt="${:,.0f}")
save(fig, "10_revenue_by_age_group.png")

# ---------------------------------------------------------------------------
# Bonus. Revenue by category + subscription donut (README headline stats)
# ---------------------------------------------------------------------------
rev_cat = df.groupby("category")["purchase_amount"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6.5, 4.5))
bars = ax.bar(rev_cat.index, rev_cat.values, color=CATEGORICAL[: len(rev_cat)], width=0.55)
style_axes(ax)
ax.set_ylabel("Total revenue (USD)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:,.0f}K"))
ax.set_title("Total Revenue by Product Category", fontsize=13, fontweight="bold", loc="left")
bar_labels(ax, bars, fmt="${:,.0f}")
save(fig, "11_revenue_by_category.png")

sub_status = df["subscription_status"].value_counts().reindex(["No", "Yes"])
fig, ax = plt.subplots(figsize=(5.5, 5.5))
wedges, _ = ax.pie(
    sub_status.values,
    colors=[BLUE, ORANGE],
    startangle=90,
    wedgeprops=dict(width=0.38, edgecolor=SURFACE, linewidth=2),
)
pct = sub_status / sub_status.sum() * 100
ax.legend(
    wedges,
    [f"{label} — {p:.0f}%" for label, p in zip(["Non-subscriber", "Subscriber"], pct.values)],
    loc="center",
    frameon=False,
    fontsize=12,
)
ax.set_title("Subscription Status Distribution", fontsize=13, fontweight="bold")
save(fig, "12_subscription_status_donut.png")

print("\nAll charts written to:", OUT_DIR)
