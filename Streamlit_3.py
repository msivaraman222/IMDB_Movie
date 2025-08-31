import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('Final_movies.csv')
    return df

df = load_data()

# Set up the page
st.set_page_config(page_title="IMDB MOVIES", page_icon="🎬", layout="wide")
st.title("🎬 IMDB MOVIES")
st.markdown("Explore and filter movies based on various criteria")

# Sidebar for filters
st.sidebar.header("Filter Movies")

# Multi-select genre filter
genres = sorted(df['Genre'].unique())
selected_genres = st.sidebar.multiselect(
    "Select Genre(s):",
    options=genres,
    default=[],
    help="Select one or more genres to filter by"
)

# Duration filter with predefined ranges
st.sidebar.subheader("Duration Ranges")
duration_options = {
    "All Durations": (0.0, float(df['Duration'].max())),
    "Short (< 2 hrs)": (0.0, 2.0),
    "Medium (2-3 hrs)": (2.0, 3.0),
    "Long (> 3 hrs)": (3.0, float(df['Duration'].max()))
}

selected_duration = st.sidebar.radio(
    "Select duration range:",
    options=list(duration_options.keys()),
    help="Filter movies by their runtime"
)

min_duration, max_duration = duration_options[selected_duration]

# Custom duration slider for more precise control
st.sidebar.markdown("**Or specify custom range:**")
custom_min, custom_max = st.sidebar.slider(
    "Custom duration range (hours):",
    min_value=0.0,
    max_value=float(df['Duration'].max()),
    value=(float(min_duration), float(max_duration)),  # Ensure both values are floats
    step=0.1,
    help="Filter movies by their runtime in hours"
)

# Use custom values if different from predefined
if custom_min != min_duration or custom_max != max_duration:
    min_duration, max_duration = float(custom_min), float(custom_max)

# Rating filter
st.sidebar.subheader("Minimum Rating")
rating_options = {
    "Any Rating": 0.0,
    "Good (6.0+)": 6.0,
    "Very Good (7.0+)": 7.0,
    "Excellent (8.0+)": 8.0,
    "Outstanding (9.0+)": 9.0
}

selected_rating = st.sidebar.radio(
    "Select minimum rating:",
    options=list(rating_options.keys()),
    help="Filter movies with rating equal to or above this value"
)

min_rating = rating_options[selected_rating]

# Custom rating slider for more precise control
st.sidebar.markdown("**Or specify custom rating:**")
custom_rating = st.sidebar.slider(
    "Custom minimum rating:",
    min_value=0.0,
    max_value=10.0,
    value=float(min_rating),  # Ensure it's a float
    step=0.1,
    help="Filter movies with rating equal to or above this value"
)

# Use custom value if different from predefined
if custom_rating != min_rating:
    min_rating = float(custom_rating)

# Votes filter
st.sidebar.subheader("Minimum Votes")
vote_options = {
    "Any number of votes": 0,
    "Popular (1K+ votes)": 1000,
    "Very Popular (10K+ votes)": 10000,
    "Blockbuster (50K+ votes)": 50000,
    "Super Hit (100K+ votes)": 100000
}

selected_votes = st.sidebar.radio(
    "Select minimum votes:",
    options=list(vote_options.keys()),
    help="Filter movies with at least this many votes"
)

min_votes = vote_options[selected_votes]

# Custom votes slider for more precise control
st.sidebar.markdown("**Or specify custom minimum votes:**")
custom_votes = st.sidebar.slider(
    "Custom minimum votes:",
    min_value=0,
    max_value=int(df['Votes'].max()),
    value=int(min_votes),  # Ensure it's an int
    step=1000,
    help="Filter movies with at least this many votes"
)

# Use custom value if different from predefined
if custom_votes != min_votes:
    min_votes = int(custom_votes)

# Apply filters
filtered_df = df.copy()

if selected_genres:
    filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genres)]

filtered_df = filtered_df[
    (filtered_df['Duration'] >= min_duration) & 
    (filtered_df['Duration'] <= max_duration) &
    (filtered_df['Rating'] >= min_rating) &
    (filtered_df['Votes'] >= min_votes)
]

# Display results
st.subheader(f"Filtered Movies ({len(filtered_df)} found)")

if len(filtered_df) == 0:
    st.warning("No movies match your filters. Try adjusting your criteria.")
else:
    # Show some metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Movies", len(filtered_df))
    col2.metric("Average Rating", f"{filtered_df['Rating'].mean():.2f}")
    col3.metric("Average Duration", f"{filtered_df['Duration'].mean():.2f} hrs")
    col4.metric("Average Votes", f"{filtered_df['Votes'].mean():.0f}")

    # Display the filtered dataframe
    st.dataframe(
        filtered_df,
        column_config={
            "Title": "Movie Title",
            "Rating": st.column_config.NumberColumn(
                "Rating",
                format="%.1f ⭐",
            ),
            "Votes": st.column_config.NumberColumn(
                "Votes",
                format="%d 👥",
            ),
            "Duration": st.column_config.NumberColumn(
                "Duration (hrs)",
                format="%.2f hours",
            ),
            "Genre": "Genre"
        },
        hide_index=True,
        use_container_width=True
    )

    # Add some visualizations
    st.subheader("Data Visualizations")

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Rating Distribution", "Duration vs Rating", "Top Movies by Votes"])

    with tab1:
        fig = px.histogram(filtered_df, x='Rating', title='Distribution of Movie Ratings')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.scatter(
            filtered_df, 
            x='Duration', 
            y='Rating', 
            color='Genre' if selected_genres and len(selected_genres) > 1 else None,
            hover_data=['Title'],
            title='Duration vs Rating'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        # Display top 10 movies by votes
        top_movies = filtered_df.nlargest(10, 'Votes')[['Title', 'Rating', 'Votes', 'Duration', 'Genre']]
        fig = px.bar(
            top_movies, 
            x='Title', 
            y='Votes',
            color='Rating',
            hover_data=['Duration', 'Genre'],
            title='Top 10 Movies by Number of Votes'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Add download button
    st.download_button(
        label="Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_movies.csv",
        mime="text/csv",
    )

# Display current filter settings
with st.expander("Current Filter Settings"):
    st.write(f"**Genres:** {', '.join(selected_genres) if selected_genres else 'All'}")
    st.write(f"**Duration:** {min_duration:.2f} to {max_duration:.2f} hours")
    st.write(f"**Minimum Rating:** {min_rating:.1f}")
    st.write(f"**Minimum Votes:** {min_votes:,}")