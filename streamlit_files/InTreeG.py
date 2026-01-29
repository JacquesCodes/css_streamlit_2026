import streamlit as st
import numpy as np
import trimesh
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(page_title="PolyForest: Zero Gaps", page_icon="🌲", layout="wide")

st.title("🌲 PolyForest Generator")
st.markdown("Generates a forest of stylized, low-polygon trees with solid geometry.")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Settings")
    n_trees = st.slider("Tree Count", 20, 300, 100)
    plot_size = st.slider("Plot Size", 50, 200, 120)
    
    st.markdown("---")
    st.caption("Gap Fix: Active (0.5m overlap)")

# --- Geometry Helpers ---

def get_random_color(base_rgb, variance=25):
    """Variates a color slightly."""
    return [np.clip(c + np.random.randint(-variance, variance), 0, 255) for c in base_rgb] + [255]

def stack_on_top(bottom_mesh, top_mesh, overlap=0.5):
    """
    Robustly places top_mesh on top of bottom_mesh.
    It calculates the exact bounding boxes to ensure connection.
    """
    # Find the highest Z point of the bottom object
    bottom_z_max = bottom_mesh.bounds[1][2]
    
    # Find the lowest Z point of the top object
    top_z_min = top_mesh.bounds[0][2]
    
    # Calculate exactly how much to move the top object
    # Target Z = (Bottom Top) - Overlap
    # Move needed = Target Z - (Current Bottom)
    shift_z = (bottom_z_max - overlap) - top_z_min
    
    top_mesh.apply_translation([0, 0, shift_z])
    return top_mesh

def create_trunk(height, radius=0.7):
    """Creates a trunk with base at Z=0"""
    trunk = trimesh.creation.cylinder(radius=radius, height=height, sections=5)
    trunk.visual.face_colors = [101, 67, 33, 255]
    # Align bottom of trunk to Z=0 (since cylinder center is at 0,0,0)
    trunk.apply_translation([0, 0, height/2]) 
    return trunk

# --- Tree Generators ---

OVERLAP_AMOUNT = 0.5  # Fixed overlap value

def create_roundy_tree(pos):
    """Sphere on Trunk"""
    h_trunk = np.random.uniform(3, 6)
    r_crown = np.random.uniform(2.5, 4.5)
    
    trunk = create_trunk(h_trunk)
    
    crown = trimesh.creation.icosphere(subdivisions=1, radius=r_crown)
    crown.visual.face_colors = get_random_color([124, 204, 57])
    
    # Use helper to stack crown on trunk
    stack_on_top(trunk, crown, overlap=OVERLAP_AMOUNT)
    
    # Combine and move to final plot position
    tree = trimesh.util.concatenate([trunk, crown])
    tree.apply_translation(pos)
    return tree

def create_pointy_tree(pos):
    """Cone on Trunk"""
    h_trunk = np.random.uniform(2, 4)
    h_crown = np.random.uniform(6, 10)
    r_crown = np.random.uniform(2.5, 4.0)
    
    trunk = create_trunk(h_trunk, radius=0.6)
    
    crown = trimesh.creation.cone(radius=r_crown, height=h_crown, sections=6)
    crown.visual.face_colors = get_random_color([34, 139, 34])
    
    # Use helper to stack crown on trunk
    stack_on_top(trunk, crown, overlap=OVERLAP_AMOUNT)
    
    tree = trimesh.util.concatenate([trunk, crown])
    tree.apply_translation(pos)
    return tree

def create_stacked_tree(pos):
    """Trunk -> Cone 1 -> Cone 2"""
    h_trunk = np.random.uniform(2, 3)
    trunk = create_trunk(h_trunk, radius=0.7)
    
    # Cone 1
    h1 = np.random.uniform(3, 5)
    c1 = trimesh.creation.cone(radius=np.random.uniform(3,4), height=h1, sections=7)
    c1.visual.face_colors = get_random_color([46, 139, 87])
    
    # Stack C1 on Trunk
    stack_on_top(trunk, c1, overlap=OVERLAP_AMOUNT)
    
    # Cone 2
    c2 = trimesh.creation.cone(radius=2.0, height=np.random.uniform(2,4), sections=7)
    c2.visual.face_colors = get_random_color([143, 188, 143])
    
    # Stack C2 on C1
    stack_on_top(c1, c2, overlap=OVERLAP_AMOUNT)
    
    tree = trimesh.util.concatenate([trunk, c1, c2])
    tree.apply_translation(pos)
    return tree

# --- Main Logic ---

with st.spinner(f"Generating {n_trees} trees..."):
    meshes = []
    # Create grid of positions
    positions = np.random.uniform(-plot_size/2, plot_size/2, (n_trees, 2))
    
    for i in range(n_trees):
        pos = [positions[i][0], positions[i][1], 0]
        rnd = np.random.rand()
        
        if rnd < 0.4:
            meshes.append(create_roundy_tree(pos))
        elif rnd < 0.75:
            meshes.append(create_pointy_tree(pos))
        else:
            meshes.append(create_stacked_tree(pos))
            
    # Combine all trees into one single mesh for performance
    forest_mesh = trimesh.util.concatenate(meshes)

# --- Visualization ---

vertices = forest_mesh.vertices
faces = forest_mesh.faces
colors = forest_mesh.visual.face_colors[:, :3]

fig = go.Figure([
    # Trees
    go.Mesh3d(
        x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
        i=faces[:,0], j=faces[:,1], k=faces[:,2],
        facecolor=colors,
        flatshading=True,
        name='Trees'
    ),
    # Ground
    go.Mesh3d(
        x=[-plot_size/1.8, plot_size/1.8, plot_size/1.8, -plot_size/1.8],
        y=[-plot_size/1.8, -plot_size/1.8, plot_size/1.8, plot_size/1.8],
        z=[-0.1, -0.1, -0.1, -0.1],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color='rgb(160, 200, 120)',
        flatshading=True,
        name='Ground'
    )
])

fig.update_layout(
    scene=dict(
        xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
        aspectmode='data',
        bgcolor='rgb(235, 245, 250)'
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=700
)

st.plotly_chart(fig, use_container_width=True)