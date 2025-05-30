from flask import Flask, render_template_string
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

app = Flask(__name__)

@app.route('/')
def index():
    # Sample block model data
    data_str = """X, Y, Z, DX, DY, DZ, Rock_Type, Ore_Flag, Au_Grade, Cu_Grade, Density
    400000, 3700000, 1200, 10, 10, 10, S, 1, 1.25, 0.45, 2.65
    400010, 3700000, 1200, 10, 10, 10, L, 0, 0.02, 0.01, 2.70
    400000, 3700010, 1200, 10, 10, 10, S, 1, 0.90, 0.30, 2.65
    400010, 3700010, 1200, 10, 10, 10, L, 0, 0.10, 0.05, 2.70
    400020, 3700000, 1210, 10, 10, 10, S, 1, 1.15, 0.50, 2.65
    400030, 3700000, 1210, 10, 10, 10, S, 1, 0.85, 0.25, 2.65
    400020, 3700010, 1210, 10, 10, 10, L, 0, 0.15, 0.08, 2.70
    400030, 3700010, 1210, 10, 10, 10, S, 1, 1.05, 0.40, 2.65"""

    df = pd.read_csv(io.StringIO(data_str), sep=',', skipinitialspace=True)
    df['X_norm'] = df['X'] - df['X'].min()
    df['Y_norm'] = df['Y'] - df['Y'].min()
    df['Z_norm'] = df['Z'] - df['Z'].min()

    def create_cube(x, y, z, dx, dy, dz):
        vertices = np.array([
            [x, y, z],
            [x+dx, y, z],
            [x+dx, y+dy, z],
            [x, y+dy, z],
            [x, y, z+dz],
            [x+dx, y, z+dz],
            [x+dx, y+dy, z+dz],
            [x, y+dy, z+dz]
        ])
        triangles = [
            [0, 1, 2], [0, 2, 3],
            [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4],
            [2, 3, 7], [2, 7, 6],
            [0, 3, 7], [0, 7, 4],
            [1, 2, 6], [1, 6, 5]
        ]
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom face
            [4, 5], [5, 6], [6, 7], [7, 4],  # Top face
            [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical edges
        ]
        return vertices, triangles, edges

    fig = go.Figure()

    for index, row in df.iterrows():
        x, y, z = row['X_norm'], row['Y_norm'], row['Z_norm']
        dx, dy, dz = row['DX'], row['DY'], row['DZ']
        rock_type = row['Rock_Type']
        ore_flag = row['Ore_Flag']

        color = (
            'red' if rock_type == 'S' and ore_flag == 1 else
            'pink' if rock_type == 'S' else
            'darkgreen' if ore_flag == 1 else
            'lightgreen'
        )

        vertices, triangles, edges = create_cube(x, y, z, dx, dy, dz)

        # Add cube mesh
        fig.add_trace(go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=[t[0] for t in triangles],
            j=[t[1] for t in triangles],
            k=[t[2] for t in triangles],
            color=color,
            opacity=0.7,
            hovertext=f"Block {index}<br>Rock: {rock_type}<br>Ore: {'Yes' if ore_flag==1 else 'No'}",
            name=f"Block {index}"
        ))

        # Add visible gray edges
        for edge in edges:
            start, end = edge
            fig.add_trace(go.Scatter3d(
                x=[vertices[start, 0], vertices[end, 0]],
                y=[vertices[start, 1], vertices[end, 1]],
                z=[vertices[start, 2], vertices[end, 2]],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False,
                hoverinfo='none'
            ))

    fig.update_layout(
        title={
            'text': "No Metadata Block Model - Rock Type Visualization",
            'font': dict(size=20, family="Arial", color="black")
        },
        width=1000,
        height=800,
        scene=dict(
            aspectmode='data',
            xaxis=dict(title='X', range=[0, df['X_norm'].max() + 10]),
            yaxis=dict(title='Y', range=[0, df['Y_norm'].max() + 10]),
            zaxis=dict(title='Z', range=[0, df['Z_norm'].max() + 10]),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1))
        )
    )

    html = fig.to_html(full_html=False)
    return render_template_string("""
    <html>
    <head>
        <title>3D Block Model</title>
        <meta charset="utf-8">
    </head>
    <body>
        {{ html_content | safe }}
    </body>
    </html>
    """, html_content=html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
