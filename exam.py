from dash import Dash
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# =========================
# 1. Chargement des données
# =========================
df = pd.read_csv("supermarket_sales.csv")


# Conversion de la date
df["Date"] = pd.to_datetime(df["Date"])

# Création d'une variable semaine
df["Week"] = df["Date"].dt.isocalendar().week.astype(int)

# =========================
# 2. Initialisation de l'app
# =========================
app = Dash(__name__)
server = app.server
# Options des filtres
gender_options = [
    {"label": gender, "value": gender}
    for gender in sorted(df["Gender"].dropna().unique())
]

city_options = [{"label": "Toutes", "value": "Toutes"}] + [
    {"label": city, "value": city}
    for city in sorted(df["City"].dropna().unique())
]

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
        "boxShadow": "2px 0 8px rgba(0,0,0,0.08)",
        "color": "fontwhite"
    },
    children=[

        # ========= Colonne gauche : filtres =========
        html.Div(
            style={
                "width": "15%",
                "backgroundColor": "#1864ab",
                "padding": "20px",
                "boxShadow": "2px 0 8px rgba(0,0,0,0.08)",
                "color": "white"
            },
            children=[
                html.H2("Filtres", style={"marginBottom": "30px"}),

                html.Label("Sexe", style={"Weight": "bold"}),
                dcc.Checklist(
                    id="gender-checklist",
                    options=gender_options,
                    value=sorted(df["Gender"].dropna().unique()),  # les deux cochés au départ
                    inline=False,
                    style={"marginBottom": "25px"},
                    inputStyle={"marginRight": "8px", "marginLeft": "5px"}
                ),

                html.Label("Ville", style={"Weight": "bold"}),
                dcc.Dropdown(
                    id="city-dropdown",
                    options=city_options,
                    value="Toutes",
                    clearable=False,
                    style={"marginBottom": "25px","color": "black","backgroundColor": "white"},
                     className="dropdown-style"
                )
            ]
        ),

        # ========= Colonne droite : indicateurs + graphiques =========
        html.Div(
            style={
                "width": "85%",
                "padding": "20px"
            },
            children=[
                html.Div(
                        html.H1(
                            "Tableau de bord des ventes du supermarché",
                            style={
                                "textAlign": "center",
                                "margin": "0",
                                "color": "white",
                                "fontSize": "38px",
                                "fontWeight": "bold",
                                "letterSpacing": "2px",
                                "textShadow": "2px 2px 6px rgba(0,0,0,0.4)",
                                "fontFamily": "Verdana"
                            }
                        ),
                        style={
                            "backgroundColor": "#1864ab",  
                             "padding": "20px",
                             "borderRadius": "12px",
                             "marginBottom": "30px",
                             "boxShadow": "0 2px 8px rgba(0,0,0,0.2)"
                        }
                ),

                # ===== KPI =====
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "marginBottom": "30px"
                    },
                    children=[
                        html.Div(
                            style={
                                "flex": "1",
                                "backgroundColor": "white",
                                "padding": "20px",
                                "borderRadius": "12px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                                "textAlign": "center"
                            },
                            children=[
                                html.H4("Montant total des achats", style={'color': '#2b8a3e', 'fontWeight': 'bold'}),
                                html.H2(id="kpi-total-sales")
                            ]
                        ),

                        html.Div(
                            style={
                                "flex": "1",
                                "backgroundColor": "white",
                                "padding": "20px",
                                "borderRadius": "12px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                                "textAlign": "center"
                            },
                            children=[
                                html.H4("Nombre total d'achats", style={'color': '#2b8a3e', 'fontWeight': 'bold'}),
                                html.H2(id="kpi-total-orders")
                            ]
                        )
                    ]
                ),

                # ===== 2 graphiques côte à côte =====
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "20px",
                        "marginBottom": "30px"

                    },
                    children=[
                        html.Div(
                            style={
                                "flex": "1",
                                "backgroundColor": "white",
                                "padding": "15px",
                                "borderRadius": "12px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                            },
                            children=[
                                dcc.Graph(id="histogram-total")
                            ]
                        ),

                        html.Div(
                            style={
                                "flex": "1",
                                "backgroundColor": "white",
                                "padding": "15px",
                                "borderRadius": "12px",
                                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                            },
                            children=[
                                dcc.Graph(id="bar-orders")
                            ]
                        )
                    ]
                ),

                # ===== 1 grand graphique =====
                html.Div(
                    style={
                        "backgroundColor": "white",
                        "padding": "15px",
                        "borderRadius": "12px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
                    },
                    children=[
                        dcc.Graph(id="line-sales-week")
                    ]
                )
            ]
        )
    ]
)

# =========================
# 4. Callback principal
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
    dff = df.copy()

    # Filtre sexe
    if selected_genders:
        dff = dff[dff["Gender"].isin(selected_genders)]
    else:
        dff = dff.iloc[0:0]   # si rien n'est coché, dataframe vide

    # Filtre ville
    if selected_city != "Toutes":
        dff = dff[dff["City"] == selected_city]

    # ===== KPI =====
    total_sales = round(dff["Total"].sum(), 2)
    total_orders = dff["Invoice ID"].nunique()

    formatted_sales = f"{total_sales:,.2f} €"
    formatted_orders = f"{total_orders:,}"

    # ===== Histogramme des montants =====
    fig_hist = px.histogram(
        dff,
        x="Total",
        nbins=20,
        color="Gender",
        title="<b>Répartition des montants totaux des achats</b>",
        color_discrete_sequence=["#1864ab", "#c92a2a"],
        labels={
        "Total": "Montant total des achats",
        "Gender": "Sexe"
    }
    )
    fig_hist.update_layout(title_x=0.5)
    fig_hist.update_yaxes(title="Fréquence")

    # ===== Diagramme en barres du nombre d'achats =====
    bar_data = dff.groupby(["City", "Gender"], as_index=False)["Invoice ID"].count()
    bar_data = bar_data.rename(columns={"Invoice ID": "Nombre_achats"})

    fig_bar = px.bar(
        bar_data,
        x="City",
        y="Nombre_achats",
        color="Gender",
        barmode="group",
        title="<b>Nombre total d'achats par sexe et par ville </b>",
        color_discrete_sequence=["#1864ab", "#c92a2a"],
        labels={
        "City": "Ville",
        "Nombre_achats": "Nombre d'achats",
        "Gender": "Sexe"
         }
    )
    fig_bar.update_layout(title_x=0.5)

    # ===== Courbe d'évolution =====
    # ===== Courbe d'évolution propre =====

    # début de semaine (lundi) pour chaque date
    dff["Week_Start"] = dff["Date"].dt.to_period("W").apply(lambda r: r.start_time)

    weekly_data = (
        dff.groupby(["Week_Start", "City"], as_index=False)["Total"]
        .sum()
    )

    fig_line = px.line(
        weekly_data,
        x="Week_Start",
        y="Total",
        color="City",
        markers=True,
        title="<b>Évolution du montant total des achats par semaine par ville</b>",
        color_discrete_sequence=["#1864ab", "#c92a2a", "#0b7285"],
        labels={
            "Week_Start": "Semaine",
            "Total": "Montant total des achats",
            "City": "Ville"
        }
    )

    fig_line.update_layout(title_x=0.5)

    # 👇 FORMAT DE L’AXE (important)
    fig_line.update_xaxes(
        tickformat="%b %Y",   # Mar 2019, May 2019...
        tickangle=0,
        showgrid=True
    )

    return (
        formatted_sales,
        formatted_orders,
        fig_hist,
        fig_bar,
        fig_line
    )

# =========================
# 5. Lancement de l'app
# =========================
if __name__ == '__main__':
    # Remplace app.run(debug=True) par ceci :
    app.run_server(debug=False, host='0.0.0.0', port=8080)