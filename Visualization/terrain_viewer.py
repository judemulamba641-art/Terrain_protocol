import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

from visualization.terrain_generator import generate_terrain_grid
from visualization.terrain_metrics import compute_health_factor

def plot_terrain_map():
    x, y, z = generate_terrain_grid()
    hf = compute_health_factor(z)

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(
        x,
        y,
        z,
        facecolors=cm.viridis(hf / hf.max()),
        linewidth=0,
        antialiased=True
    )

    ax.set_title("Terrain Protocol – 3D NFT Map")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Terrain Value / Height")

    mappable = cm.ScalarMappable(cmap=cm.viridis)
    mappable.set_array(hf)
    plt.colorbar(mappable, shrink=0.5, label="Health Factor")

    plt.show()


if __name__ == "__main__":
    plot_terrain_map()
