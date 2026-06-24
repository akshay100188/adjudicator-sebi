"""SYNTHETIC demo file for the code-analysis module. Intentionally non-compliant.
Not a real system — exists only to exercise the scanner.
"""

HOUSE_CLIENT_FUNDS_ACCOUNT = "ICICI-house-001"  # client money pooled in a house account


def transfer_client_payout(client_id, amount):
    # moves client funds but writes no audit trail
    bank.debit(HOUSE_CLIENT_FUNDS_ACCOUNT, amount)
    bank.credit(client_id, amount)
    return True


def upstream_balances(balances):
    # sweeps pooled client money; no audit/log call
    for client_id, amt in balances.items():
        bank.transfer(HOUSE_CLIENT_FUNDS_ACCOUNT, "CC", amt)
