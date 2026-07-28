import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. PAGE SETUP & DATA LOADING
# ---------------------------------------------------------
st.set_page_config(layout='wide')

# Load the cleaned election dataset
from pathlib import Path
BASE_DIR = Path(__file__).parent
election_data = pd.read_csv(BASE_DIR / "cleaned_data_v2.csv")    # when relative path not working on deployment

# Display the main dashboard title
st.title("Nepal Election Results 2082 :blue[(2026)]")

# ---------------------------------------------------------
# 2. SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title('Election Analysis Menu')
analysis_choice = st.sidebar.selectbox(
    'Choose a category to explore:', 
    ['Overall Analysis', 'Party-wise', 'Candidate-wise']
)


# =========================================================
# PAGE 1: OVERALL ANALYSIS
# =========================================================
if analysis_choice == 'Overall Analysis':
    st.header('Overall Analysis')

    # --- MAP VISUALIZATION ---
    # Display a scatter map of votes across different constituencies
    map_fig = px.scatter_map(
        election_data, 
        lat='latitude', 
        lon='longitude', 
        size='votes', 
        color='province', 
        zoom=5, 
        size_max=20, 
        hover_name='constituency', 
        hover_data=['party', 'candidate', 'is_winner'], 
        map_style='carto-positron'
    )
    st.plotly_chart(map_fig, width='stretch')

    # --- CHARTS SECTION ---
    with st.container(border=False):
        bar_chart_col, pie_chart_col = st.columns([3, 1])
        
        # 1. Bar Chart: Top 10 Constituencies by Top 5 Parties
        top_10_constituencies = election_data.groupby('constituency')['votes'].sum().nlargest(10).index
        top_5_parties = election_data.groupby('party')['votes'].sum().nlargest(5).index

        # Group data by constituency and party
        constituency_party_votes = election_data.groupby(['constituency', 'party'], as_index=False)['votes'].sum()

        # Group anything outside the Top 10/Top 5 into "Others"
        constituency_party_votes['const_grouped'] = constituency_party_votes['constituency'].apply(lambda x: x if x in top_10_constituencies else 'Others')
        constituency_party_votes['party_grouped'] = constituency_party_votes['party'].apply(lambda x: x if x in top_5_parties else 'Others')

        # Calculate average votes for the grouped data
        avg_votes_df = constituency_party_votes.groupby(['const_grouped', 'party_grouped'], as_index=False)['votes'].mean()
        avg_votes_df = avg_votes_df.rename(columns={'const_grouped': 'constituency', 'party_grouped': 'party'})

        bar_fig = px.bar(
            avg_votes_df,
            x='constituency',
            y='votes',
            color='party',
            labels={'votes': 'Avg Votes'},
            title='Top 10 Constituencies By Top 5 Parties',
            category_orders={
                'constituency': list(top_10_constituencies) + ['Others'],
                'party': list(top_5_parties) + ['Others']
            }
        )
        bar_chart_col.plotly_chart(bar_fig, width='stretch')

        # 2. Pie Chart: Vote Share % of Top 5 Parties
        party_vote_totals = election_data.groupby('party')['votes'].sum()
        
        pie_fig = px.pie(
            party_vote_totals.rename(lambda x: x if x in top_5_parties else 'Others').groupby(level=0).mean().reset_index(name='votes'),
            values='votes',
            hole=0.0, 
            hover_name='party', 
            title='Parties Vote Share %'
        )
        pie_chart_col.plotly_chart(pie_fig, width='stretch')

    # --- METRICS SECTION ---
    with st.container(border=True):
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        # Calculate Total Votes
        metric_col1.metric('TOTAL VOTES', election_data['votes'].sum())

        # Calculate Voter Turnout Percentage
        turnout_data = election_data.groupby('constituency')[['votes_cast', 'total_voters']].head(1)
        turnout_percentage = (turnout_data['votes_cast'].sum() / turnout_data['total_voters'].sum()) * 100
        metric_col2.metric('TURNOUT %', round(turnout_percentage, 2))

        # Count Female and Male Candidates
        metric_col3.metric('FEMALE CANDIDATES', election_data[election_data['gender'] == 'F']['candidate'].count())
        metric_col4.metric('MALE CANDIDATES', election_data[election_data['gender'] == 'M']['candidate'].count())

    # --- TOP 20 CANDIDATES TABLE ---
    st.subheader("Top 20 Winning Candidates")
    winning_candidates = election_data[election_data['is_winner'] == True]
    top_20_winners = winning_candidates.groupby(['candidate', 'party', 'constituency'])['votes'].sum().reset_index().nlargest(20, 'votes')
    
    top_20_winners['rank'] = top_20_winners['votes'].rank(ascending=False).astype(int)
    st.dataframe(top_20_winners[['rank', 'candidate', 'party', 'constituency', 'votes']].set_index('rank'))


# =========================================================
# PAGE 2: PARTY-WISE ANALYSIS
# =========================================================
elif analysis_choice == 'Party-wise':
    st.header('Party-wise Analysis')
    
    selected_party = st.sidebar.selectbox('Select a Party', election_data['party'].unique())
    search_party_btn = st.sidebar.button('Find Party Details')

    if search_party_btn:
        # Filter data for the selected party
        party_data = election_data[election_data['party'] == selected_party]

        # Calculate party rankings based on total votes
        party_rankings = election_data.groupby('party')['votes'].sum().reset_index()
        party_rankings['rank'] = party_rankings['votes'].rank(ascending=False).astype(int)
        
        current_party_rank = party_rankings[party_rankings['party'] == selected_party]['rank'].values[0]
        total_party_votes = party_rankings['votes'].sum()

        # --- PARTY HEADER & METRICS ---

        import io
        import requests
        # import pandas as pd
        # import streamlit as st
        from PIL import Image
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Cache the image so it only downloads ONCE per hour, not on every user click
        @st.cache_data(ttl=3600)
        def fetch_symbol_image(url):
            if pd.isna(url) or not str(url).startswith('http'):
                return None
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(url, headers=headers, timeout=5, verify=False)
                response.raise_for_status()
                # Open image using Pillow
                return Image.open(io.BytesIO(response.content))
            except Exception:
                return None

        # --- UI CODE ---
        with st.container(border=False):
            logo_col, name_col, stats_col = st.columns([1, 3, 1], vertical_alignment="center")
            
            symbol_url = party_data['party_symbol'].unique()[0]
            symbol_img = fetch_symbol_image(symbol_url)
            
            with logo_col:
                # If remote image fails, pass local file path
                display_target = symbol_img if symbol_img else str(BASE_DIR / "independent.JPG")
                st.image(display_target, caption=f'Rank: #{current_party_rank}', use_container_width=True)

            name_col.title(selected_party)

        # import requests
        # import base64
        # import urllib3

        # # Suppress warnings if the target website has a broken SSL certificate
        # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # def force_display_image(url, fallback_path):
        #     """
        #     Fetches an image bypassing 403s, SSL errors, and CORS, then converts it 
        #     to a Base64 HTML string so the browser is forced to render it.
        #     """
        #     if pd.isna(url) or not str(url).startswith('http'):
        #         return {"type": "local", "content": fallback_path}
                
        #     try:
        #         # 1. Spoof a full Chrome browser to bypass anti-scraping walls
        #         headers = {
        #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        #             "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        #             "Referer": url # Tricks the server into thinking the request comes from its own site
        #         }
                
        #         # 2. verify=False forces the download even if their SSL certificate is invalid
        #         response = requests.get(url, headers=headers, timeout=10, verify=False)
        #         response.raise_for_status()

        #         # 3. Convert directly to Base64 to bypass Streamlit processing limits (like SVGs)
        #         content_type = response.headers.get("Content-Type", "image/png").split(";")[0]
        #         encoded_image = base64.b64encode(response.content).decode("utf-8")
                
        #         # 4. Build raw HTML to force the browser to render the raw data
        #         html_string = f"""
        #         <div style="display: flex; justify-content: center; align-items: center; width: 100%;">
        #             <img src="data:{content_type};base64,{encoded_image}" 
        #                 style="width: 100%; max-width: 100%; border-radius: 4px;" 
        #                 alt="Party Symbol" />
        #         </div>
        #         """
        #         return {"type": "html", "content": html_string}
                
        #     except Exception as e:
        #         # If the server is literally offline, fail gracefully to the default image
        #         return {"type": "local", "content": fallback_path}


        # # --- UI CODE ---
        # with st.container(border=False):
        #     logo_col, name_col, stats_col = st.columns([1, 3, 1], vertical_alignment="center")

        #     symbol_url = party_data['party_symbol'].unique()[0]
            
        #     # Process the URL through our bulletproof function
        #     fallback = (BASE_DIR / "independent.JPG")   # Place extension correctly (.jpg → .JPG) due to str()
        #     image_result = force_display_image(symbol_url, fallback)
            
        #     with logo_col:
        #         if image_result["type"] == "html":
        #             # Force render via HTML Base64 injection
        #             st.markdown(image_result["content"], unsafe_allow_html=True)
        #             # Add caption below the HTML image
        #             st.caption(f'Rank: #{current_party_rank}', text_alignment='center')
        #         else:
        #             # Standard fallback for the local independent image
        #             st.image(image_result["content"], caption=f'Rank: #{current_party_rank}', use_container_width=True)

        #     name_col.title(selected_party)

            # Display Party Wins and Vote Share
            total_wins = party_data[party_data['is_winner'] == True]['candidate'].count()
            vote_share = (party_data['votes'].sum() / total_party_votes) * 100
            
            stats_col.metric('WINS', total_wins)
            stats_col.metric('VOTE SHARE %', round(vote_share, 2))

        # --- TOP 10 CONSTITUENCIES FOR THE PARTY ---
        constituency_votes = party_data.groupby('constituency')['votes'].sum()
        top_10_party_constituencies = constituency_votes.nlargest(10).index
        
        party_bar_fig = px.bar(
            constituency_votes.rename(lambda x: x if x in top_10_party_constituencies else 'Others').groupby(level=0).mean().reset_index(name='votes').sort_values(by='votes', ascending=False),
            x='constituency',
            y='votes',
            labels={'votes': 'Avg Votes'},
            title=f'Top 10 Constituencies for {selected_party}',
        )
        st.plotly_chart(party_bar_fig, width='stretch')

        # --- CANDIDATES LIST FOR THE PARTY ---
        party_candidates = party_data.sort_values(by=['votes', 'is_winner'], ascending=[False, True])[['candidate', 'constituency', 'is_winner', 'votes']]
        party_candidates['rank'] = np.arange(len(party_candidates)) + 1
        st.dataframe(party_candidates.set_index('rank'))


# =========================================================
# PAGE 3: CANDIDATE-WISE ANALYSIS
# =========================================================
elif analysis_choice == 'Candidate-wise':
    st.header('Candidate-wise Analysis')
    
    sorted_candidates = sorted(election_data['candidate'].unique().tolist())
    selected_candidate = st.sidebar.selectbox('Select a Candidate', sorted_candidates)
    search_candidate_btn = st.sidebar.button('Find Candidate Details')

    if search_candidate_btn:
        # Filter data for the selected candidate
        candidate_data = election_data[election_data['candidate'] == selected_candidate]

        # Calculate overall candidate rank based on total votes
        candidate_rankings = election_data.groupby(['candidate_id', 'candidate'])['votes'].sum().reset_index()
        candidate_rankings['rank'] = candidate_rankings['votes'].rank(ascending=False).astype(int)
        current_candidate_rank = candidate_rankings[candidate_rankings['candidate'] == selected_candidate]['rank'].values[0]

        # Use standard Streamlit container for layout safety
        with st.container(border=True):
            photo_url = candidate_data['candidate_photo'].values[0]
            
            # --- CANDIDATE HEADER ---
            header_col1, header_col2 = st.columns([1, 3])
            
            header_col1.image(photo_url, caption=f'Rank: #{current_candidate_rank}', width=250)
            
            with header_col2:
                status_col, symbol_col = st.columns([3, 1], vertical_alignment='center')
                is_winner = candidate_data['is_winner'].values[0]
                constituency = candidate_data['constituency'].values[0]
                party_symbol = candidate_data['party_symbol'].values[0]
                
                # Show win/loss badge
                if is_winner:
                    status_col.success(constituency, icon='🏆', width=200)
                else:
                    status_col.error(constituency, width=200)

                # Show party symbol
                display_symbol = party_symbol if pd.notna(party_symbol) else 'independent.jpg'
                symbol_col.image(display_symbol, width=100)
                
                # Display Name and Party
                st.title(selected_candidate)
                party_name = candidate_data['party'].values[0]
                
                # Metrics Row
                party_label_col, vote_metric_col = st.columns([3, 1])
                party_label_col.subheader(f"({party_name})")
                
                # Calculate candidate's vote percentage inside their constituency
                total_constituency_votes = election_data[election_data['constituency'] == constituency]['votes'].sum()
                candidate_votes = candidate_data['votes'].values[0]
                vote_percentage = round((candidate_votes / total_constituency_votes) * 100, 2)
                
                vote_metric_col.metric(f"VOTES ({vote_percentage}%)", candidate_votes)

        # --- CANDIDATE DETAILS & RIVALS ---
        info_col, rivals_col = st.columns(2, vertical_alignment='bottom')
        
        with info_col:
            st.markdown("#### :gray[PERSONAL INFORMATION]")
            with st.container(border=True):
                gender_val = "Male" if candidate_data['gender'].values[0] == 'M' else "Female"
                
                st.write(f"***GENDER:** {gender_val}*")
                st.write(f"***FATHER:** {candidate_data['father'].values[0]}*")
                st.write(f"***SPOUSE:** {candidate_data['spouse'].values[0]}*")
                st.write(f"***ADDRESS:** {candidate_data['address'].values[0]}*")
                st.write(f"***EDUCATION:** {candidate_data['qualification'].values[0]}*")
                st.write(f"***EXPERIENCE:** {candidate_data['experience'].values[0]}*")

        with rivals_col:
            st.markdown("## :rainbow[TOP 5 RIVALS]")
            with st.container(border=True):
                # Find other candidates in the same constituency
                all_constituency_candidates = election_data[election_data['constituency'] == constituency][['candidate', 'party', 'votes']]
                
                # Filter out the selected candidate and get top 5 by votes
                rivals = all_constituency_candidates[all_constituency_candidates['candidate'] != selected_candidate]
                top_5_rivals = rivals.nlargest(5, 'votes').set_index('candidate')
                
                st.dataframe(top_5_rivals, width='stretch')