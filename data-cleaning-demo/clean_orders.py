#!/usr/bin/env python3
"""
数据清洗 Demo
=============
用 pandas 清洗一份模拟的电商订单"脏数据"：
缺失值 / 重复行 / 日期格式混乱 / 金额格式混乱 / 大小写空格不一致 / 异常值 / 字段错位

清洗步骤：
1. 去重（按 order_id）
2. 缺失值处理：邮箱缺失填充占位，产品/金额缺失标记
3. 日期统一为 YYYY-MM-DD
4. 金额统一为 float（处理 $1,234.56 和 1.234,56 两种格式）
5. 字符串规范化：去空格、统一大小写
6. 异常值过滤：负数/离谱金额
7. 字段错位修复（邮箱在名字列时交换）

输出：
- data/cleaned_orders.csv  清洗后数据
- data/cleaning_report.txt 清洗报告（前后对比）
"""
import pandas as pd

INPUT = "data/dirty_orders.csv"
OUTPUT = "data/cleaned_orders.csv"
REPORT = "data/cleaning_report.txt"


def parse_amount(value: str) -> float:
    """解析多种金额格式：$1,234.56 / 1.234,56 / 1234.56"""
    if pd.isna(value) or str(value).strip().lower() == "unknown":
        return pd.NA
    s = str(value).strip().replace("$", "").replace(" ", "")
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):  # 1.234,56 -> 欧洲格式
            s = s.replace(".", "").replace(",", ".")
        else:  # $1,234.56 -> 美式
            s = s.replace(",", "")
    elif "," in s:  # 1,234 或 1,234,56
        parts = s.split(",")
        if len(parts[-1]) == 2 and len(parts) == 2:  # 1,56 视作小数
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return pd.NA


def parse_date(value: str):
    """统一日期为 YYYY-MM-DD"""
    if pd.isna(value):
        return pd.NA
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return pd.to_datetime(s, format=fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return pd.NA


def main():
    df = pd.read_csv(INPUT, dtype=str)
    n_before = len(df)
    report = []
    report.append(f"输入行数: {n_before}")

    # ---- 1. 去重 ----
    df = df.drop_duplicates()
    report.append(f"去重后行数: {len(df)} (删除 {n_before - len(df)} 行)")

    # ---- 7. 字段错位修复（邮箱含 @ 且在名字列）----
    mask = df["customer_name"].str.contains("@", na=False)
    if mask.any():
        df.loc[mask, ["customer_name", "customer_email"]] = df.loc[
            mask, ["customer_email", "customer_name"]
        ].values
        report.append(f"字段错位修复: {mask.sum()} 行")

    # ---- 2. 缺失值处理 ----
    df["customer_email"] = df["customer_email"].replace(
        {r"^\s*$": pd.NA, "N/A": pd.NA, "unknown": pd.NA}, regex=True
    )
    df["customer_email"] = df["customer_email"].fillna("(missing)")
    n_missing = (df["customer_email"] == "(missing)").sum()
    report.append(f"邮箱缺失: {n_missing} 行 (填充占位)")

    # 金额 unknown -> 缺失
    df["amount"] = df["amount"].replace({"unknown": pd.NA})

    # ---- 3. 日期统一 ----
    df["order_date"] = df["order_date"].apply(parse_date)

    # ---- 4. 金额统一 ----
    df["amount"] = df["amount"].apply(parse_amount)

    # ---- 5. 规范化 ----
    df["order_id"] = df["order_id"].str.strip().str.upper()
    df["customer_name"] = df["customer_name"].str.strip()
    df["country"] = df["country"].str.strip().str.upper()
    df["product"] = df["product"].str.strip().str.lower()
    df["customer_email"] = df["customer_email"].str.strip().str.lower()

    # ---- 6. 异常值 ----
    n_before_anomaly = len(df)
    df = df[df["amount"] > 0]
    df = df[df["amount"] < 100000]
    n_removed = n_before_anomaly - len(df)
    report.append(f"异常金额过滤: {n_removed} 行 (负数/离谱值)")

    # 排序
    df = df.sort_values("order_id").reset_index(drop=True)

    report.append(f"输出行数: {len(df)}")
    report.append(f"输出列数: {len(df.columns)}")
    report.append("")
    report.append("=== 清洗后样例 ===")
    report.append(df.head(8).to_string(index=False))

    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print("\n".join(report))
    print(f"\n已保存: {OUTPUT} / {REPORT}")


if __name__ == "__main__":
    main()
