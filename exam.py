from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os

# =========================
# 1. Chargement des données
# =========================
# Utilisation de os.path pour garantir que le fichier est trouvé sur le serveur Linux
base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, "supermarket_sales.csv")
df = pd.read_csv(file_path)

# Conversion de la date
df["Date"] = pd.to_datetime(df["Date"])
df["Week"] = df["Date"].dt.isocalendar().week.astype(int)

# =========================
# 2. Initialisation de l'app
# =========================
app = Dash(__name__)
server = app.server  # <--- TRÈS IMPORTANT pour Render/Gunicorn

# Options des filtres
gender_options = [{"label": g, "value": g} for g in sorted(df["Gender"].unique())]
city_options = [{"label": "Toutes", "value": "Toutes"}] + \
               [{"label": c, "value": c} for c in sorted(df["City"].unique())]

# =========================
# 3. Mise en page
# =========================
app.layout = html.Div(
    style={
        "display": "flex",
        "minHeight": "100vh",
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#bde0fe",
        "padding": "20px",
        "color": "white" # <--- "fontwhite" corrigé en "white"
    },
    children=[
        # Colonne gauche : filtres
        html.Div(
            style={
                "width": "20%",
                "backgroundColor": "#1864ab",
                "padding": "20px",
                "borderRadius": "12px",
                "color": "white"
            },
            children=[
                html.H2("Filtres", style={"marginBottom": "30px"}),
                html.Label("Sexe", style={"fontWeight": "bold"}),
                dcc.Checklist(
                    id="gender-checklist",
                    options=gender_options,
                    value=sorted(df["Gender"].unique()),
                    inline=False,
                    style={"marginBottom": "25px"},
                    inputStyle={"marginRight": "8px"}
                ),
                html.Label("Ville", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="city-dropdown",
                    options=city_options,
                    value="Toutes",
                    clearable=False,
                    style={"color": "black"}
                )
            ]
        ),

        # Colonne droite : KPIs + Graphs
        html.Div(
            style={"width": "80%", "paddingLeft": "20px"},
            children=[
                # Titre
                html.Div(
                    html.H1("Tableau de bord des ventes", style={"textAlign": "center", "color": "white"}),
                    style={"backgroundColor": "#1864ab", "padding": "10px", "borderRadius": "12px", "marginBottom": "20px"}
                ),
                # KPIs
                html.Div(style={"display": "flex", "gap": "20px", "marginBottom": "20px"}, children=[
                    html.Div(children=[html.H4("Ventes Totales"), html.H2(id="kpi-total-sales")], 
                             style={"flex": "1", "backgroundColor": "white", "color": "#2b8a3e", "textAlign": "center", "borderRadius": "12px", "padding": "10px"}),
                    html.Div(children=[html.H4("Nb Achats"), html.H2(id="kpi-total-orders")], 
                             style={"flex": "1", "backgroundColor": "white", "color": "#2b8a3e", "textAlign": "center", "borderRadius": "12px", "padding": "10px"}),
                ]),
                # Graphiques
                html.Div(style={"display": "flex", "gap": "20px"}, children=[
                    dcc.Graph(id="histogram-total", style={"flex": "1"}),
                    dcc.Graph(id="bar-orders", style={"flex": "1"})
                ]),
                dcc.Graph(id="line-sales-week", style={"marginTop": "20px"})
            ]
        )
    ]
)


# =========================
# 4. Callback
# =========================
@app.callback(
    Output("kpi-total-sales", "children"),
    Output("kpi-total-orders", "children"),
    Output("histogram-total", "figure"),
    Output("bar-orders", "figure"),
    Output("line-sales-week", "figure"),
    Input("gender-checklist", "value"),
    Input("city-dropdown", "value")
)
def update_dashboard(selected_genders, selected_city):
    # 1. Gestion du cas "Rien n'est coché"
    if not selected_genders:
        dff = df.copy()
    else:
        dff = df[df["Gender"].isin(selected_genders)].copy()
    
    # 2. Filtrage par ville
    if selected_city != "Toutes":
        dff = dff[dff["City"] == selected_city]

    # 3. Sécurité : Si après filtrage il n'y a plus de données
    if dff.empty:
        return "0.00 €", "0", {}, {}, {}

    # 4. Calcul des KPIs
    total_sales = f"{dff['Total'].sum():,.2f} €"
    total_orders = f"{dff['Invoice ID'].nunique():,}"

    # --- Histogramme ---
    fig_hist = px.histogram(
        dff,
        x="Total",
        nbins=20,
        color="Gender", 
        title="<b>Répartition des montants totaux des achats</b>",
        color_discrete_map={"Female": "#c92a2a", "Male": "#1864ab"},
        labels={"Total": "Montant total des achats", "Gender": "Sexe"}
    )
    
    # --- Bar Chart ---
    bar_data = dff.groupby(["City", "Gender"], as_index=False)["Invoice ID"].count()
    bar_data = bar_data.rename(columns={"Invoice ID": "Nombre_achats"})
    
    fig_bar = px.bar(
        bar_data,
        x="City",
        y="Nombre_achats",
        color="Gender",
        barmode="group",
        title="<b>Nombre total d'achats par sexe et par ville</b>",
        color_discrete_map={"Male": "#1864ab", "Female": "#c92a2a"},
        labels={"City": "Ville", "Nombre_achats": "Nombre d'achats", "Gender": "Sexe"}
    )

    # --- Line Chart ---
    dff["Week_Start"] = dff["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_data = dff.groupby(["Week_Start", "City"], as_index=False)["Total"].sum()
    
    fig_line = px.line(
        weekly_data,
        x="Week_Start",
        y="Total",
        color="City",
        markers=True,
        title="<b>Évolution du montant total des achats par semaine</b>",
        color_discrete_map={
            "Yangon": "#1864ab", 
            "Mandalay": "#c92a2a", 
            "Naypyitaw": "#0b7285"
        },
        labels={"Week_Start": "Semaine", "Total": "Montant", "City": "Ville"}
    )

    return total_sales, total_orders, fig_hist, fig_bar, fig_line
    

# =========================
# 5. Lancement
# =========================
if __name__ == '__main__':
    # Configuration pour Render (port dynamique)
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host='0.0.0.0', port=port)
