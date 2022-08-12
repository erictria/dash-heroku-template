import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"], low_memory=False)

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

wage_gap_link = 'https://www.epi.org/blog/equal-pay-day-there-has-been-little-progress-in-closing-the-gender-wage-gap/'
gss_link_1 = 'https://www.gss.norc.org/About-The-GSS'
gss_link_2 = 'https://www.gigeconomydata.org/research/data-sources/general-social-survey'

markdown_text = """
The gender wage gap has been a topic of discussion for quite some time now. Even though there has been more focus on gender rights and equality in more recent years, recent studies have shown that the gender wage gap is still pretty much present in society today. An article on the [Economy Policy Institute](https://www.epi.org/blog/equal-pay-day-there-has-been-little-progress-in-closing-the-gender-wage-gap/) discusses a study showing that the wage gap has not improved that much in recent years, with women on average still getting paid 21% less than men in 2021. In the article it was mentioned there is no one way of solving this issue. It would require a lot of policy and structural changes. This is definitely an interesting development to follow in the coming years.

One way to visualize this is through the data from the [GSS or General Social Survey](https://www.gss.norc.org/About-The-GSS). It is a survey that has been conducted in the United States of America Since 1972. The survey aims to provide insight on various social trends to see what the attitudes are of different demographics.The survey adapts as different social trends come up throughout the years. Keeping the questions in the survey up to date makes the survey a relevant source of information for social topics.

The survey contains different modules such as the [Quality of Working Life Module](https://www.gigeconomydata.org/research/data-sources/general-social-survey). As the trends and standards of working life continue to change in the United States, it is very helpful to see how the attitude of different demographics change with regards to the topics in question. The GSS data is easily accessible through their [website](https://gss.norc.org/get-the-data), which makes it very convenient for conducting various analyses.
"""

mean_values = gss_clean.groupby('sex').agg(
    {
        'income': 'mean',
        'job_prestige': 'mean',
        'socioeconomic_index': 'mean',
        'education': 'mean'
    }
).round(2).reset_index()
mean_values = mean_values.rename({
    'sex': 'Gender',
    'income': 'Income',
    'job_prestige': 'Job Prestige Score',
    'socioeconomic_index': 'Socioeconomic Index',
    'education': 'Education'
}, axis = 1)

table_fig = ff.create_table(
    mean_values
)

gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].astype('category')
gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].cat.reorder_categories([
    'strongly agree',
    'agree',
    'disagree',
    'strongly disagree'
])

male_bw = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index()
male_bw = male_bw.rename({0: 'count'}, axis = 1)

bar_fig = px.bar(
    male_bw, 
    x = 'male_breadwinner', 
    y = 'count',
    color = 'sex',
    barmode = 'group',
    labels = {
        'male_breadwinner': 'Response to Males as the Primary Breadwinner', 
        'count': 'Number of People',
        'sex': 'Gender'
    }
)

scatter_fig = px.scatter(
    gss_clean,
    x = 'job_prestige', 
    y = 'income', 
    color = 'sex',
    trendline = 'ols',
    labels = {
        'income':'Annual Income', 
        'job_prestige':'Job Prestige Score',
        'sex': 'Gender',
        'education': 'Education',
        'socioeconomic_index': 'Socioeconomic Index Score'
    },
    hover_data = ['education', 'socioeconomic_index']
)
scatter_fig.update(layout=dict(title=dict(x=0.5)))

income_box_fig = px.box(
    gss_clean, 
    x = 'sex', 
    y = 'income', 
    color = 'sex',
    labels = {'sex': '', 'income': 'Annual Income'}
)
income_box_fig.update(layout = dict(title = dict(x=0.5)))
income_box_fig.update_layout(showlegend = False)

prestige_box_fig = px.box(
    gss_clean, 
    x = 'sex', 
    y = 'job_prestige', 
    color = 'sex',
    labels = {'sex': '', 'job_prestige': 'Job Prestige Score'}
)
prestige_box_fig.update(layout = dict(title = dict(x=0.5)))
prestige_box_fig.update_layout(showlegend = False)

gss_subset = gss_clean[['income', 'sex', 'job_prestige']]
gss_subset['job_prestige_category'] = pd.cut(
    gss_subset.job_prestige,
    bins = 6,
    labels = (
        'Bin 1',
        'Bin 2',
        'Bin 3',
        'Bin 4',
        'Bin 5',
        'Bin 6'
    )
)
gss_subset = gss_subset.dropna()
gss_subset['job_prestige_category'] = gss_subset['job_prestige_category'].astype('category')
gss_subset['job_prestige_category'] = gss_subset['job_prestige_category'].cat.reorder_categories([
    'Bin 1',
    'Bin 2',
    'Bin 3',
    'Bin 4',
    'Bin 5',
    'Bin 6'
])

bin_box_fig = px.box(
    gss_subset, 
    x = 'sex', 
    y = 'income', 
    color = 'sex',
    facet_col = 'job_prestige_category',
    facet_col_wrap = 2,
    labels = {'sex': '', 'job_prestige_category': 'Job Prestige Category'},
    category_orders = {
        'job_prestige_category': [
            'Bin 1',
            'Bin 2',
            'Bin 3',
            'Bin 4',
            'Bin 5',
            'Bin 6'
        ]
    }
)
bin_box_fig.update(layout = dict(title = dict(x=0.5)))
bin_box_fig.update_layout(showlegend = False)

bars = [
    'satjob',
    'relationship',
    'male_breadwinner',
    'men_bettersuited',
    'child_suffer',
    'men_overwork'
]
groupings = [
    'sex',
    'region',
    'education'
]
label_map = {
    'satjob': 'Job Satisfaction',
    'relationship': 'Working Mother Maintains Relationship with Kids',
    'male_breadwinner': 'Male As Main Breadwinner',
    'men_bettersuited': 'Men Better Suited for Politics',
    'child_suffer': 'Child Suffers from Working Mothers',
    'men_overwork': 'Family Suffers from Men Overwork',
    'sex': 'Gender',
    'region': 'Region',
    'education': 'Education'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = html.Div(
    [
        html.H1('Exploring the 2019 General Social Survey'),
        
        dcc.Markdown(children = markdown_text),
        
        html.H2('Comparing Genders'),
        
        dcc.Graph(figure = table_fig),
        
        html.H2('Responses to Various Questions'),
        
        html.Div([
            html.Div([
            
                html.H3('Category to Visualize'),

                dcc.Dropdown(
                    id = 'bars_dropdown',
                    options = [{'label': label_map[i], 'value': i} for i in bars],
                    value = 'male_breadwinner'
                ),
                
                
                html.H3('Grouping'),

                dcc.Dropdown(
                    id = 'grouping_dropdown',
                    options = [{'label': label_map[i], 'value': i} for i in groupings],
                    value = 'sex'
                )

            ], style = {'width': '25%', 'float': 'left'}),
            
            html.Div([
                dcc.Graph(id = 'interactive_graph')
            ], style = {'width': '70%', 'float': 'left'})
        ]),
        
        html.H2('Comparing Annual Income and Job Prestige by Gender'),
        
        dcc.Graph(figure = scatter_fig),
        
        html.H2('Comparing Income and Job Prestige Distribution by Gender'),
        
        html.Div([
            
            dcc.Graph(figure = income_box_fig)
        
        ], style = {'width': '48%', 'float': 'left'}),
        
        html.Div([
            
            dcc.Graph(figure = prestige_box_fig)
        
        ], style = {'width': '48%', 'float': 'right'}),
        
        html.H2('Comparing Income Distributions per Job Prestige Bins'),
        
        dcc.Graph(figure = bin_box_fig),
    
    ]
)

@app.callback(
    Output(component_id = 'interactive_graph', component_property = 'figure'), 
    [
        Input(component_id = 'bars_dropdown', component_property = 'value'),
        Input(component_id = 'grouping_dropdown', component_property = 'value'),
    ]
)
def make_figure(bars, grouping):
    new_df = gss_clean.groupby([grouping, bars]).size().reset_index()
    new_df = new_df.rename({0: 'count'}, axis = 1)
    
    fig =  px.bar(
        new_df, 
        x = bars, 
        y = 'count',
        color = grouping,
        barmode = 'group',
        labels = {
            bars: label_map[bars], 
            grouping: label_map[grouping],
            'count': 'Number of People'
        },
        title = ''
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
