import ast
import dash
from dash import dcc, html, dash_table, Output, Input
import pandas as pd
import plotly.express as px
from datetime import datetime

from utils import df

def get_public_metrics(metrics_json):
    data = ast.literal_eval(metrics_json)
    return pd.Series([
        data['retweet_count'],
        data['reply_count'],
        data['like_count'],
        data['quote_count'],
        data['bookmark_count'],
        data['impression_count']
    ])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("📊 JDOviedoAr"),

    html.Div([
        html.Div([
            dcc.DatePickerRange(
                id='date-range',
                start_date=df['date'].min(),
                end_date=df['date'].max(),
                display_format='YYYY-MM-DD'
            ),
        ], style={'display': 'inline-block', 'marginRight': '50px'}),

        html.Div([
            dcc.Checklist(
                id='category-filter',
                options=[{'label': 'Vid. Consejo de Estado', 'value': 'video'}],
                inline=True
            )
        ], style={'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '25px'}),

    html.Div(id='summary-text', style={'margin': '20px 0', 'fontSize': '18px'}),

    html.Div([
        html.Div([
            dcc.Graph(id='pie-chart')
        ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dcc.Graph(id='bar-chart')
        ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in ['username', 'tweets', 'influence_score', 'sentiment']],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center'},
                page_size=10
            )
        ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ])
])

@app.callback(
    [Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('data-table', 'data'),
     Output('summary-text', 'children')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('category-filter', 'value')]
)
def update_dashboard(start_date_str, end_date_str, video_selection):
    start_date = datetime.fromisoformat(start_date_str).date()
    end_date = datetime.fromisoformat(end_date_str).date()
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if video_selection:
        filtered_df = filtered_df[filtered_df['related']]

    pie_data = filtered_df['sentiment_llm'].value_counts(normalize=True).to_frame('Count').reset_index()
    pie_data['Count'] *=  100
    pie_fig = px.pie(pie_data, names='sentiment_llm', values='Count', title='Sentimiento Tweets')

    bar_data = pd.crosstab(filtered_df['date'], filtered_df['sentiment_llm']).reset_index()
    bar_fig = px.bar(bar_data, x="date", y=["NEUTRO", "NEGATIVO", "POSITIVO"], title="Distribución por día")

    
    filtered_df[['retweet_count', 'reply_count', 'like_count', 'quote_count', 'bookmark_count', 'impression_count']] = filtered_df['public_metrics'].progress_apply(lambda x: get_public_metrics(x))
    filtered_df["engagement"] = (
        filtered_df["retweet_count"] * 2   # A count of how many times the Post has been Retweeted. Does not include Quote Tweets (“Retweets with comment”).
        + filtered_df["reply_count"] * 1.5 # A count of how many times the Post has been replied to.
        + filtered_df["like_count"] * 1    # A count of how many times the Post has been liked.
        + filtered_df["quote_count"] * 2.5 # A count of how many times the Post has been Retweeted with a new comment (message).
    )
    user_stats = filtered_df.groupby("username").agg(
        tweets=("username", "count"),
        total_engagement=("engagement", "sum"),
        total_impressions=("impression_count", "sum"),
        avg_engagement=("engagement", "mean"),
        avg_impressions=("impression_count", "mean"),
        sentiment=("sentiment_llm", pd.Series.mode)
    ).reset_index()

    user_stats["influence_score"] = (
        user_stats["total_engagement"]*0.6 +
        user_stats["total_impressions"]*0.4
    )
    user_stats["influence_score"] = user_stats["influence_score"].round(1)
    table_data = user_stats.sort_values("influence_score", ascending=False)[['username', 'tweets', 'influence_score', 'sentiment']].reset_index(drop=True)
    table_data['sentiment'] = table_data['sentiment'].progress_apply(lambda sentiments: ", ".join(map(str, sentiments)) if isinstance(sentiments, list) else str(sentiments))
    print(table_data.head(20))
    
    table_data = table_data.to_dict('records')

    text_summary = f"Registros mostrados: {len(filtered_df)} (desde {start_date_str} hasta {end_date_str})"

    return pie_fig, bar_fig, table_data, text_summary


if __name__ == '__main__':
    app.run(debug=True)
