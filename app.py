import dash_bootstrap_components as dbc

from dash import Dash, dcc, html, Input, Output, ctx
from dash.exceptions import PreventUpdate

# Import business layer module which handles the necessary backend work
from business_layer import summarizer, derive_themes


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

#-------------------------------------------------------------

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "15rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(children=[
            dbc.Alert("Ensure you've selected the right format for your transcript.", color="warning"),

            dbc.Alert("Verify your format!", color="danger", duration=4000, is_open=False, id="format_warning"),

            dbc.RadioItems(
                options=[
                    {"label": "Dialogue Format", "value": "dialogue"},
                    {"label": "Non-Dialogue Format", "value": "non-dialogue"}
                ],
                value="dialogue",
                id="format_selection"
            ),

            dbc.Button("Draw Insights", id="insight_button", disabled=True,
                        style={"margin-left": "15px", "margin-top": "15px", "margin-bottom": '15px'}),

            dbc.Alert("Loading Insights...", id="loading_insights_alert", color="info", 
                      is_open=False, duration=15000),

            dbc.Alert("Insights Gotten!", id="insights_gotten_alert", color="success", 
                      is_open=False, duration=4000),

            html.Br(),
                    
            dbc.Button("Get Themes", id="get_themes_button", disabled=True,
                    style={"margin-left": "15px", "margin-top": "15px", "margin-bottom": '15px'}),

            dbc.Alert("Loading Themes...", id="loading_themes_alert", color="info", 
                      is_open=False, duration=3000),

            dbc.Alert("Themes Gotten!", id="themes_gotten_alert", color="success", 
                      is_open=False, duration=4000)


    ], className="d-grid gap-2", style=SIDEBAR_STYLE)

content = html.Div(children=[
    html.H1("Customer Feedback Analyzer.", style={"textAlign": "center"}),

    html.Div(style={"display": "flex", "flex-direction": "row"}, children=[
        dcc.Textarea(id="transcript1_input", placeholder="Enter Transcript 1 Here", value="",
                     style={"margin-left": "15px", "margin-top": "15px",
                            "width":"50%", "height":300}),

        dcc.Textarea(id="transcript1_output", placeholder="Transcript 1 Insights Go Here...", value="",
                     disabled=True,
                     style={"margin-left": "15px", "margin-top": "15px", "margin-right": "15px",
                            "width":"50%", "height":300})
    ]),

    html.Div(style={"display": "flex", "flex-direction": "row"}, children=[
        dcc.Textarea(id="transcript2_input", placeholder="Enter Transcript 2 Here", value="",
                     style={"margin-left": "15px", "margin-top": "15px",
                            "width":"50%", "height":300}),

        dcc.Textarea(id="transcript2_output", placeholder="Transcript 2 Insights Go Here...", value="",
                     disabled=True,
                     style={"margin-left": "15px", "margin-top": "15px", "margin-right": "15px",
                            "width":"50%", "height":300})
    ]),

    html.Div(style={"display": "flex", "flex-direction": "row"}, children=[
        dcc.Textarea(id="transcript3_input", placeholder="Enter Transcript 3 Here", value="",
                     style={"margin-left": "15px", "margin-top": "15px",
                            "width":"50%", "height":300}),

        dcc.Textarea(id="transcript3_output", placeholder="Transcript 3 Insights Go Here...", value="",
                     disabled=True,
                     style={"margin-left": "15px", "margin-top": "15px", "margin-right": "15px",
                            "width":"50%", "height":300}),
    ]),

    html.Div(style={"display": "flex", "flex-direction": "row"}, children=[
        dcc.Textarea(id="theme1_output", placeholder="Theme1 Goes Here...", disabled=True, value="",
                    style={"margin-left": "15px", "margin-top": "15px", "margin-right": "15px",
                            "margin-bottom": "15px", "width":"32%", "height":300}),

        dcc.Textarea(id="theme2_output", placeholder="Theme2 Goes Here...", disabled=True, value="",
                    style={"margin-left": "15px", "margin-top": "15px", "margin-right": "15px",
                            "margin-bottom": "15px", "width":"32%", "height":300}),

        dcc.Textarea(id="theme3_output", placeholder="Theme3 Goes Here...", disabled=True, value="",
                    style={"margin-left": "15px", "margin-top": "15px", "margin-right": "15px",
                            "margin-bottom": "15px", "width":"32%", "height":300})
    ])

    ], style=CONTENT_STYLE)


layout = [html.Div(children=[sidebar, content,
                             dcc.Store(id="intermediate_values", storage_type="session"),
])]
app.layout = html.Div(layout)

@app.callback(Output("format_warning", "is_open"),
              Input("transcript1_input", "value"))
def toggle_warning(transcript1):
    if transcript1 != "":
        return True

@app.callback([Output("insight_button", "disabled"),
               Output("get_themes_button", "disabled")],
              [Input("transcript3_input", "value"),
               Input("transcript3_output", "value"),
               Input("theme3_output", "value")])
def activate_buttons(transcript3, insight3, theme3):
    if (transcript3 == "") and (insight3 == ""):
        return True, True
    elif (transcript3 != "") and (theme3 != ""):
        return True, True
    elif insight3 != "":
        return True, False 
    elif transcript3 != "":
        return False, True
    

@app.callback([Output("loading_insights_alert", "is_open")],
              [Input("insight_button", "n_clicks")])
def loading_insights_alerts(n_clicks):
    if n_clicks == 1:
        return [True]
    return [False]
    

@app.callback([Output("loading_themes_alert", "is_open")],
              [Input("get_themes_button", "n_clicks")])
def loading_themes_alerts(n_clicks):
    if n_clicks == 1:
        return [True]
    return [False]


@app.callback([Output("insights_gotten_alert", "is_open")], 
              [Input("transcript3_output", "value")])
def insights_gotten_alerts(insight3):
    if insight3 != "":
        return [True]
    return [False]
    

@app.callback([Output("themes_gotten_alert", "is_open")],
              [Input("theme3_output", "value")])
def themes_gotten_alerts(theme3):
    if theme3 != "":
        return [True]
    return [False]
    

@app.callback([Output("intermediate_values", "data"),
               Output("transcript1_output", "value"),
               Output("transcript2_output", "value"),
               Output("transcript3_output", "value")],
              [Input("format_selection", "value"),
               Input("transcript1_input", "value"),
               Input("transcript2_input", "value"),
               Input("transcript3_input", "value"),
               Input("insight_button", "n_clicks")])
def get_insight(format, text1, text2, text3, n_clicks):
    changed_id = [p["prop_id"] for p in ctx.triggered][0]
    texts = [text1, text2, text3]
    if n_clicks is None:
        raise PreventUpdate
    elif "insight_button" in changed_id:
        feedbacks = summarizer(format=format, texts=texts)
        return feedbacks, feedbacks["transcript_0"]["output"], feedbacks["transcript_1"]["output"], \
            feedbacks["transcript_2"]["output"]


@app.callback([Output("theme1_output", "value"),
               Output("theme2_output", "value"),
               Output("theme3_output", "value")],
              [Input("intermediate_values", "data"),
               Input("get_themes_button", "n_clicks")])
def get_themes(data, n_clicks):
    changed_id = [p["prop_id"] for p in ctx.triggered][0]
    if n_clicks is None:
        raise PreventUpdate
    elif "get_themes_button" in changed_id:
        outputs = derive_themes(feedbacks=data)  # data: Data cache
        return outputs[0], outputs[1], outputs[2]
    

if __name__ == "__main__":
    app.run_server(debug=False)  # Set debug to False before deployment.
