import numpy as np

def compute_health_factor(z_values):
    """
    Convertit la valeur terrain → health factor
    """
    normalized = (z_values - z_values.min()) / (z_values.ptp() + 1e-9)
    health_factor = 1.2 + normalized * 1.5  # HF entre 1.2 et 2.7
    return health_factor


def compute_risk_level(health_factor):
    """
    Niveau de risque pour la visualisation
    """
    risk = np.where(
        health_factor < 1.3, "HIGH",
        np.where(health_factor < 1.6, "MEDIUM", "LOW")
    )
    return risk
