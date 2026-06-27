#!/usr/bin/env python3
"""
自动选股脚本 —— 从 A 股全市场筛选股价 ≤ 12 元的股票，随机选取 5 只输出。

用于 GitHub Actions daily_analysis 工作流的自动选股步骤。

输出格式：逗号分隔的股票代码，例如 "000001,600519,000002"
"""

import random
import sys

try:
    import akshare as ak
except ImportError:
    print("❌ 请先安装 akshare: pip install akshare", file=sys.stderr)
    sys.exit(1)

MAX_PRICE = 12.0        # 股价上限
TARGET_COUNT = 5        # 目标选股数
PRICE_COLUMNS = ["最新价", "现价"]  # akshare 可能使用的列名


def main():
    print("📡 正在获取 A 股全市场行情...", file=sys.stderr)

    try:
        df = ak.stock_zh_a_spot_em()
    except Exception as e:
        print(f"❌ 获取行情失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  共获取 {len(df)} 只股票", file=sys.stderr)

    # 确定价格列名
    price_col = None
    for col in PRICE_COLUMNS:
        if col in df.columns:
            price_col = col
            break

    if price_col is None:
        print(f"❌ 未找到价格列，可用列: {list(df.columns)}", file=sys.stderr)
        sys.exit(1)

    # 筛选股价 ≤ MAX_PRICE 的股票
    df_filtered = df[df[price_col].notna() & (df[price_col] <= MAX_PRICE)].copy()

    print(f"  股价 ≤ {MAX_PRICE} 元的股票: {len(df_filtered)} 只", file=sys.stderr)

    if len(df_filtered) == 0:
        print(f"❌ 没有找到符合条件的股票", file=sys.stderr)
        sys.exit(1)

    # 随机选取 TARGET_COUNT 只
    sample_size = min(TARGET_COUNT, len(df_filtered))
    sampled = df_filtered.sample(n=sample_size, random_state=random.randint(0, 9999))

    # 提取股票代码，取后6位（akshare 可能返回如 "000001" 格式）
    stock_codes = []
    for code in sampled["代码"]:
        code_str = str(code).strip()
        # 如果代码是 6 位纯数字，保留原样；否则取后 6 位
        if code_str.isdigit() and len(code_str) == 6:
            stock_codes.append(code_str)
        elif len(code_str) >= 6 and code_str[-6:].isdigit():
            stock_codes.append(code_str[-6:])
        else:
            stock_codes.append(code_str)

    # 输出
    result = ",".join(stock_codes)
    print(result)

    # 打印选股明细到 stderr 供日志查看
    print(f"\n✅ 本次选股结果 ({len(stock_codes)} 只):", file=sys.stderr)
    for i, (_, row) in enumerate(sampled.iterrows()):
        name = row.get("名称", "?")
        price = row.get(price_col, "?")
        code = stock_codes[i] if i < len(stock_codes) else row.get("代码", "?")
        print(f"  {i+1}. {code} {name}  ¥{price}", file=sys.stderr)


if __name__ == "__main__":
    main()
