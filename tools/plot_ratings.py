"""
Minimal example visualization script for `/ratings`.

This script fetches JSON from the local server and builds a simple scatter-line plot
showing line segments colored by `stress_pct`. It is intentionally lightweight and
expects `bus0_lon`, `bus0_lat`, `bus1_lon`, `bus1_lat`, and `stress_pct` in the API
response (these fields were added to the backend).

Dependencies (not added to repo requirements to avoid interfering):
  pip install requests plotly

Run the local server first (in another terminal):
  uvicorn app.main:app --reload --port 8000

Then run this script:
  python tools/plot_ratings.py

It will write `ratings_map.html` which you can open in a browser.
"""

import sys

try:
    import requests
    import plotly.graph_objects as go
except Exception as e:
    print("Missing dependency:", e)
    print("Please install: pip install requests plotly")
    sys.exit(1)

URL = "http://localhost:8000/ratings"

def fetch_ratings(url=URL):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def build_figure(ratings):
    fig = go.Figure()
    for line in ratings:
        lon0 = line.get("bus0_lon")
        lat0 = line.get("bus0_lat")
        lon1 = line.get("bus1_lon")
        lat1 = line.get("bus1_lat")
        stress = line.get("stress_pct")
        if None in (lon0, lat0, lon1, lat1):
            continue
        color = None
        if stress is None:
            color = "gray"
        else:
            # simple red-green scale
            s = max(0.0, min(100.0, stress)) / 100.0
            # interpolate green->red
            rcol = int(255 * s)
            gcol = int(255 * (1 - s))
            color = f"rgb({rcol},{gcol},0)"

        fig.add_trace(go.Scatter(
            x=[lon0, lon1], y=[lat0, lat1],
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=6),
            name=line.get("line_id"),
            hoverinfo='text',
            hovertext=(f"{line.get('line_id')}<br>conductor: {line.get('conductor')}<br>"
                       f"ampacity (A): {line.get('amps')}<br>mva: {line.get('mva')}<br>"
                       f"s_nom_mva: {line.get('s_nom_mva')}<br>stress_pct: {line.get('stress_pct')}")
        ))

    fig.update_layout(
        title='Line stress map (simple lon/lat plot)',
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        showlegend=False,
        height=700,
        width=1000
    )
    return fig


def main():
    print("Fetching ratings from:", URL)
    ratings = fetch_ratings()
    fig = build_figure(ratings)
    out = "ratings_map.html"
    fig.write_html(out)
    print("Wrote", out)

if __name__ == '__main__':
    main()
