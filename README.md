# 🗳️ Election Result 2082 Analysis

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Data Analysis](https://img.shields.io/badge/Data%20Analysis-10ac84?style=for-the-badge)

A comprehensive data analytics project exploring candidate demographics, party performance, and voter turnout for the Nepal Election 2082 (2026). This project encompasses end-to-end data processing—from multi-source data extraction and cleaning to exploratory data analysis (EDA) and an interactive Streamlit dashboard.

## 📌 Project Objectives (Asking Questions)
The core objective of this project is to extract actionable insights from electoral data. The analysis focuses on the following key areas:
*   **Demographics:** Analyze candidate demographics and election outcomes.
*   **Party Performance:** Compare the performance of various political parties across the nation.
*   **Voter Behavior:** Examine voter turnout and abstention rates across different constituencies.
*   **Correlations:** Explore relationships between candidate characteristics (like age and education) and election results.
*   **Trends & Anomalies:** Identify statistical trends, correlations, and notable anomalies in the voting patterns.
*   **Visualization:** Present findings through interactive visualizations and a comprehensive dashboard.

---

## 🛠️ [Data Collection & Wrangling](https://github.com/Basnyat27/Election-Result-2082-Analysis/blob/main/2.%20data_wrangling/2.1%20data_gathering/second_way/data_collection.ipynb)
Gathering accurate and comprehensive data was a crucial first step, requiring data extraction from multiple sources and formats.

*   **JSON Data:** Retrieved candidates, parties, and constituencies-related data from `nepalvotes.live`.
*   **Web Scraping:** Extracted missing candidate ages, candidate photos, and party symbols directly from the official portal `result.election.gov.np`.
*   **AI Integration:** Leveraged ChatGPT to generate constituencies' geospatial coordinates in CSV format, which were subsequently validated for accuracy.

### [Assessing and Cleaning Data](https://github.com/Basnyat27/Election-Result-2082-Analysis/blob/main/2.%20data_wrangling/2.2%20data_assessing_and_cleaning/data_preparation_2nd_way.ipynb)
The raw datasets presented several structural and quality issues. These were addressed through multiple iterative cleaning steps to ensure robust and reliable data for analysis.

---

## 📊 [Exploratory Data Analysis (EDA) & Key Insights](https://github.com/Basnyat27/Election-Result-2082-Analysis/blob/main/3.%20eda/eda_on_election_data.ipynb)
Extensive univariate and bivariate analyses, alongside feature engineering, were conducted to draw meaningful conclusions. 

**Key Findings:**
1.  **Candidate Demographics:** 
    *   The age distribution of candidates shows a bell-curve trend peaking around the mid-40s to early 50s.
    *   There is a significant gender disparity, with **88.6% Male** candidates and only **11.4% Female** candidates.
2.  **Party Dominance:** 
    *   The **Rastriya Swatantra Party** emerged as the dominant force, securing the highest number of wins (125 seats) and a massive 75.8% share among the top winning parties, with an overall vote share of 44.33%.
3.  **Age vs. Votes:** 
    *   Winning candidates (plotted distinctly) span a wide age range, but the highest vote clusters predominantly belong to candidates aged 30 to 60.
4.  **Education vs. Electoral Success:** 
    *   Candidates with advanced degrees (Master's and Doctorate/Ph.D.) showed notable variance and strong average vote counts compared to other educational backgrounds.
5.  **Voter Abstention:** 
    *   Abstention rates varied significantly by constituency. Rukum East-1 recorded the highest abstention rate at **82.9%**, followed by Achham-1 (63.2%) and Achham-2 (63.1%).

---

## 📈 [Interactive Streamlit Dashboard](https://election-result-2082-analysis-rnxsmltzc97dqrpirtgu4m.streamlit.app/)
To make the data accessible and engaging, an interactive dashboard was developed using Streamlit. It offers three distinct analytical views:

### 1. Overall Analysis
*   **Geospatial Mapping:** Visualizes election results across Nepal's provinces.
*   **High-Level Metrics:** Displays total votes (10.55M+), overall turnout (55.9%), female candidate participation (11.4%), and youth individual percentage (31.0%).
*   **Aggregated Charts:** Features a pie chart for total vote share and bar charts for top constituencies by top parties.
*   **Leaderboards:** Showcases the top 20 winning candidates nationwide.

### 2. Party-wise Analysis
*   Detailed breakdown of individual political parties.
*   Displays the selected party's total wins, national vote share percentage, and a bar chart of its top 10 strongest constituencies.

### 3. Candidate-wise Analysis
*   A deep dive into specific candidates (e.g., Balendra Shah, Indira Rana Magar).
*   Displays the candidate's portrait, personal information (Status, Education, Address), party affiliation, and total votes secured.
*   Includes a localized "Top 5 Rivals" table comparing the candidate's performance against direct competitors in their constituency.

---

## ⚠️ Limitations
While this dataset provides valuable insights into candidate demographics and historical voting patterns, electoral outcomes are ultimately shaped by numerous external factors not captured here. 
Variables such as candidate popularity, social influence, voter relationships, and grassroots campaign strategies are missing. Therefore, this analysis relies on limited available indicators—such as candidate qualifications and residential background—which serve as indirect proxies for understanding broader electoral patterns.
