"""SYNTHETIC demo file. Intentionally non-compliant settlement config."""

SETTLEMENT_PERIOD = "annual"  # running accounts settled once a year


def settle_running_accounts(clients):
    # annual settlement cadence
    for c in clients:
        c.settle(frequency="yearly")
