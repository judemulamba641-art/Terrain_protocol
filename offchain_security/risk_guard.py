def compute_fee(base_fee, utilization):
    if utilization > 0.95:
        return base_fee * 2
    elif utilization > 0.9:
        return int(base_fee * 1.5)
    return base_fee
