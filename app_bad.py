from dash import Dash, dcc, html, Input, Output, callback,State,ctx
import os
import dash_daq as daq
import pickle
from utils import *
from collections import Counter
import plotly.express as px
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
def get_percent(variable,value,ref_dict):
    return round(100*value/ref_dict[variable],2)

class tags_object:
    def __init__(self,tags):
        self.tags=tags

tags=[]
tags_obj=tags_object(tags)
dbref=pd.read_csv('keys_db_petis.csv')

#print(dir(tags_obj))
with open('capitales.pkl','rb') as cpfile:
    capitals=pickle.load(cpfile)
with open('gobernaciones.pkl','rb') as gbfile:
    gobernaciones=pickle.load(gbfile)
cat_list=['Capitales','Gobernaciones']
app.layout = html.Div([
    dcc.Dropdown(id='categories',options=[{'label':i,'value':i} for i in cat_list],value='Capitales'),
    dcc.Input(id='tag-input',type='text',placeholder='Put some keyword'),
    html.Button('Add Tag',id='add-btn'),
    dcc.Dropdown(id='tag-in',multi=True),
    
    #html.Div(id='display-keywords'),
    html.Div(id='treemap-chart')
])



@callback(Output('tag-in', 'options') ,
          Output('tag-in', 'value'),
          [Input('add-btn','n_clicks'),
           State('tag-input', 'value'),
           State('tag-in','options'),
           State('tag-in','value')])
def display_value(nclicks,value,options,opts_value):
    #print(options)
    #print(value)
    #if options is None:
    #    options=[]
    print(opts_value)
    if opts_value is None:
        opts_value=[]
    
    if len(opts_value)==0:
        tags_obj.tags=[]


    
    if ctx.triggered_id=='add-btn':
        
        if value is not None and value.strip()!='':
            if value not in tags_obj.tags:
                tags_obj.tags.append(value.lower())

            #print(options)
        def_options=[{'label':i,'value':i} for i in list(set(tags_obj.tags))]    



        return def_options,tags_obj.tags

    return [{'label':'','value':''}],[]
@callback(Output('treemap-chart','children'),
          [Input('tag-in','value'),
           Input('categories','value')])
def plot_chart(key_tags,category):
    
    if key_tags is None:
        key_tags=[]
    if len(key_tags)==0:
        tags_obj.tags=[]
        return ''
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
        tags_obj.tags=[i for i in key_tags]
        return tree_chart

        



if __name__ == '__main__':
    app.run(debug=True)