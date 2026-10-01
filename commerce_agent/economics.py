"""Unit-economics arithmetic. NOT a forecast."""
import math

def net_per_sale(price, production_cost, platform, fees):
    f = fees[platform]
    if platform == "etsy":
        cut = price * (f["transaction_pct"] + f["payment_pct"]) / 100 + f["payment_fixed"] + f["listing_fee"]
    else:
        cut = price * f["pct"] / 100 + f["fixed"]
    return round(price - cut - production_cost, 2), round(cut, 2)

def table(price, production_cost, platform, fees, targets):
    net, cut = net_per_sale(price, production_cost, platform, fees)
    rows = [{"target": t, "sales_needed": (math.ceil(t / net) if net > 0 else None)} for t in targets]
    return {"price": price, "platform_fees": cut, "production_cost": production_cost, "net_per_sale": net, "rows": rows}
