# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 15:17:32 2022

@author: julian
"""

from dash import Dash, html, dcc, dash_table
import plotly.express as px
import base64
import pandas as pd

path = "./"
        
app = Dash(__name__)

app.title = '8erlijke statistieken'

server = app.server


stats_overview = pd.read_csv(path+'stats.csv')
opstelling_figure = "./opstelling.png"

test_base64 = base64.b64encode(open(opstelling_figure, 'rb').read()).decode('ascii')



goals_assists = stats_overview.loc[0:len(stats_overview)-3,'Arjan':'Tom']

goals_assists_usable = pd.DataFrame(columns=list(goals_assists.keys()+ '_doelpunten') + list(goals_assists.keys()+ '_assists'))


for key in goals_assists.keys():
    for index in goals_assists.index:
        if index % 2 == 0: # Kijken we naar doelpunten
            actual_index = int(index/2)
            datum = stats_overview.loc[index,'Datum']
            goals_assists_usable.loc[actual_index,'Datum'] = datum
            goals_assists_usable.loc[actual_index,key + '_doelpunten'] = goals_assists.loc[index,key]
        else:
            actual_index = int(index/2)
            goals_assists_usable.loc[actual_index,key + '_assists'] = goals_assists.loc[index,key]
    
        
df_cumulative_goals_assists = goals_assists_usable.loc[:,'Arjan_doelpunten':'Tom_assists'].cumsum()
df_cumulative_goals_assists['Datum'] = goals_assists_usable.Datum

df_stats_melted = goals_assists_usable.melt(id_vars = 'Datum',  value_vars= goals_assists_usable.keys()[0:-1])
df_stats_cum_melted = df_cumulative_goals_assists.melt(id_vars = 'Datum',  value_vars= goals_assists_usable.keys()[0:-1])
df_stats_melted['assist'] = False
df_stats_cum_melted['assist'] = False

for index in df_stats_melted.index:
    if 'assists' in df_stats_melted.loc[index,'variable']:
        df_stats_melted.loc[index,'assist'] = True
        df_stats_cum_melted.loc[index,'assist'] = True
        

# Creating the figures
fig0 = px.line(df_stats_cum_melted, x = "Datum", y = "value", color = 'variable', 
           line_dash='assist',title='Cumulatief Goals/Assists',
           labels={"value":'Aantal'})
fig1 = px.bar(df_stats_melted, x = "Datum", y = "value", color = 'variable',
           pattern_shape = 'assist',title='Goals/Assists per wedstrijd',
           labels={"value":'Aantal'})
    

app.layout = html.Div(children=[
                        dcc.Tabs([
                            dcc.Tab(label='Statistieken',children=[
                                    html.Div(dcc.Graph(id='cumulative-goals', figure=fig0)),
                                    html.Div(dcc.Graph(id='individual-matches',figure=fig1),
                                             style={'marginBottom':'88px'}),
                                    html.Div([dash_table.DataTable(id='manual-input-editable-table',
                                     data=stats_overview.to_dict('records'), 
                                     columns= [{"name": i, "id": i} for i in stats_overview.columns[0:-1]],
                                     style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(220, 220, 220)'},
                                                             {'if': {'column_id': 'asset_name'},'fontWeight': 'bold' }],
                                     style_cell={'height': 'auto','minWidth': '50px', 'width': '50px', 'maxWidth': '80px', 'whiteSpace': 'normal'},
                                     style_header={'fontWeight': 'bold'},
                                     editable=False
                                     )],
                                    style={'marginBottom': 50, 'width': '100%', 'display': 'inline-block'})]),
                        dcc.Tab(label='Opstelling', children=[
                                html.Div([html.Img(src='data:image/png;base64,{}'.format(test_base64)),]),])
                        ])])


if __name__ == '__main__':
    app.run_server(debug=True)
