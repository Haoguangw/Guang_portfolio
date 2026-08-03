#!/usr/bin/env python3
"""
生成一份模拟"脏数据"（演示用）
模拟一家电商的客户订单记录，包含常见数据质量问题：
- 缺失值（空单元格、'N/A'、'unknown'）
- 重复行
- 日期格式混乱（YYYY-MM-DD / MM/DD/YYYY / DD.MM.YYYY）
- 金额格式混乱（$1,234.56 / 1234.56 / 1.234,56）
- 大小写/空格不一致
- 异常值（负数价格、超长记录）
- 字段错位（名字和邮箱互换的脏记录）
"""
import csv
import random

random.seed(42)

# 基础正确数据（10 条）
clean_base = [
    ["ORD-001", "2024-03-15", "Alice Chen", "alice.chen@example.com", "CN", "Laptop", 899.99],
    ["ORD-002", "2024-03-16", "Bob Wang", "bob.wang@example.com", "US", "Mouse", 24.50],
    ["ORD-003", "2024-03-17", "Carol Li", "carol.li@example.com", "CN", "Keyboard", 59.90],
    ["ORD-004", "2024-03-18", "David Liu", "david.liu@example.com", "US", "Monitor", 199.00],
    ["ORD-005", "2024-03-19", "Eva Zhang", "eva.zhang@example.com", "CN", "Webcam", 45.30],
    ["ORD-006", "2024-03-20", "Frank Sun", "frank.sun@example.com", "US", "Headset", 89.99],
    ["ORD-007", "2024-03-21", "Grace Wu", "grace.wu@example.com", "CN", "USB Hub", 29.90],
    ["ORD-008", "2024-03-22", "Henry Zhao", "henry.zhao@example.com", "US", "SSD 1TB", 129.00],
    ["ORD-009", "2024-03-23", "Ivy Huang", "ivy.huang@example.com", "CN", "GPU", 499.99],
    ["ORD-010", "2024-03-24", "Jack Lin", "jack.lin@example.com", "US", "Router", 79.50],
]

rows = []
for r in clean_base:
    rows.append(r)

# 注入脏数据
dirty_rows = list(rows)

# 1. 缺失值（3 种形式）
dirty_rows.append(["ORD-011", "2024-03-25", "Kate Ma", "", "CN", "Cable", 12.99])           # 空邮箱
dirty_rows.append(["ORD-012", "2024-03-26", "Leo Xu", "N/A", "US", "Stand", 19.99])         # N/A 邮箱
dirty_rows.append(["ORD-013", "2024-03-27", "Mia Zhou", "mia.zhou@example.com", "CN", "", "unknown"])  # 产品缺失+金额 unknown

# 2. 重复行（完全重复 + 部分重复）
dirty_rows.append(["ORD-001", "2024-03-15", "Alice Chen", "alice.chen@example.com", "CN", "Laptop", 899.99])  # 完全重复
dirty_rows.append(["ORD-002", "2024-03-16", "Bob Wang", "bob.wang@example.com", "US", "Mouse", 24.50])        # 完全重复

# 3. 日期格式混乱
dirty_rows.append(["ORD-014", "03/28/2024", "Nick Ye", "nick.ye@example.com", "US", "Camera", 320.00])
dirty_rows.append(["ORD-015", "29.03.2024", "Olivia Tan", "olivia.tan@example.com", "CN", "Mic", 55.00])

# 4. 金额格式混乱
dirty_rows.append(["ORD-016", "2024-03-30", "Paul He", "paul.he@example.com", "US", "Chair", "$1,234.56"])
dirty_rows.append(["ORD-017", "2024-03-31", "Queen Yu", "queen.yu@example.com", "CN", "Desk", "1.234,56"])

# 5. 大小写/空格不一致
dirty_rows.append(["ord-018", "2024-04-01", "  rick fan  ", "RICK.FAN@EXAMPLE.COM", "cn", "Lamp", 39.99])
dirty_rows.append(["ORD-019", "2024-04-02", "Sam Gao", "sam.gao@example.com", "US", "speaker", 69.00])

# 6. 异常值
dirty_rows.append(["ORD-020", "2024-04-03", "Tina Luo", "tina.luo@example.com", "CN", "Phone", -599.99])  # 负数价格
dirty_rows.append(["ORD-021", "2024-04-04", "Uma Shi", "uma.shi@example.com", "US", "Tablet", 9999999.99])  # 离谱价格

# 7. 字段错位（邮箱写在名字列）
dirty_rows.append(["ORD-022", "2024-04-05", "victor.kim@example.com", "Victor Kim", "US", "Drone", 150.00])

# 写脏数据文件
with open("data/dirty_orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "order_date", "customer_name", "customer_email", "country", "product", "amount"])
    writer.writerows(dirty_rows)

print(f"脏数据已生成: data/dirty_orders.csv  ({len(dirty_rows)} 行)")
