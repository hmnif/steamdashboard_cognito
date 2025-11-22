import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as colors
import os
import numpy as np

from plotly.subplots import make_subplots
from ipywidgets import interact

# Set page configuration
st.set_page_config(page_title="Steam Dashboard", layout="wide")

kpi_style = """
<style>
.kpi-box {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: -10px;
}
.kpi-label {
    font-size: 14px;
    color: #555;
}
.kpi-delta {
    font-size: 13px;
    color: #009900;
    margin-top: 4px;
}
.kpi-delta-neg {
    font-size: 13px;
    color: #cc0000;
    margin-top: 4px;
}
</style>
"""
st.markdown(kpi_style, unsafe_allow_html=True)

# Load data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CSV di folder data di root repo
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "steam.csv")
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"File CSV tidak ditemukan di path: {DATA_PATH}")
    st.stop()

# Preprocess data
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['release_year'] = df['release_date'].dt.year

# Sidebar filters
st.sidebar.header('Filter Data')
period_options = [
    'Semua (1997 - 2019)',
    '5 Tahun Terakhir (2014 - 2019)',
    '10 Tahun Terakhir (2009 - 2019)',
    '< Tahun 2009'
]

time_period = st.sidebar.selectbox(
    'Periode Waktu:',
    period_options,
    index=0   # default
)

# Filter utama berdasarkan time_period
if time_period == 'Semua (1997 - 2019)':
    df_current = df
    df_prev = None
elif time_period == '5 Tahun Terakhir (2014 - 2019)':
    df_current = df[df['release_year'] >= 2014]
    df_prev = df[(df['release_year'] >= 2009) & (df['release_year'] <= 2013)]
elif time_period == '10 Tahun Terakhir (2009 - 2019)':
    df_current = df[df['release_year'] >= 2009]
    df_prev = df[(df['release_year'] >= 1999) & (df['release_year'] <= 2008)]
elif time_period == '< Tahun 2009':
    df_current = df[df['release_year'] < 2009]
    df_prev = None  

# Title and description
st.title('Dashboard Tren Game Steam 🎮')
st.markdown("""
Dibuat oleh **Cognito Team.**
""")

#KPI Cards
total_games = df_current.shape[0]
total_publishers = df_current['publisher'].nunique()
most_common_genre = df_current['genres'].dropna().mode()[0]
avg_price_current = df_current['price'].mean()

#Logical Delta Absence for Time Period
if df_prev is not None and len(df_prev) > 0:
    total_games_prev = df_prev.shape[0]
    delta_games = total_games - total_games_prev
    #Price
    avg_price_prev = df_prev['price'].mean()
    delta_price_abs = avg_price_current - avg_price_prev
    delta_price_pct = (delta_price_abs / avg_price_prev) * 100
else:
    delta_games = None
    delta_price_abs = None
    delta_price_pct = None

col1, col2, col3, col4 = st.columns(4)
with col1:
    if delta_games is not None:
        kelas_delta = "kpi-delta" if delta_games >= 0 else "kpi-delta-neg"
        nilai_delta = delta_games
    else:
        kelas_delta = "kpi-delta"
        nilai_delta = "–"

    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Total Games</div>
            <div class="kpi-value">{total_games:,}</div>
            <div class="{kelas_delta}">
                {nilai_delta}
            </div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Total Publisher</div>
            <div class="kpi-value">{total_publishers}</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Genre Terpopuler</div>
            <div class="kpi-value">{most_common_genre}</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    if delta_price_abs is not None:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Harga Rata-rata</div>
                <div class="kpi-value">£{avg_price_current:.2f}</div>
                <div class="{ 'kpi-delta' if delta_price_abs >= 0 else 'kpi-delta-neg' }">
                    {delta_price_abs:+.2f} GBP ({delta_price_pct:+.1f}%)
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Harga Rata-rata</div>
                <div class="kpi-value">£{avg_price_current:.2f}</div>
                <div class="kpi-delta">–</div>
            </div>
        """, unsafe_allow_html=True)

#Trend Game of Release per Year
st.subheader("Tren Perilisan Game per Tahun")
games_per_year = df_current.groupby('release_year').size().reset_index(name='count')
fig1 = px.line(
    games_per_year,
    x='release_year',
    y='count',
    markers=True,
    labels={'release_year': 'Tahun Rilis', 'count': 'Jumlah Game'},
    title=None,
    line_shape='spline'
)
fig1.update_traces(line_color='royalblue', line_width=3)
fig1.update_layout(
    template='plotly_white',
    title=None,
    title_x=0.5,
    title_font=dict(size=20, family='Arial', color='black'),
    xaxis=dict(tickmode='linear', tick0=1990, dtick=2),
    yaxis_title='Jumlah Game Dirilis',
    hovermode='x unified'
)
st.plotly_chart(fig1, use_container_width=True)

# Top 5 Games by Reviews and 5 Genres Distribution
col1, col2 = st.columns(2)
with col1:
    st.subheader("5 Game Teratas berdasarkan Review")
    top5_games = df_current.nlargest(5, 'positive_ratings')[['name', 'positive_ratings', 'negative_ratings']]
    top5_games_melted = top5_games.melt(id_vars='name', value_vars=['positive_ratings', 'negative_ratings'],
                                        var_name='review_type', value_name='count')
    fig2 = px.bar(
        top5_games_melted,
        x='name',
        y='count',
        color='review_type',
        barmode='group',
        labels={'name': 'Nama Game', 'count': 'Jumlah Review', 'review_type': 'Tipe Review'},
        color_discrete_map={'positive_ratings': 'green', 'negative_ratings': 'red'}
    )
    fig2.update_layout(
        template='plotly_white',
        title=None,
        title_x=0.5,
        xaxis_title='Nama Game',
        yaxis_title='Jumlah Review',
        hovermode='x unified'
    )
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.subheader("Distribusi 5 Genre Teratas")
    top5_genres = df_current['genres'].value_counts().nlargest(5).reset_index()
    top5_genres.columns = ['genre', 'count']
    fig3 = px.bar(
        top5_genres,
        x='genre',
        y='count',
        labels={'genre': 'Genre', 'count': 'Jumlah Game'},
        title=None,
        color='genre',
        color_discrete_map={
            top5_genres['genre'][0]: colors.qualitative.Plotly[0],
            top5_genres['genre'][1]: colors.qualitative.Plotly[1],
            top5_genres['genre'][2]: colors.qualitative.Plotly[2],
            top5_genres['genre'][3]: colors.qualitative.Plotly[3],
            top5_genres['genre'][4]: colors.qualitative.Plotly[4],
        }
    )
    fig3.update_layout(
        template='plotly_white',
        title=None,
        title_x=0.5,
        xaxis_title='Genre',
        yaxis_title='Jumlah Game',
        hovermode='x unified'
    )
    st.plotly_chart(fig3, use_container_width=True)

# Top 5 Publishers by Average Positive Reviews and Price Distribution (Free vs Paid)
col1, col2 = st.columns(2)
with col1:
    st.subheader("5 Publisher Teratas berdasarkan Rata-rata Review Positif")
    avg_positive_reviews = df_current.groupby('publisher')['positive_ratings'].mean().reset_index()
    top5_publishers = avg_positive_reviews.nlargest(5, 'positive_ratings')
    fig4 = px.bar(
        top5_publishers,
        x='publisher',
        y='positive_ratings',
        labels={'publisher': 'Publisher', 'positive_ratings': 'Rata-rata Review Positif'},
        title=None,
        color='publisher',
        color_discrete_sequence=colors.qualitative.Plotly
    )
    fig4.update_layout(
        template='plotly_white',
        title=None,
        title_x=0.5,
        xaxis_title='Publisher',
        yaxis_title='Rata-rata Review Positif',
        hovermode='x unified'
    )
    st.plotly_chart(fig4, use_container_width=True)
with col2:
    st.subheader("Distribusi Harga Game (Gratis vs Berbayar)")
    df_current['price_category'] = np.where(df_current['price'] == 0, 'Gratis', 'Berbayar')
    price_distribution = df_current['price_category'].value_counts().reset_index()
    price_distribution.columns = ['price_category', 'count']
    fig5 = px.pie(
        price_distribution,
        names='price_category',
        values='count',
        color='price_category',
        color_discrete_map={'Gratis': 'lightgreen', 'Berbayar': 'lightblue'},
        title=None
    )
    fig5.update_layout(
        template='plotly_white',
        title=None,
        title_x=0.5,
        hovermode='x unified'
    )
    st.plotly_chart(fig5, use_container_width=True)

# Corelation Ratio Positive Reviews vs Price Game with Filter Genre
st.subheader("Korelasi Antara Review Positif dan Harga Game")
positive_ratio = df_current['positive_ratings'] / (df_current['positive_ratings'] + df_current['negative_ratings'])
df_current['positive_ratio'] = positive_ratio
genre_options = ['Semua'] + sorted(df_current['genres'].dropna().unique().tolist())
selected_genre = st.selectbox('Pilih Genre:', genre_options, index=0)

if selected_genre != 'Semua':
    df_current = df_current[df_current['genres'].str.contains(selected_genre)]

fig6 = px.scatter(
    df_current,
    x='positive_ratio',
    y='price',
    hover_data=['name', 'publisher', 'genres'],
    labels={
        'positive_ratio': 'Rasio Review Positif',
        'price': 'Harga Game (GBP)'
    },
    title=None,
    trendline='ols'
)

fig6.update_layout(
    template='plotly_white',
    title=None,
    title_x=0.5,
    xaxis_title='Rasio Review Positif',
    yaxis_title='Harga Game (GBP)',
    hovermode='x unified'
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

#Corelation Owner (Players) vs Median Playtime with Filter Genre
st.subheader("Korelasi Antara Owner dan Median Playtime Game")
def convert_owner_range(x):
    x = str(x).replace(',', '').replace('+', '')
    if '-' in x:
        a, b = x.split('-')
        return (float(a) + float(b)) / 2
    return float(x)

df_current['owners'] = df_current['owners'].apply(convert_owner_range)
owner_mean = df_current['owners'].mean()
df_current['owners'] = df_current['owners'].fillna(owner_mean)
df_current = df_current.dropna(subset=['owners','median_playtime','genres'])

fig7 = px.scatter(
    df_current,
    x='owners',
    y='median_playtime',
    hover_data=['name', 'publisher', 'genres'],
    labels={
        'owners': 'Jumlah Owner',
        'median_playtime': 'Median Playtime'
    },
    title=None,
    trendline='ols'
)

fig7.update_layout(
    template='plotly_white',
    title=None,
    title_x=0.5,
    xaxis_title='Jumlah Owner',
    yaxis_title='Median Playtime',
    hovermode='x unified'
)

st.plotly_chart(
    fig7,
    use_container_width=True
)