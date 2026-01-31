import numpy as np

def generate_terrain_grid(
    size=50,
    max_height=100,
    volatility=0.3,
    seed=42
):
    """
    Génère une carte de terrains NFT 3D
    """
    np.random.seed(seed)

    x = np.linspace(0, size, size)
    y = np.linspace(0, size, size)
    x, y = np.meshgrid(x, y)

    base = np.sin(x / 4) * np.cos(y / 4)
    noise = volatility * np.random.randn(size, size)

    z = (base + noise) * max_height

    return x, y, z
