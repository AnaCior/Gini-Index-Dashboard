import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#Page configuration
st.set_page_config(
    page_title='Gini Index Dashboard',
    page_icon= '💸',
    layout='wide',
    initial_sidebar_state='expanded')

alt.themes.enable('dark')

#CSS styling of the page

#Load data
data = pd.read_csv('global_income_inequality_reshaped.csv')

#Sidebar
with st.sidebar:
    st.title('💸 Gini Index Dashboard')

    year_list = list(data.Year.unique())[::-1]
    selected_year = st.selectbox('Select a year', year_list)
    data_yr = data[data.Year == selected_year]
    data_yr_sorted = data_yr.sort_values(by='Gini_Index', ascending= False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

    #countries_list = list(data.Country.unique())[::-1]
    #selected_country = st.selectbox('Select a country', countries)
    #the beginning of trying to create the simple line charts with a selected country

#Plots
#Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Choropleth map
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(
        input_df,
        locations=input_id,
        color=input_column,
        locationmode="ISO-3",
        color_continuous_scale=input_color_theme,
        range_color=(0, max(data_yr.Gini_Index)),
        labels= {'Gini_Index': 'Gini_Index'},
    )
    
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

#Donut chart
def make_donut(input_response, input_text, input_color):
  if input_color == 'blue':
      chart_color = ['#29b5e8', '#155F7A']
  if input_color == 'green':
      chart_color = ['#27AE60', '#12783D']
  if input_color == 'orange':
      chart_color = ['#F39C12', '#875A12']
  if input_color == 'red':
      chart_color = ['#E74C3C', '#781F16']
    
  source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
  source_bg = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100, 0]
  })
    
  plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          #domain=['A', 'B'],
                          domain=[input_text, ''],
                          # range=['#29b5e8', '#155F7A']),  # 31333F
                          range=chart_color),
                      legend=None),
  ).properties(width=130, height=130)
    
  text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
  plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% value",
      color= alt.Color("Topic:N",
                      scale=alt.Scale(
                          # domain=['A', 'B'],
                          domain=[input_text, ''],
                          range=chart_color),  # 31333F
                      legend=None),
  ).properties(width=130, height=130)
  return plot_bg + plot + text

# Convert Gini Index to text 
def format_number(num):
    n = round(num, 2)
    return f'{(n)}'
   #if num > 1000000:
       # if not num % 1000000:
            #return f'{num // 1000000} M'
        #return f'{round(num / 1000000, 1)} M'
   # return f'{num // 1000} K'

# Calculation year-over-year Gini Index migrations
def calculate_difference_gini(data_set, year):
    selected_year = data_set[data_set['Year'] == year].reset_index()
    previous_year = data_set[data_set['Year'] == year - 1].reset_index()

    # Merge on Country or Country_codes to align both years
    merged = pd.merge(selected_year, previous_year, on="Country_codes", suffixes=('', '_prev'))
    
    merged['Gini_difference'] = merged.Gini_Index.sub(merged.Gini_Index_prev, fill_value=0)
    merged['Gini_absolute_difference'] = abs(merged.Gini_difference)
    
    return merged[['Country', 'Country_codes', 'Gini_Index', 'Gini_difference', 'Gini_absolute_difference']].sort_values(by="Gini_difference", ascending=False)



#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Gains/Losses')

    Gini_difference_sorted = calculate_difference_gini(data, selected_year)

    if selected_year > 2000:
        first_Country_name = Gini_difference_sorted.Country.iloc[0]
        first_Country_Gini_Index = format_number(Gini_difference_sorted.Gini_Index.iloc[0])
        first_Country_delta = format_number(Gini_difference_sorted.Gini_difference.iloc[0])
    else:
        first_Country_name = '-'
        first_Country_Gini_Index = '-'
        first_Country_delta = ''
    st.metric(label=first_Country_name, value=first_Country_Gini_Index, delta=first_Country_delta)

    if selected_year > 2000:
        last_Country_name = Gini_difference_sorted.Country.iloc[-1]
        last_Country_Gini_Index = format_number(Gini_difference_sorted.Gini_Index.iloc[-1])   
        last_Country_delta = format_number(Gini_difference_sorted.Gini_difference.iloc[-1])   
    else:
        last_Country_name = '-'
        last_Country_Gini_Index = '-'
        last_Country_delta = ''
    st.metric(label=last_Country_name, value=last_Country_Gini_Index, delta=last_Country_delta)

with col[1]:
    st.markdown('#### Gini Index Distribution')
    
    choropleth = make_choropleth(data_yr, 'Country_codes', 'Gini_Index', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)
    
    heatmap = make_heatmap(data, 'Year', 'Country', 'Gini_Index', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

    #st.markdown('#### Gini Index Evolution')

    #
    

with col[2]:
    st.markdown(
    """
    <style>
    .css-1l5jf47.e1tzin5v2 {
        width: 200px !important; /* Adjust width here */
    }
    </style>
    """,
    unsafe_allow_html=True
)
    st.markdown('#### Top Countries')

    st.dataframe(data_yr_sorted,
                 column_order=("Country", "Gini_Index"),
                 hide_index=True,
                 width=800,
                 column_config={
                    "Country": st.column_config.TextColumn(
                        "Countries",
                    ),
                    "Gini_Index": st.column_config.ProgressColumn(
                        "Gini Index",
                        format="%.2f",
                        min_value=0,
                        max_value=max(data_yr_sorted.Gini_Index),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data:
            https://www.kaggle.com/datasets/georgehanyfouad/global-income-inequality
            - :orange[**Gini Index**]: In economics, the Gini coefficient, also known as the Gini index or Gini ratio, is a measure of statistical dispersion intended to represent the income inequality, the wealth inequality, or the consumption inequality within a nation or a social group.
            ''')
