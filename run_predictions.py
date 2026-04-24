import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
import matplotlib.pyplot as plt

def run_standalone_forecast():
    print("Loading Superstore Data...")
    
    # 1. Load the dataset
    try:
        df = pd.read_csv("Smart_Retail_Ready_Superstore.csv")
    except FileNotFoundError:
        print("Error: Could not find 'Smart_Retail_Ready_Superstore.csv' in this folder.")
        return

    # Ensure Date is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # 2. Show the top products so you can choose one
    print("\n--- Top 5 Products by Quantity Sold ---")
    top_products = df.groupby('Product_Name')['Quantity'].sum().nlargest(5).index.tolist()
    for i, product in enumerate(top_products, 1):
        print(f"{i}. {product}")

    # 3. Select the target product (You can change this string to anything in the list!)
    target_product = "Staples"
    print(f"\nTraining ML Model on: '{target_product}'...")

    # 4. Filter data for the specific product and group by day
    prod_df = (
        df[df["Product_Name"] == target_product]
        .groupby("Date")["Quantity"]
        .sum()
        .reset_index()
        .sort_values("Date")
    )

    if len(prod_df) < 2:
        print(f"Not enough data to train a model for {target_product}.")
        return

    # 5. Feature Engineering (Convert dates to numbers for the math model)
    origin = prod_df["Date"].min()
    prod_df["days_since_start"] = (prod_df["Date"] - origin).dt.days

    X = prod_df[["days_since_start"]].values
    y = prod_df["Quantity"].values

    # 6. Train the Linear Regression Model
    model = LinearRegression()
    model.fit(X, y)

    # 7. Predict the next 30 days
    last_date = prod_df["Date"].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    future_days = [(d - origin).days for d in future_dates]

    raw_preds = model.predict(np.array(future_days).reshape(-1, 1))
    predictions = [max(0, int(round(p))) for p in raw_preds]

    # 8. Print Results
    print("\n✅ --- AI FORECAST RESULTS ---")
    print(f"Total Predicted Demand (Next 30 Days): {sum(predictions)} units")
    print(f"Next 5 Days Breakdown: {predictions[:5]}")

    # 9. Plot the Results Visually
    print("\nGenerating forecast graph... (Close the graph window to end the script)")
    plt.figure(figsize=(12, 6))
    
    # Plot historical data in blue
    plt.plot(prod_df["Date"], y, label="Historical Sales", color="#60a5fa", marker="o", alpha=0.6)
    
    # Plot future predictions in red
    plt.plot(future_dates, predictions, label="30-Day AI Forecast", color="#f97060", linestyle="dashed", linewidth=2)
    
    plt.title(f"Demand Forecast for '{target_product}'", fontsize=16, fontweight="bold")
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Quantity Sold", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    
    # This pops open the window
    plt.show()

if __name__ == "__main__":
    run_standalone_forecast()
