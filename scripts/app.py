import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as colors
import os
import numpy as np

from plotly.subplots import make_subplots
# from ai.insight_engine import insight_distributiongame

# Set page configuration
st.set_page_config(page_title="Steam Dashboard", layout="wide")

# CSS Style
kpi_style = """
<style>
.title {
    font-size: 36px;
    font-weight: 700;
    color: #262730;
}
.kpi-box {
    background: #F0F2F6;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border-left: 4px solid #0068C9;
    min-height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: -10px;
    color: #0068C9;
}
.kpi-label {
    font-size: 16px;
    color: #262730;
}
.kpi-delta {
    text: None;
}
.kpi-delta-pos {
    display: inline-block;
    font-size: 14px;
    color: #37C900;
    # background-color: #02FF20;
}
.kpi-delta-neg {
    font-size: 14px;
    color: #C90000;
    # background-color: #FF4B4B;
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
df['genres'] = df['genres'].fillna('Unknown').str.split(';')
df['genres'] = df['genres'].apply(
    lambda x: [g.strip() for g in x if g.strip().lower() != 'indie']
)
df_exploded = df.explode('genres')
df_exploded = df_exploded[df_exploded['genres'].notna() & (df_exploded['genres'] != "")]

# Sidebar filters
st.sidebar.header('Filter Data')
period_options = [
    'Semua',
    '5 Tahun Terakhir',
    '2010s (2010 - 2019)',
    '2000s (2000 - 2009)'
]

time_period = st.sidebar.selectbox(
    'Periode Waktu:',
    period_options,
    index=0   # default
)

# Filter utama berdasarkan time_period
if time_period == 'Semua':
    df_current = df
    df_prev = None
elif time_period == '5 Tahun Terakhir':
    df_current = df[df['release_year'] >= 2014]
    df_prev = df[(df['release_year'] <= 2013)]
elif time_period == '2010s (2010 - 2019)':
    df_current = df[(df['release_year'] >= 2010) & (df['release_year'] <= 2019)]
    df_prev = df[(df['release_year'] >= 2000) & (df['release_year'] <= 2009)]
elif time_period == '2000s (2000 - 2009)':
    df_current = df[(df['release_year'] <= 2009)]
    df_prev = df[df['release_year'] < 2000]

# Title and description
st.markdown("""
    <h1 class="title">
        Dahsboard Tren Game Steam🎮
    </h1>
""", unsafe_allow_html=True)

st.markdown("""
Dibuat oleh **Cognito Team.**
""")

st.markdown("---")

#KPI Cards
total_games = df_current.shape[0]
total_publishers = df_current['publisher'].nunique()
if df_exploded.empty:
    most_common_genre = "Unknown"
else:
    most_common_genre = df_exploded['genres'].mode()[0]

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
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Total Games</div>
                <div class="kpi-value">
                    {total_games:,}
                    <span class="{ 'kpi-delta-pos' if delta_games >= 0 else 'kpi-delta-neg' }">
                        {delta_games:+,}
                    </span>
                </div>
                <div style="color: #3B3B3B; margin-top: 4px; font-size: 14px">Periode Sebelumnya</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Total Games</div>
                <div class="kpi-value">{total_games:,}</div>
                <div class="kpi-delta"></div>
            </div>
        """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Total Publisher</div>
            <div class="kpi-value">{total_publishers:,}</div>
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
                <div class="kpi-value">
                    £{avg_price_current:.2f}
                    <span class="{ 'kpi-delta-neg' if delta_price_abs >= 0 else 'kpi-delta-pos' }">
                    {delta_price_abs:+.2f}£ ({delta_price_pct:+.1f}%)
                    </span>
                </div>
                <div style="color: #3B3B3B; margin-top: 4px; font-size: 14px">Periode Sebelumnya</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">Harga Rata-rata</div>
                <div class="kpi-value">£{avg_price_current:.2f}</div>
                <div class="kpi-delta"></div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

#Trend Game of Release per Year
st.subheader("Tren Perilisan Game per Tahun")
games_per_year = df_current.groupby('release_year').size().reset_index(name='count')
fig1 = px.line(
    games_per_year,
    x='release_year',
    y='count',
    markers=True,
    color_discrete_map={'count': '#0068C9'},
    labels={'release_year': 'Tahun Rilis', 'count': 'Jumlah Game'},
    line_shape='spline'
)
fig1.update_traces(line_color='royalblue', line_width=3)
fig1.update_layout(
    template='plotly_white',
    xaxis=dict(tickmode='linear', tick0=1990, dtick=2),
    yaxis_title='Jumlah Game Dirilis',
    hovermode='x unified'
)
st.plotly_chart(fig1, use_container_width=True)

# Top 5 Games by Reviews and 5 Genres Distribution
col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 5 Game Terpopuler")
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
        color_discrete_map={'positive_ratings': '#0068C9', 'negative_ratings': '#64B5F6'}
    )
    fig2.update_layout(
        template='plotly_white',
        xaxis_title='Nama Game',
        yaxis_title='Jumlah Review',
        hovermode='x unified'
    )
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.subheader("Top 5 Genre Tepopuler")
    df_genre = df_current.copy()
    df_genre = df_genre.explode('genres')

    df_genre = df_genre[
        df_genre['genres'].notna() & 
        (df_genre['genres'] != "") &
        (df_genre['genres'].str.lower() != "indie")
    ]

    top5_genres = (
        df_genre['genres']
        .value_counts()
        .nlargest(5)
        .reset_index()
    )
    top5_genres.columns = ['genre', 'count']
    fig3 = px.bar(
        top5_genres,
        x='genre',
        y='count',
        labels={'genre': 'Genre', 'count': 'Jumlah Game'},
        color='genre',
        color_discrete_map={
            top5_genres['genre'][0]: '#0068C9',
            top5_genres['genre'][1]: '#3286d3',
            top5_genres['genre'][2]: '#66a4de',
            top5_genres['genre'][3]: '#99c2e9',
            top5_genres['genre'][4]: '#e5eff9',
        }
    )
    fig3.update_layout(
        template='plotly_white',
        xaxis_title='Genre',
        yaxis_title='Jumlah Game',
        hovermode='x unified'
    )
    st.plotly_chart(fig3, use_container_width=True)

# Top 5 Publishers by Average Positive Reviews and Price Distribution (Free vs Paid)
col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 5 Publisher Teratas")
    avg_positive_reviews = (df_current.groupby('publisher')['positive_ratings'].mean().reset_index())
    top5_publishers = (avg_positive_reviews.nlargest(5, 'positive_ratings').reset_index(drop=True))
    fig4 = px.bar(
        top5_publishers,
        x='publisher',
        y='positive_ratings',
        labels={'publisher': 'Publisher', 'positive_ratings': 'Rata-rata Review Positif'},
        color='publisher',
        # color_discrete_sequence=colors.qualitative.Plotly
        color_discrete_map={
            top5_publishers['publisher'][0]: '#0068C9',
            top5_publishers['publisher'][1]: '#3286d3',
            top5_publishers['publisher'][2]: '#66a4de',
            top5_publishers['publisher'][3]: '#99c2e9',
            top5_publishers['publisher'][4]: '#e5eff9',
        }
    )
    fig4.update_layout(
        template='plotly_white',
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
        color_discrete_map={'Gratis': '#64B5F6', 'Berbayar': '#0068C9'},
    )
    fig5.update_traces(
        pull=[0 if cat == 'Gratis' else 0.1 for cat in price_distribution['price_category']]
    )
    fig5.update_layout(
        template='plotly_white',
        hovermode='x unified'
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Insight Dropdown for Price Distribution
    # with st.expander("💡 Insight"):
    #     total_gratis = price_distribution.loc[
    #         price_distribution['price_category'] == 'Gratis', 'count'
    #     ].sum()

    #     total_berbayar = price_distribution.loc[
    #         price_distribution['price_category'] == 'Berbayar', 'count'
    #     ].sum()

    #     st.markdown(f"""
    #         <div style="font-size:16px; line-height:2;">
    #             <div>Game Gratis: <b>{total_gratis:,}</b></div>
    #             <div>Game Berbayar: <b>{total_berbayar:,}</b></div>
    #         </div>
    #         <div>
    #             Recommendation by <b>AI ✨</b>:
    #             <div>{insight_distributiongame(total_gratis, total_berbayar)}</div>
    #         </div>
    #     """, unsafe_allow_html=True)

st.markdown("---")

# Corelation Ratio Positive Reviews vs Price Game with Filter Genre
# st.subheader("Korelasi Antara Review Positif dan Harga Game")
# df_pos = df_current.copy()
# df_pos['positive_ratio'] = df_pos['positive_ratings'] / (
#     df_pos['positive_ratings'] + df_pos['negative_ratings']
# )

# df_pos = df_pos.explode('genres')
# df_pos['genres'] = df_pos['genres'].fillna("Unknown")
# df_pos = df_pos[df_pos['genres'].str.lower() != "indie"]
# df_pos = df_pos[df_pos['price'] <= 100]
# col1, col2, col3, col4 = st.columns(4)
# with col4:
#     df_pos['genres'] = df_pos['genres'].astype(str)
#     genre_options_pos = ['Semua'] + sorted(df_pos['genres'].unique().tolist())
#     selected_genre_pos = st.selectbox(
#         'Pilih Genre:',
#         genre_options_pos,
#         index=0
#     )
# if selected_genre_pos != 'Semua':
#     df_pos = df_pos[df_pos['genres'] == selected_genre_pos]

# fig6 = px.scatter(
#     df_pos,
#     x='positive_ratio',
#     y='price',
#     color='price',
#     color_continuous_scale=[
#         [0.00, "#0077ff"],
#         [0.10, "#00baff"],
#         [0.20, "#fee08b"],
#         [0.50, "#f46d43"],
#         [1.00, "#C90000"]
#     ],
#     hover_data=['name', 'publisher', 'genres'],
#     labels={
#         'positive_ratio': 'Rasio Review Positif',
#         'price': 'Harga Game (£)'
#     },
#     title=None
# )
# fig6.update_traces(
#     marker=dict(size=8, opacity=0.75, line=dict(width=0.4, color='DarkSlateGrey')),
#     hovertemplate=(
#         'Persentase Ulasan Positif=%{x:.0%}<br>'
#         'Harga Game (£)=%{y}<br>'
#         'Nama=%{customdata[0]}<br>'
#         'Developer=%{customdata[1]}<br>'
#         'Publisher=%{customdata[2]}<br>'
#         'Genre=%{customdata[3]}<extra></extra>'
#     )
# )
# fig6.update_layout(
#     template='plotly_white',
#     xaxis_title='Rasio Review Positif',
#     yaxis_title='Harga Game (£)',
# )
# st.plotly_chart(fig6, use_container_width=True)

# st.markdown("---")

# Density Game by Ratio Positive Reviews and Price Game with Filter Price Category
st.subheader("Distribusi Game Berdasarkan Rasio Review Positif dan Harga Game")
df_density = df_current.copy()
df_density['positive_ratio'] = df_density['positive_ratings'] / (
    df_density['positive_ratings'] + df_density['negative_ratings']
)

col1, col2, col3, col4 = st.columns(4)
with col4:
    price_category_options = ['Semua', 'Gratis', 'Murah (0-£10)', 'Sedang (£10-£30)', 'Mahal (£30-£100)', 'Premium (£100+)']
    selected_price_category = st.selectbox(
        'Pilih Kategori Harga:',
        price_category_options,
        index=0
    )
if selected_price_category == 'Gratis':
    df_density = df_density[df_density['price'] == 0]
elif selected_price_category == 'Murah (0-£10)':
    df_density = df_density[(df_density['price'] > 0) & (df_density['price'] <= 10)]
elif selected_price_category == 'Sedang (£10-£30)':
    df_density = df_density[(df_density['price'] > 10) & (df_density['price'] <= 30)]
elif selected_price_category == 'Mahal (£30-£100)':
    df_density = df_density[(df_density['price'] > 30) & (df_density['price'] <= 100)]
elif selected_price_category == 'Premium (£100+)':
    df_density = df_density[df_density['price'] > 100]

fig7 = px.density_heatmap(
    df_density,
    x='positive_ratio',
    y='price',
    nbinsx=40,
    nbinsy=40,
    color_continuous_scale='Blues',
    labels={
        'positive_ratio': 'Persentase Ulasan Positif',
        'price': 'Harga (£)'
    },
    width=1100,
    height=650
)
fig7.update_layout(
    template='plotly_white',
    xaxis_title='Persentase Ulasan Positif',
    yaxis_title='Harga (£)',
    
)
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

#Corelation Owner (Players) vs Median Playtime with Filter Genre
# st.subheader("Korelasi Antara Owner dan Median Playtime Game")
# df_owner = df_current.copy()
# def convert_owner_range(x):
#     x = str(x).replace(',', '').replace('+', '')
#     if '-' in x:
#         a, b = x.split('-')
#         return (float(a) + float(b)) / 2
#     return float(x)

# df_owner['owners'] = df_owner['owners'].apply(convert_owner_range)
# df_owner['owners'] = df_owner['owners'].fillna(df_owner['owners'].mean())

# df_owner['genres'] = (
#     df_owner['genres']
#     .fillna('Unknown')
#     .apply(lambda x: x.split(';') if isinstance(x, str) else x)
# )

# df_owner['genres'] = df_owner['genres'].apply(
#     lambda x: [g.strip() for g in x] if isinstance(x, list) else ['Unknown']
# )

# df_owner = df_owner.explode('genres')
# df_owner = df_owner[df_owner['genres'].str.lower() != 'indie']
# df_owner['genres'] = df_owner['genres'].replace('', 'Unknown')

# col1, col2, col3, col4 = st.columns(4)
# with col4:
#     df_owner['genres'] = df_owner['genres'].astype(str)
#     genre_options_owner = ['Semua'] + sorted(df_owner['genres'].unique().tolist())
#     selected_genre_owner = st.selectbox('Pilih Genre:', genre_options_owner, index=0)

# if selected_genre_owner != 'Semua':
#     df_owner = df_owner[df_owner['genres'] == selected_genre_owner]

# df_owner = df_owner.dropna(subset=['owners', 'median_playtime'])

# fig7 = px.scatter(
#     df_owner,
#     x='owners',
#     y='median_playtime',
#     hover_data=['name', 'publisher', 'genres'],
#     labels={
#         'owners': 'Jumlah Owner',
#         'median_playtime': 'Median Playtime (menit)'
#     },
#     color_discrete_sequence=colors.qualitative.Plotly
# )

# fig7.update_layout(
#     template='plotly_white',
#     xaxis_title='Jumlah Owner',
#     yaxis_title='Median Playtime (menit)',
#     hovermode='x unified'
# )

# st.plotly_chart(fig7, use_container_width=True)

# st.markdown("---")

#Corelation Owner (Players) vs Median Playtime with Filter Genre use Hexbin Plot
# st.subheader("Korelasi Antara Owner dan Median Playtime Game")
# df_owner = df_current.copy()
# def convert_owner_range(x):
#     x = str(x).replace(',', '').replace('+', '')
#     if '-' in x:
#         a, b = x.split('-')
#         return (float(a) + float(b)) / 2
#     return float(x)

# df_owner['owners'] = df_owner['owners'].apply(convert_owner_range)
# df_owner['owners'] = df_owner['owners'].fillna(df_owner['owners'].mean())

# df_owner['genres'] = (
#     df_owner['genres']
#     .fillna('Unknown')
#     .apply(lambda x: x.split(';') if isinstance(x, str) else x)
# )

# df_owner['genres'] = df_owner['genres'].apply(
#     lambda x: [g.strip() for g in x] if isinstance(x, list) else ['Unknown']
# )

# df_owner = df_owner.explode('genres')
# df_owner = df_owner[df_owner['genres'].str.lower() != 'indie']
# df_owner['genres'] = df_owner['genres'].replace('', 'Unknown')

# col1, col2, col3, col4 = st.columns(4)
# with col4:
#     df_owner['genres'] = df_owner['genres'].astype(str)
#     genre_options_owner = ['Semua'] + sorted(df_owner['genres'].unique().tolist())
#     selected_genre_owner = st.selectbox('Pilih Genre:', genre_options_owner, index=0)

# if selected_genre_owner != 'Semua':
#     df_owner = df_owner[df_owner['genres'] == selected_genre_owner]
# df_owner = df_owner.dropna(subset=['owners', 'median_playtime'])

# genres = sorted(df_owner['genres'].unique())
# genre_map = {g: i * 360 / len(genres) for i, g in enumerate(genres)}
# df_owner['theta'] = df_owner['genres'].map(genre_map)

# df_owner['owners_scaled'] = df_owner['owners']

# df_owner['marker_size'] = (df_owner['median_playtime'] / 60).clip(5, 20)

# fig7 = go.Figure()

# fig7.add_trace(go.Scatterpolar(
#     r=df_owner['owners_scaled'],
#     theta=df_owner['theta'],
#     mode='markers',
#     marker=dict(
#         size=df_owner['marker_size'],
#         color=df_owner['owners_scaled'],
#         colorscale='Blues',
#         showscale=True,
#         colorbar=dict(title='Jumlah Owner')
#     ),
#     hovertemplate=(
#         "<b>%{text}</b><br>"
#         "Genre: %{customdata[1]}<br>"
#         "Jumlah Owner: %{r}<br>"
#         "Median Playtime: %{marker.size} menit<br>"
#         "Publisher: %{customdata[0]}<extra></extra>"
#     ),
#     text=df_owner['name'],
#     customdata=df_owner[['publisher', 'genres']]
# ))

# fig7.update_layout(
#     template='plotly_white',
#     polar=dict(
#         radialaxis=dict(title='Jumlah Owner (log scale)', type='log'),
#         angularaxis=dict(
#             tickmode='array',
#             tickvals=list(genre_map.values()),
#             ticktext=list(genre_map.keys())
#         )
#     ),
#     showlegend=False
# )

# st.plotly_chart(fig7, use_container_width=True)

#Corelation Owner (Players) vs Average Playtime with Filter Genre use Scatter Polar Plot
st.subheader("Korelasi Antara Owner dan Rata-rata Playtime Game")
df_owner = df_current.copy()
def convert_owner_range(x):
    x = str(x).replace(',', '').replace('+', '')
    if '-' in x:
        a, b = x.split('-')
        return (float(a) + float(b)) / 2
    return float(x)

df_owner['owners'] = df_owner['owners'].apply(convert_owner_range)
df_owner['owners'] = df_owner['owners'].fillna(df_owner['owners'].mean())

df_owner['genres'] = (
    df_owner['genres']
    .fillna('Unknown')
    .apply(lambda x: x.split(';') if isinstance(x, str) else x)
)
df_owner['genres'] = df_owner['genres'].apply(
    lambda x: [g.strip() for g in x] if isinstance(x, list) else ['Unknown']
)

df_owner = df_owner.explode('genres')
df_owner = df_owner[df_owner['genres'].str.lower() != 'indie']
df_owner['genres'] = df_owner['genres'].replace('', 'Unknown')

col1, col2, col3, col4 = st.columns(4)
with col4:
    df_owner['genres'] = df_owner['genres'].astype(str)
    genre_options_owner = ['Semua'] + sorted(df_owner['genres'].unique().tolist())
    selected_genre_owner = st.selectbox('Pilih Genre:', genre_options_owner, index=0)

if selected_genre_owner != 'Semua':
    df_owner = df_owner[df_owner['genres'] == selected_genre_owner]
df_owner = df_owner.dropna(subset=['owners', 'average_playtime'])

genres = sorted(df_owner['genres'].unique())
genre_map = {g: i * 360 / len(genres) for i, g in enumerate(genres)}
df_owner['theta'] = df_owner['genres'].map(genre_map)

df_owner['owners_scaled'] = df_owner['owners']

df_owner['marker_size'] = (df_owner['average_playtime'] / 60).clip(5, 20)

fig8 = go.Figure()

fig8.add_trace(go.Scatterpolar(
    r=df_owner['owners_scaled'],
    theta=df_owner['theta'],
    mode='markers',
    marker=dict(
        size=df_owner['marker_size'],
        color=df_owner['owners_scaled'],
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title='Jumlah Owner')
    ),
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Genre: %{customdata[1]}<br>"
        "Jumlah Owner: %{r}<br>"
        "Rata-rata Playtime: %{marker.size} menit<br>"
        "Publisher: %{customdata[0]}<extra></extra>"
    ),
    text=df_owner['name'],
    customdata=df_owner[['publisher', 'genres']]
))
fig8.update_layout(
    template='plotly_dark',
    polar=dict(
        radialaxis=dict(title='Jumlah Owner (log scale)', type='log'),
        angularaxis=dict(
            tickmode='array',
            tickvals=list(genre_map.values()),
            ticktext=list(genre_map.keys())
        )
    ),
    showlegend=False
)

st.plotly_chart(fig8, use_container_width=True)