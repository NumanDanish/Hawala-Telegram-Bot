# Made-up practice rates: how many AFN for 1 unit of each currency
RATES_TO_AFN = {
    "USD": 70.0,
    "EUR": 76.0,
    "PKR": 0.25,
    "AFN": 1.0,
}

FEE_PERCENT = 0.01      # 1% fee
MIN_FEE_AFN = 150       # minimum fee, in afghani


def calculate(amount: float, currency: str):
    currency = currency.upper()
    rate = RATES_TO_AFN.get(currency)
    if rate is None:
        return None

    amount_afn = amount * rate
    fee_afn = max(amount_afn * FEE_PERCENT, MIN_FEE_AFN)
    fee = fee_afn / rate                 # fee in the customer's currency

    return {
        "fee": round(fee, 2),
        "total": round(amount + fee, 2),
        "rate": rate,
        "total_afn": round((amount + fee) * rate),
    }