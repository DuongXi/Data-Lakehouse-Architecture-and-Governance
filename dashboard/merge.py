import pandas as pd
import os

def merge_gold_data(directory="gold_data"):
    # Ở đây tôi dùng Parquet vì nó giữ đúng định dạng kiểu dữ liệu hơn
    fact_sales = pd.read_parquet(os.path.join(directory, "fact_sales.parquet"))
    dim_customer = pd.read_parquet(os.path.join(directory, "dim_customer.parquet"))
    dim_product = pd.read_parquet(os.path.join(directory, "dim_product.parquet"))

    print("[*] Đang tiến hành gộp dữ liệu...")

    merged_df = pd.merge(fact_sales, dim_product, on='product_id', how='left')

    final_df = pd.merge(merged_df, dim_customer, on='customer_id', how='left')

    print(f"[*] Số dòng sau khi gộp: {len(final_df)}")
    
    output_path = os.path.join(directory, "final_gold_viz.csv")
    final_df.to_csv(output_path, index=False)
    
    print(f"[+] Thành công! File sẵn sàng tại: {output_path}")
    print("\n--- Bản xem trước dữ liệu phẳng (Flat Table) ---")
    print(final_df.head())

if __name__ == "__main__":
    merge_gold_data()