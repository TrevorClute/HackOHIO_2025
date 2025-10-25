"""
Minimal Dash app that displays a stress map using `/ratings_geojson`.

Dependencies:
  pip install -r requirements.txt

Run the server first (in another terminal):
  uvicorn app.main:app --reload --port 8000

Then run this app:
  python tools/dash_app.py

It will start a Dash server on http://127.0.0.1:8050 where you can adjust
ambient and wind values and see the stress map update.
"""

import json
import math
import requests
import sys
import pandas as pd

try:
    from dash import Dash, dcc, html, Output, Input, State
    from dash import exceptions
    from dash import dcc as _dcc
    from dash.dcc import Download
    import plotly.graph_objects as go
except Exception as e:
    print("Missing dependencies:", e)
    print("Please install: pip install dash plotly requests")
    sys.exit(1)

API_URL = "http://localhost:8000/ratings_geojson"


def stress_to_rgb(stress_pct):
    """Return an RGB color string sampled from a smooth colorscale.

    The colorscale is defined at stops: 0->green, 0.6->yellow, 0.9->orange, 1->red.
    We normalize stress_pct to [0,1] by dividing by 100 and clamp.
    """
    if stress_pct is None:
        return "rgb(160,160,160)"
    try:
        s = float(stress_pct)
    except Exception:
        return "rgb(160,160,160)"

    # normalized t in [0,1]
    t = max(0.0, min(1.0, s / 100.0))

    # color stops (changed yellow stop from 0.6 -> 0.5)
    stops = [
        (0.0, (0,200,0)),      # green
        (0.5, (255,215,0)),    # yellow (50%)
        (0.9, (255,140,0)),    # orange
        (1.0, (220,20,60))     # red
    ]

    # find surrounding stops
    for i in range(len(stops)-1):
        t0, c0 = stops[i]
        t1, c1 = stops[i+1]
        if t0 <= t <= t1:
            # interpolate
            if t1 - t0 == 0:
                f = 0.0
            else:
                f = (t - t0) / (t1 - t0)
            r = int(c0[0] + f * (c1[0] - c0[0]))
            g = int(c0[1] + f * (c1[1] - c0[1]))
            b = int(c0[2] + f * (c1[2] - c0[2]))
            return f"rgb({r},{g},{b})"

    return "rgb(160,160,160)"


def fetch_geojson(ambient_c=30, wind_ms=2):
    params = {"ambient_c": ambient_c, "wind_ms": wind_ms}
    r = requests.get(API_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def build_figure(geojson):
    fig = go.Figure()
    features = geojson.get("features", [])
    all_lons = []
    all_lats = []
    for feat in features:
        props = feat.get("properties", {})
        geom = feat.get("geometry")
        if not geom or geom.get("type") != "LineString":
            continue
        coords = geom.get("coordinates", [])
        if len(coords) < 2:
            continue
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        all_lons.extend(lons)
        all_lats.extend(lats)
        stress = props.get("stress_pct")
        color = stress_to_rgb(stress)
        text = (
            f"{props.get('line_id')}<br>conductor: {props.get('conductor')}<br>"
            f"amps: {props.get('amps')}<br>mva: {props.get('mva')}<br>"
            f"s_nom_mva: {props.get('s_nom_mva')}<br>stress_pct: {props.get('stress_pct')}<br>"
            f"status: {props.get('status')}")
        fig.add_trace(go.Scattermapbox(
            lon=lons, lat=lats,
            mode='lines',
            line=dict(color=color, width=4),
            hoverinfo='text',
            hovertext=text,
            name=props.get('line_id')
        ))
    # compute bounding box and choose a zoom so the map fits the lines
    if all_lons and all_lats:
        min_lon = min(all_lons)
        max_lon = max(all_lons)
        min_lat = min(all_lats)
        max_lat = max(all_lats)
        center_lon = (min_lon + max_lon) / 2.0
        center_lat = (min_lat + max_lat) / 2.0
        lon_span = max_lon - min_lon
        lat_span = max_lat - min_lat
        span = max(lon_span, lat_span)
        if span <= 0:
            zoom = 10
        else:
            # approximate zoom level from longitude span
            zoom = math.log2(360.0 / span)
            # clamp to reasonable values
            zoom = max(3, min(12, zoom))
        mapbox = dict(style="open-street-map", center=dict(lon=center_lon, lat=center_lat), zoom=zoom)
    else:
        # fallback: default center roughly Hawaii
        mapbox = dict(style="open-street-map", center=dict(lon=-157.8, lat=21.3), zoom=6)

    fig.update_layout(
        mapbox=mapbox,
        margin={"r":0,"t":0,"l":0,"b":0},
        height=800
    )
    return fig


app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.H3("Line Stress Map"),
        html.Label("Ambient (°C)"),
        dcc.Slider(id='ambient-slider', min=-40, max=50, step=1, value=30,
                   marks={-40:"-40",0:"0",20:"20",40:"40"}, updatemode='mouseup'),
        html.Label("Wind (m/s)"),
        dcc.Slider(id='wind-slider', min=0, max=20, step=0.5, value=2,
                   marks={0:"0",5:"5",10:"10",20:"20"}, updatemode='mouseup'),

        html.Div([
            html.Button('Download GeoJSON', id='download-geojson-btn'),
            html.Button('Download CSV', id='download-csv-btn', style={"marginLeft":"8px"}),
            Download(id='download-geojson'),
            Download(id='download-csv')
        ], style={"marginTop":"10px"}),

        # Colorbar: vertical gradient with labels positioned to match color stops
        html.Div([
            html.H4("Stress \u2014 %"),
            # container with relative positioning
            html.Div(
                style={"position": "relative", "height": "200px", "width": "120px", "marginTop": "8px"},
                children=[
                    # gradient bar on the left
                    html.Div(style={
                        "position": "absolute",
                        "left": "0px",
                        "top": "0px",
                        "height": "200px",
                        "width": "28px",
                        # updated gradient stop from 60% -> 50%
                        "background": "linear-gradient(to top, rgb(0,200,0) 0%, rgb(255,215,0) 50%, rgb(255,140,0) 90%, rgb(220,20,60) 100%)",
                        "border": "1px solid #ccc"
                    }),
                    # tick labels placed exactly at stops
                    html.Div("100%", style={"position":"absolute", "left":"36px", "top":"0%"}),
                    
                    # changed label from 60% -> 50% and adjust top to match gradient stop (50% from bottom => 50% from top)
                    html.Div("50%",  style={"position":"absolute", "left":"36px", "top":"50%", "transform":"translateY(-50%)"}),
                    html.Div("0%",   style={"position":"absolute", "left":"36px", "top":"100%", "transform":"translateY(-100%)"})
                ]
            )
        ], style={"marginTop":"12px"})

    ], style={"width": "300px", "display": "inline-block", "verticalAlign": "top", "padding": "10px"}),

    html.Div([
        dcc.Graph(id='map-graph'),
        dcc.Graph(id='hist-graph', style={"height":"200px"})
    ], style={"display": "inline-block", "width": "calc(100% - 320px)"})
])


@app.callback(
    Output('map-graph', 'figure'),
    Output('hist-graph', 'figure'),
    Input('ambient-slider', 'value'),
    Input('wind-slider', 'value')
)
def update_map(ambient, wind):
    try:
        geojson = fetch_geojson(ambient_c=ambient, wind_ms=wind)
        fig = build_figure(geojson)
        # also update histogram
        stresses = []
        for f in geojson.get('features', []):
            try:
                s = f.get('properties', {}).get('stress_pct')
                if s is not None:
                    stresses.append(float(s))
            except Exception:
                pass
        hist_fig = go.Figure()
        if stresses:
            hist_fig.add_trace(go.Histogram(x=stresses, nbinsx=20, marker_color='rgba(255,100,0,0.8)'))
            hist_fig.update_layout(title='Stress (%) distribution', xaxis_title='Stress (%)', yaxis_title='Count')
        else:
            hist_fig.update_layout(title='No stress data available')

    except Exception as e:
        fig = go.Figure()
        fig.update_layout(title=f"Error fetching data: {e}")
        hist_fig = go.Figure()
        hist_fig.update_layout(title='No stress data available')

    # return map figure and histogram
    return fig, hist_fig


@app.callback(
    Output('download-geojson', 'data'),
    Input('download-geojson-btn', 'n_clicks'),
    State('ambient-slider', 'value'),
    State('wind-slider', 'value'),
    prevent_initial_call=True
)
def download_geojson(n_clicks, ambient, wind):
    try:
        geojson = fetch_geojson(ambient_c=ambient, wind_ms=wind)
        return dcc.send_bytes(lambda f: f.write(json.dumps(geojson).encode('utf-8')), filename=f'ratings_{ambient}C_{wind}ms.geojson')
    except Exception as e:
        raise exceptions.PreventUpdate


@app.callback(
    Output('download-csv', 'data'),
    Input('download-csv-btn', 'n_clicks'),
    State('ambient-slider', 'value'),
    State('wind-slider', 'value'),
    prevent_initial_call=True
)
def download_csv(n_clicks, ambient, wind):
    try:
        geojson = fetch_geojson(ambient_c=ambient, wind_ms=wind)
        rows = []
        for f in geojson.get('features', []):
            p = f.get('properties', {})
            rows.append(p)
        if not rows:
            raise exceptions.PreventUpdate
        df = pd.DataFrame(rows)
        return dcc.send_data_frame(df.to_csv, filename=f'ratings_{ambient}C_{wind}ms.csv', index=False)
    except Exception as e:
        raise exceptions.PreventUpdate


if __name__ == '__main__':
    print("Starting Dash app on http://127.0.0.1:8050")
    app.run_server(debug=True)
