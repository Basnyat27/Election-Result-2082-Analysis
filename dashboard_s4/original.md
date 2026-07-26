# **Dashboard Code** (v1)

> The dashboard was **initially developed entirely by me**. The code shown here is the original implementation before being refactored with AI assistance to improve readability, maintainability, and code organization.

```python
import streamlit as st
import numpy as np 
import pandas as pd
import plotly.express as px 

st.set_page_config(layout='wide')

# Load the cleaned election dataset
df = pd.read_csv("cleaned_data_v2.csv")


# Display the main title of the dashboard
st.markdown("# Nepal Election Results 2082 :blue[(2026)]")

# Add a title to the sidebar
st.sidebar.title('Election Data Analysis')

# Create a dropdown menu to select the analysis type
options = st.sidebar.selectbox('Select One', ['Overall analysis','Party-wise','Candidate-wise'])

# Show the Overall Analysis page
if options == 'Overall analysis':
    st.markdown('## Overall Analysis')

    fig = px.scatter_map(df, lat='latitude', lon='longitude', size='votes', color='province', zoom=5, size_max=20, 
                                hover_name='constituency', hover_data=['party','candidate','is_winner'], map_style='carto-positron')
    st.plotly_chart(fig, width='stretch', height=680)

    with st.container(border=False):
        bar_chart, pie_chart = st.columns([3, 1])
        
        top_10_const = df.groupby('constituency')['votes'].sum().nlargest(10).index
        top_5_parties = df.groupby('party')['votes'].sum().nlargest(5).index

        temp_df = df.groupby(['constituency', 'party'], as_index=False)['votes'].sum()

        temp_df['const_grouped'] = temp_df['constituency'].apply(lambda x: x if x in top_10_const else 'Others')
        temp_df['party_grouped'] = temp_df['party'].apply(lambda x: x if x in top_5_parties else 'Others')

        plot_df = temp_df.groupby(['const_grouped', 'party_grouped'], as_index=False)['votes'].mean()
        plot_df = plot_df.rename(columns={'const_grouped': 'constituency', 'party_grouped': 'party'})

        fig = px.bar(
            plot_df,
            x='constituency',
            y='votes',
            color='party',
            labels={'votes': 'avg votes'},
            title='Top 10 Constituencies By Top 5 Parties',
            category_orders={
                'constituency': list(top_10_const) + ['Others'],
                'party': list(top_5_parties) + ['Others']
            }
        )
        bar_chart.plotly_chart(fig, width='stretch', height='content')


        temp_seri = df.groupby('party')['votes'].sum()
        top_5 = temp_seri.nlargest(5).index

        fig = px.pie(
            temp_seri.rename(lambda x: x if x in top_5 else 'Others').groupby(level=0).mean().reset_index(name='votes'),
            values='votes',
            hole=0.0, 
            hover_name='party', 
            title='Parties Vote Share %'
        )
        pie_chart.plotly_chart(fig)

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        col1.metric('VOTES', df['votes'].sum())

        temp_df = df.groupby('constituency')[['votes_cast','total_voters']].head(1)
        col2.metric('TURNOUT %', round((temp_df['votes_cast'].sum() / temp_df['total_voters'].sum()) * 100, 2))

        col3.metric('FEMALES', df.query("gender == 'F'")['candidate'].count())
        col4.metric('MALES', df.query("gender == 'M'")['candidate'].count())


    st.subheader("Top 20 Candidates")
    temp_df = df.query("is_winner == True").groupby(by=['candidate','party','constituency'])['votes'].sum().reset_index().nlargest(n=20, columns='votes')
    temp_df['rank'] = temp_df['votes'].rank(ascending=False).astype(int)
    st.dataframe(temp_df[['rank','candidate','party','constituency','votes']].set_index('rank'))


        


    # # This box stays 300 pixels tall, scrolling internally if content overflows
    # with st.container(height=300):
        
    #     for i in range(1, 15):
    #         st.write(f"📢 Update {i}: District {i} counting has started.")



    # # Side-by-side metrics using columns
    # col1, col2, col3 = st.columns(3)

    # col1.metric(
    #     label="Active Users", 
    #     value="12,540", 
    #     delta="1,200",
    #     help="Total users online in the last 24 hours"
    # )

    # col2.metric(
    #     label="Server Latency", 
    #     value="42 ms", 
    #     delta="-5 ms", 
    #     delta_color="inverse"  # Negative change is good for latency
    # )

    # col3.metric(
    #     label="Conversion Rate", 
    #     value="3.2%", 
    #     delta="0.4%"
    # )




# Show the Party-wise Analysis page
elif options == 'Party-wise':
    st.markdown('## Party-wise Analysis')
    selected_party = st.sidebar.selectbox('Select Party', df['party'].unique())      # Dropdown to select a political party
    btn1 = st.sidebar.button('Find Party Details')                  # Button to display party details

    if btn1:
        temp_df = df[df['party'] == selected_party]

        temp_df2 = df.groupby(by=['party'])['votes'].sum().reset_index()
        temp_df2['rank'] = temp_df2['votes'].rank(ascending=False).astype(int)
        party_rank = temp_df2[temp_df2['party'] == selected_party]['rank'].values[0]

        with st.container(border=False):
            # Vertically align elements inside the columns row
            col1, col2, col3 = st.columns([1, 3, 1], vertical_alignment="center")

            symbol_url = temp_df['party_symbol'].unique()[0]
            # Fixed: Replaced width='content' with use_container_width=True
            if pd.notna(symbol_url):
                col1.image(
                    symbol_url,
                    caption=f'# {party_rank}',
                    use_container_width=True
                )
            else:
                col1.image(
                    "independent.jpg",
                    caption=f'# {party_rank}',
                    use_container_width=True
                )

            
            col2.title(selected_party)

            col3.metric('WINS', temp_df[temp_df['is_winner'] == True]['candidate'].count())
            col3.metric('VOTE SHARE %', round((temp_df['votes'].sum()/temp_df2['votes'].sum())*100, 2))


        const_series = temp_df.groupby('constituency')['votes'].sum()
        top_10 = const_series.nlargest(10).index
        fig = px.bar(
            const_series.rename(lambda x: x if x in top_10 else 'Others').groupby(level=0).mean().reset_index(name='votes'),
            x='constituency',
            y='votes',
            labels={'votes':'avg votes'},
            title='Top 10 Constituencies',
        )

        st.plotly_chart(fig, width='stretch', height='content')

        temp_df3 = temp_df.sort_values(by=['votes','is_winner'], ascending=[False,True])[['candidate','constituency','is_winner','votes']]
        temp_df3['rank'] = np.arange(temp_df3.index.size) + 1
        st.dataframe(temp_df3.set_index('rank'))


# Show the Candidate-wise Analysis page
elif options == 'Candidate-wise':
    st.markdown('## Candidate-wise Analysis')
    selected_candidate = st.sidebar.selectbox('Select Candidate', sorted(df['candidate'].unique().tolist()))     # Dropdown to select a candidate (sorted alphabetically)
    btn2 = st.sidebar.button('Find Candidate Details')                                      # Button to display candidate details

    if btn2:
        temp_df = df[df['candidate'] == selected_candidate]

        temp_df2 = df.groupby(by=['candidate_id','candidate'])['votes'].sum().reset_index()
        temp_df2['rank'] = temp_df2['votes'].rank(ascending=False).astype(int)
        candidate_rank = temp_df2[temp_df2['candidate'] == selected_candidate]['rank'].values[0]


        with st.container(border=True, width='stretch', horizontal=True, horizontal_alignment='right', vertical_alignment='top'):

            photo_url = temp_df['candidate_photo'].values[0]
            
            st.image(
                photo_url,
                caption=f'# {candidate_rank}',
                # use_container_width=True
                width=250
                )
                
            with st.container(border=False, gap='small'):
                    
                col1,col2 = st.columns([3,1], border=False, vertical_alignment='center')
                if (temp_df['is_winner']).values == True:
                    col1.success(temp_df['constituency'].values[0], icon='🏆', width=200)

                    if pd.notna(temp_df['party_symbol'].values[0]):
                        col2.image(temp_df['party_symbol'].values[0], width=100)
                    else:
                        col2.image('independent.jpg', width=100)
                else:
                    col1.error(temp_df['constituency'].values[0], width=200)

                    if pd.notna(temp_df['party_symbol'].values[0]):
                        col2.image(temp_df['party_symbol'].values[0], width=100)
                    else:
                        col2.image('independent.jpg', width=100)
                st.title(selected_candidate)

                col3,col4 = st.columns([3,1], border=False, gap='xsmall', vertical_alignment='top')
                col3.subheader(f"({temp_df['party'].values[0]})")
                col4.metric(
                    f"VOTES ({round(temp_df['votes'] / df[df['constituency' ] == temp_df['constituency'].values[0]]['votes'].sum() * 100, 2).values[0]}%)", 
                    temp_df['votes'].values[0]
                    )
        

        with st.container(border=False, horizontal=True, vertical_alignment='bottom'):
            pass
            
            with st.container(border=False):
                
                st.markdown("#### :gray[PERSONAL INFORMATION]")
                pass
                with st.container(border=True, gap='xxsmall'):
                    pass
                    candidate_info = ['gender','father','spouse','address','qualification','experience']
                    col5, = st.columns(1)
                    col5.write(f"***GENDER:**  {("Male" if temp_df[candidate_info]['gender'].values[0] == 'M' else "Female")}*")
                    col5.write(f"***FATHER:**  {temp_df[candidate_info]['father'].values[0]}*")
                    col5.write(f"***SPOUSE:**  {temp_df[candidate_info]['spouse'].values[0]}*")
                    col5.write(f"***ADDRESS:**  {temp_df[candidate_info]['address'].values[0]}*")
                    col5.write(f"***EDUCATION:**  {temp_df[candidate_info]['qualification'].values[0]}*")
                    col5.write(f"***EXPERIENCE:**  {temp_df[candidate_info]['experience'].values[0]}*")
                    

            with st.container(border=True):

                st.subheader(":rainbow[Top 5 Rivals]")
                pass
                with st.container(border=False):
                    rivals = df[df['constituency'] == temp_df['constituency'].values[0]][['candidate','party','votes']]
                    st.dataframe(rivals[~(rivals['candidate'] == selected_candidate)].nlargest(5, 'votes').set_index('candidate'))
            


                # col1,col2 = st.columns([1,3], border=True)
                # col1.image(temp_df['party_symbol'].values[0])
                # col2.write(temp_df['party'].values[0])


            # col1,col2 = st.columns(2, border=True)

            # col1.header(selected_candidate)

            # # Vertically align elements inside the columns row
            # col1, col2 = st.columns([1, 1], vertical_alignment="center")

            # photo_url = temp_df['candidate_photo'].values[0]
            # # Fixed: Replaced width='content' with use_container_width=True
            
            # col1.image(
            #     photo_url,
            #     caption=f'# {candidate_rank}',
            #     # use_container_width=True
            #     )
```
