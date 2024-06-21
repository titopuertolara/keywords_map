from dash import Dash, dcc, html, Input, Output, callback,State,ctx
import os

import pickle
from utils import *
from collections import Counter
import plotly.express as px
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
def get_percent(variable,value,ref_dict):
    try:
        return round(100*value/ref_dict[variable],2)
    except:
        return 0

#class tags_object:
#    def __init__(self,tags):
#        self.tags=tags

#tags=[]
#tags_obj=tags_object(tags)
dbref=pd.read_csv('keys_db_petis.csv')

#print(dir(tags_obj))
with open('capitales.pkl','rb') as cpfile:
    capitals=pickle.load(cpfile)
with open('gobernaciones.pkl','rb') as gbfile:
    gobernaciones=pickle.load(gbfile)
cat_list=['Capitales','Gobernaciones']
app.layout = html.Div([
    html.H2('Análisis de clusters por palabras Clave', style={'text-align': 'center', 'margin-bottom': '20px'}),
    html.H3('Proyectos de infraestructura tecnológica en Capitales y gobernaciones de Colombia', style={'text-align': 'center', 'margin-bottom': '30px'}),
    
    html.Div([
        dcc.Input(id='tag-input', type='text', placeholder='Escribir palabra clave', style={'width': '60%', 'margin-right': '10px'}),
        html.Button('Agregar palabra clave', id='add-btn')
    ], style={'display': 'flex', 'justify-content': 'center', 'margin-bottom': '30px'}),
    
    html.Div([
        dcc.Dropdown(
            id='categories', 
            options=[{'label': i, 'value': i} for i in cat_list], 
            value='Capitales', 
            style={'flex': '1', 'margin-right': '10px'}
        ),
        dcc.Dropdown(
            id='tag-in', 
            multi=True, 
            style={'flex': '2'}
        )
    ], style={'display': 'flex', 'justify-content': 'center', 'margin-bottom': '30px'}),
    
    dcc.Loading(id='loading1',children=[html.Div(id='treemap-chart', style={'width': '90%', 'margin': '0 auto', 'text-align': 'center'})],type='cube'),
    
    # Add CSS for dropdown arrow visibility
    
], style={'max-width': '1500px', 'margin': '0 auto'})  # Center the container on the page


@callback(Output('tag-in', 'options') ,
          Output('tag-in', 'value'),
          [Input('add-btn','n_clicks'),
           State('tag-input', 'value'),
           State('tag-in','options'),
           State('tag-in','value')])
def display_value(nclicks,value,options,opts_value):
    print('opciones',options)
    #print(value)
    #if options is None:
    #    options=[]
    print('opciones_valor',opts_value)
    if opts_value is None:
        opts_value=[]
    
    #if len(opts_value)==0:
    #    tags_obj.tags=[]


    
    if ctx.triggered_id=='add-btn':
        
        if value is not None and value.strip()!='':
            tags_list=[option['label'] for option in options]
            value=value.lower()
            if value not in tags_list:
                #tags_obj.tags.append(value.lower())
                options.append({'label':value,'value':value})


            #print(options)
        #def_options=[{'label':i,'value':i} for i in list(set(tags_obj.tags))]    



        return options,[option['value'] for option in options]

    return [],[]
@callback(Output('treemap-chart','children'),
          Output('tag-in','options' ,allow_duplicate=True),
          [Input('tag-in','value'),
           Input('categories','value')], prevent_initial_call=True)
def plot_chart(key_tags,category):
    
    if key_tags is None:
        key_tags=[]
    if len(key_tags)==0:
        #key_tags=[]
        return '',[]
    else:
        if category=='Capitales':
            pdf_column='Cap_PDF'
            doclist=capitals
            ref_column='Capital'
        else:
            pdf_column='Gob_PDF'
            doclist=gobernaciones
            ref_column='Departamento'
        narrative_df=get_referenced_with_pages(key_tags,doclist,column_name='motivations')
        narrative_df=narrative_df.merge(dbref,how='left',left_on='pdf',right_on=pdf_column)
        #print(narrative_df.head())
        base_dict={'location':[]}
        for i in key_tags:
            base_dict[i]=[]
        base_df=pd.DataFrame(base_dict)
        for i in narrative_df.index:
            base_df.loc[i,'location']=narrative_df.loc[i,ref_column]
            hist_words=[j[0] for j in narrative_df.loc[i,'motivations']]
            cnt=Counter(hist_words)
            #print(cnt)
            for k in key_tags:
                try:
                    base_df.loc[i,k]=cnt[k]
                except:
                    pass
        
        melted_df=pd.melt(base_df,id_vars=['location'],value_vars=key_tags)
        melted_df['variable']=melted_df['variable'].apply(lambda x: x.upper())
        melted_df=melted_df[~melted_df['location'].isnull()]
        total_ref=melted_df.groupby(['variable']).sum().reset_index()
        ref_dict={variable:value for variable,value in zip(total_ref['variable'],total_ref['value'])}
        melted_df['percentage']=melted_df.apply(lambda x: get_percent(x['variable'],x['value'],ref_dict),axis=1)

        
        #print(melted_df)
        fig = px.treemap(melted_df[melted_df['value']!=0], path=[px.Constant('Keywords'), 'variable', 'location'], values='value',
                  color='value', hover_data={'value':False,'percentage':False},
                  color_continuous_scale='geyser',
                  custom_data=['percentage', 'location'],

                )
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        fig.update_traces(
            texttemplate='%{label}<br>%{customdata[0]:.2f}%',
            hovertemplate='%{customdata[1]} %{customdata[0]}%<extra></extra>'
    
        )
        tree_chart=dcc.Graph(figure=fig)
        #print(key_tags)
        #tags_obj.tags=[i for i in key_tags]
        options=[{'label':i,'value':i} for i in key_tags]
        return tree_chart,options

        



if __name__ == '__main__':
    app.run(debug=True)