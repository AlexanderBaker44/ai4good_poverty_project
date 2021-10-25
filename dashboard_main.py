import streamlit as st
import pandas as pd
import pickle as pkl
import plotly.express as px
from statsmodels.tsa.arima.model import ARIMA

st.set_option('deprecation.showPyplotGlobalUse', False)
page_select=st.sidebar.radio('Select Page',['Snapshot','Change','Regions'])
snapshot_group=pd.read_csv('snapshot.csv')
change_groups=pd.read_csv('change_group.csv')
time_df=pd.read_csv('time_series_set.csv')
country_codes=pd.read_csv('countries_to_code.csv')


#df = px.data.gapminder().query("year == 2007")
#fig = px.scatter_geo(health_survival_m_2016, locations='Country Code',size='First Tooltip',color='classification' )
#fig.show()

def time_series(data,params,number_forecast):
    data_t=data.T
    data_t.columns=['values']


    proper=data_t.dropna()
    final_val=proper.index[len(proper.index)-1]

    diff=2018-int(final_val)


    model = ARIMA(proper, order=params)
    model_fit = model.fit()
    forecast_nums=model_fit.forecast(number_forecast+diff)

    print(forecast_nums)
    years=[i+(2019-diff) for i in range(number_forecast+diff)]
    print(years)
    forecasts=pd.DataFrame({'year':years,'values':forecast_nums})
    #print(forecasts)

    forecasts['year']=[int(i) for i in forecasts['year']]
    forecasts.set_index('year',inplace=True)

    display_data=pd.concat([proper,forecasts],axis=0)


    return display_data

file = open('params.pkl','rb')
dict=pkl.load(file)
file.close()

#snapshot, cluster and give the ability to analyze country by a certain metric
# read from the set
if page_select=='Snapshot':
    cols=snapshot_group.drop(['Country_New','classification'],axis=1).columns
    option_snap=st.selectbox("Select Attribute",cols)
    with_cc_2016=pd.merge(snapshot_group,country_codes,left_on='Country_New',right_on='Country_New',how='left')
    with_cc_2016.fillna(0,inplace=True)
    fig = px.scatter_geo(with_cc_2016, locations='Country Code',size=option_snap,color='classification' )
    st.plotly_chart(fig)

#change from 2010-2015 give the ability to analyze country by a certain metric
#read from the set
if page_select=='Change':
    cols_change=change_groups.drop(['Country_New','classification'],axis=1).columns
    option_change=st.selectbox("Select Attribute",cols_change)
    with_cc_change=pd.merge(change_groups,country_codes,left_on='Country_New',right_on='Country_New',how='left')

    with_cc_change.fillna(0,inplace=True)
    with_cc_change[option_change]=[abs(i) for i in with_cc_change[option_change]]
    fig = px.scatter_geo(with_cc_change, locations='Country Code',size=option_change,color='classification' )
    st.plotly_chart(fig)
#Line charts with all 7 regions, give the ability to filter by such region
#forecast and train models on the fly.

if page_select=='Regions':
    forecasted_numbers=[]
    series=st.multiselect("Select Sequences to Display",time_df['Type'])
    df_list_190=[]
    df_list_prim=[]
    titles_190=[]
    titles_prim=[]
    for i in series:

        data_selected=time_df[time_df['Type']==i]
        entered=data_selected.drop(['Type'],axis=1)
        parameters=dict[i]
        forecasted_numbers=time_series(entered,parameters,5)

        if '190' in i:
            titles_190.append(i)
            df_list_190.append(forecasted_numbers)
            df_190_full=pd.concat(df_list_190,axis=1)


        if 'Primary' in i:
            titles_prim.append(i)
            df_list_prim.append(forecasted_numbers)
            df_prim_full=pd.concat(df_list_prim,axis=1)


    if df_list_190!=[]:
        df_190_full.columns=titles_190
        df_190_full.plot(kind='line',title=i)
        st.pyplot()

    if df_list_prim!=[]:
        df_prim_full.columns=titles_prim
        df_prim_full.plot(kind='line',title=i)
        st.pyplot()
    #st.write(forecasted_numbers)


    #st.write(df_series)
