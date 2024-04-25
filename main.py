import dash_draggable
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input

data_frame = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

graph_container_style = {
    "height": '100%',
    "width": '100%',
    "display": "flex",
    "flex-direction": "column",
    "flex-grow": "0"
}

# График 1

default_countries = ["Russia", "Georgia", "China"]


def build_meas_vs_year_figure(active_countries, measure="pop"):
    linechart_countries = data_frame[data_frame.country.isin(active_countries)]
    return px.line(linechart_countries, x="year", y=measure, color="country", title="Показатели по годам")


meas_vs_year_dash = html.Div([
    html.Table([
        html.Tr([
            html.Td([
                html.Span("Выберите страны")
            ], style={"white-space": "nowrap"}),
            html.Td([
                dcc.Dropdown(data_frame.country.unique(), default_countries, multi=True,
                             id='dropdown-active-countries'),
            ], style={"width": "100%"}),
        ]),
        html.Tr([
            html.Td([
                html.Span("Мера оси Y ")
            ]),
            html.Td([
                dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], "pop", id='dropdown-measure', clearable=False)
            ]),
        ])
    ], style={"margin": "0rem 1rem"}),
    dcc.Graph(id='meas-vs-year-graph', figure=build_meas_vs_year_figure(default_countries), style=graph_container_style,
              responsive=True)
], style=graph_container_style, id="meas-vs-year-dash")


@callback(
    Output('meas-vs-year-graph', 'figure'),
    Input('dropdown-active-countries', 'value'),
    Input('dropdown-measure', 'value')
)
def update_meas_vs_year_dash(active_countries, measure):
    return build_meas_vs_year_figure(active_countries, measure)


# График 2

def build_bubble_figure(x="gdpPercap", y="lifeExp", size="pop", start_year=None, end_year=None):
    filtered_data = data_frame

    if start_year and end_year:
        filtered_data = data_frame[data_frame.year.between(start_year, end_year)]

    latest_data = filtered_data.sort_values(["continent", "year"], ascending=False).drop_duplicates("country")

    return px.scatter(latest_data, x=x, y=y, size=size, color="continent", hover_name="country", size_max=60,
                      hover_data=["year"])


bubble_dash = html.Div([
    html.Table([
        html.Tr([
            html.Td([
                html.Span("Мера оси X")
            ], style={"white-space": "nowrap"}),
            html.Td([
                dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], "gdpPercap", id='bubble-x', clearable=False)
            ], style={"width": "100%"})
        ]),
        html.Tr([
            html.Td([
                html.Span("Мера оси Y")
            ]),
            html.Td([
                dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], "lifeExp", id='bubble-y', clearable=False),
            ])
        ]),
        html.Tr([
            html.Td([
                html.Span("Мера размера")
            ]),
            html.Td([
                dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], "pop", id='bubble-size', clearable=False),
            ])
        ]),
    ], style={"margin": "0rem 1rem"}),
    dcc.Graph(id='bubble-graph', figure=build_bubble_figure(), style=graph_container_style, responsive=True)
], style=graph_container_style, id="bubble-dash")


@callback(
    Output('bubble-graph', 'figure'),
    Input('bubble-x', 'value'),
    Input('bubble-y', 'value'),
    Input('bubble-size', 'value'),
    Input('meas-vs-year-graph', 'relayoutData'),
)
def update_bubble_dash(x, y, size, meas_vs_year_zoom):
    return build_bubble_figure(x, y, size, *extract_year_range_from_relayout_data(meas_vs_year_zoom))


# График 3

def build_top_pop_figure(start_year=None, end_year=None):
    filtered_data = data_frame

    if start_year and end_year:
        filtered_data = data_frame[data_frame.year.between(start_year, end_year)]

    latest_data = filtered_data.sort_values("year", ascending=False).drop_duplicates("country")
    top = latest_data.sort_values("pop", ascending=False)[:15][::-1]

    return px.bar(top, x="pop", y="country", title="Топ 15 стран по населению", hover_data=["year"])


top_pop_dash = html.Div([
    dcc.Graph(id='top-pop-graph', figure=build_top_pop_figure(), style=graph_container_style, responsive=True)
], style=graph_container_style, id="top-pop-dash")


@callback(
    Output('top-pop-graph', 'figure'),
    Input('meas-vs-year-graph', 'relayoutData'),
)
def update_top_pop_dash(meas_vs_year_zoom):
    return build_top_pop_figure(*extract_year_range_from_relayout_data(meas_vs_year_zoom))


# График 4

def build_pop_pie_figure():
    return px.pie(data_frame, values="pop", names="continent", title="Население континентов", hole=.3)


@callback(
    Output('pop-pie-graph', 'figure'),
    Input('meas-vs-year-graph', 'relayoutData'),
)
def update_pop_pie_dash(meas_vs_year_zoom):
    return px.pie(data_frame, values="pop", names="continent", title="Население континентов", hole=.3)


pop_pie_dash = html.Div([
    dcc.Graph(id='pop-pie-graph', figure=build_pop_pie_figure(), style=graph_container_style, responsive=True)
], style=graph_container_style, id="pop-pie-dash")

# Макет приложения
app.layout = html.Div([
    html.H1(children='Сравнение стран', style={'textAlign': 'center'}),
    dash_draggable.ResponsiveGridLayout([
        meas_vs_year_dash, bubble_dash,
        top_pop_dash, pop_pie_dash
    ], clearSavedLayout=True, layouts={
        "lg": [
            {
                "i": "meas-vs-year-dash",
                "x": 0, "y": 0, "w": 6, "h": 20
            },
            {
                "i": "bubble-dash",
                "x": 6, "y": 0, "w": 6, "h": 20
            },
            {
                "i": "top-pop-dash",
                "x": 0, "y": 20, "w": 6, "h": 20
            },
            {
                "i": "pop-pie-dash",
                "x": 6, "y": 20, "w": 6, "h": 20
            }
        ]
    })
])


def extract_year_range_from_relayout_data(relayout_data):
    start_year = None
    end_year = None
    if relayout_data:
        if 'xaxis.range[0]' in relayout_data:
            start_year = relayout_data['xaxis.range[0]']
        if 'xaxis.range[1]' in relayout_data:
            end_year = relayout_data['xaxis.range[1]']

    return start_year, end_year


app = app.server

if __name__ == '__main__':
    app.run(debug=True)
