import streamlit as st
import pandas as pd
import re
import unicodedata
from catalog_recommendation_engine import (
    df as catalog_df,
    search_catalog,
    recommend_catalog,
    get_catalog_item_by_id,
    get_watch_providers
)

# Use final CineSphere catalog
df = catalog_df

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CineSphere | Discover Movies",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(120, 70, 180, 0.12),
                transparent 28%
            ),
            radial-gradient(
                circle at 85% 20%,
                rgba(40, 120, 220, 0.10),
                transparent 25%
            ),
            #08090d;
        color: #ffffff;
    }

    /* Hide Streamlit default header */
    header {
        background: transparent !important;
    }

    /* Main content width */
    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Hero */
    .hero {
        padding: 45px 20px 35px 20px;
        text-align: center;
    }

    .hero-badge {
        display: inline-block;
        padding: 7px 16px;
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 30px;
        background: rgba(255,255,255,0.05);
        color: #b9b9c8;
        font-size: 13px;
        letter-spacing: 1px;
        margin-bottom: 18px;
    }

    .hero h1 {
        font-size: clamp(42px, 7vw, 78px);
        font-weight: 800;
        letter-spacing: -3px;
        margin: 0;
        line-height: 1;
    }

    .hero h1 span {
        background: linear-gradient(
            90deg,
            #ffffff,
            #a78bfa,
            #60a5fa
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero p {
        color: #a7a7b5;
        font-size: 17px;
        margin-top: 18px;
    }

    /* Section headings */
    .section-title {
        font-size: 26px;
        font-weight: 750;
        margin-top: 35px;
        margin-bottom: 18px;
    }

    .section-subtitle {
        color: #8f909d;
        margin-top: -12px;
        margin-bottom: 20px;
    }

    /* Movie card */
    .movie-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        overflow: hidden;
        transition: 0.25s ease;
        height: 100%;
    }

    .movie-card:hover {
        transform: translateY(-5px);
        border-color: rgba(167,139,250,0.45);
        background: rgba(255,255,255,0.07);
    }

    .movie-info {
        padding: 12px;
    }

    .movie-title {
        font-size: 15px;
        font-weight: 700;
        color: white;
        margin-bottom: 6px;
        min-height: 38px;
    }

    .movie-meta {
        color: #9b9ca8;
        font-size: 12px;
    }

    .rating {
        color: #facc15;
        font-weight: 700;
    }

    /* Search */
    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        color: white;
        border-radius: 12px;
    }
    
        /* Mobile responsive adjustments */
    @media (max-width: 768px) {

        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 2rem;
        }

        .hero {
            padding: 30px 10px 25px 10px;
        }

        .hero h1 {
            font-size: 42px;
            letter-spacing: -1.5px;
        }

        .hero p {
            font-size: 14px;
        }

        .section-title {
            font-size: 22px;
        }

        .movie-title {
            font-size: 14px;
        }
    }

    /* =========================================================
   CINESPHERE PREMIUM UI ENHANCEMENT
   Visual only - no functionality changes
   ========================================================= */

/* Premium overall background */
.stApp {
    background:
        radial-gradient(
            circle at 15% 5%,
            rgba(124, 58, 237, 0.14),
            transparent 32%
        ),
        radial-gradient(
            circle at 85% 15%,
            rgba(59, 130, 246, 0.10),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #09090f 0%,
            #0b0b12 45%,
            #070910 100%
        );
}

/* Smooth page appearance */
.main .block-container {
    animation: cineFadeIn 0.7s ease-out;
}

@keyframes cineFadeIn {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* =========================================================
   HERO
   ========================================================= */

.hero {
    position: relative;
    padding: 55px 25px 45px;
    border-radius: 28px;
    margin-bottom: 35px;

    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(139, 92, 246, 0.18),
            transparent 55%
        ),
        linear-gradient(
            135deg,
            rgba(20, 18, 35, 0.95),
            rgba(8, 10, 18, 0.96)
        );

    border: 1px solid rgba(255,255,255,0.07);

    box-shadow:
        0 25px 70px rgba(0,0,0,0.45),
        inset 0 1px 0 rgba(255,255,255,0.04);

    overflow: hidden;
}

/* cinematic glow */
.hero::before {
    content: "";
    position: absolute;
    width: 420px;
    height: 420px;
    top: -220px;
    left: 50%;
    transform: translateX(-50%);

    background: radial-gradient(
        circle,
        rgba(139,92,246,0.20),
        transparent 68%
    );

    filter: blur(20px);
    pointer-events: none;
}

.hero h1 {
    position: relative;
    text-shadow:
        0 0 30px rgba(139,92,246,0.22);

    animation: heroTitle 0.9s ease-out;
}

@keyframes heroTitle {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero p {
    position: relative;
    opacity: 0.82;
}


/* =========================================================
   SECTION HEADINGS
   ========================================================= */

.section-title {
    position: relative;
    margin-top: 32px;
    margin-bottom: 8px;
}

.section-title::after {
    content: "";
    display: block;

    width: 45px;
    height: 3px;

    margin-top: 9px;

    border-radius: 10px;

    background: linear-gradient(
        90deg,
        #8b5cf6,
        #60a5fa
    );

    box-shadow:
        0 0 14px rgba(139,92,246,0.55);
}


/* =========================================================
   PREMIUM SELECT BOXES
   ========================================================= */

div[data-baseweb="select"] > div {
    background:
        linear-gradient(
            145deg,
            rgba(35,35,47,0.92),
            rgba(22,22,31,0.95)
        ) !important;

    border: 1px solid rgba(255,255,255,0.08) !important;

    border-radius: 13px !important;

    transition:
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.2s ease;
}

div[data-baseweb="select"] > div:hover {
    border-color: rgba(139,92,246,0.55) !important;

    box-shadow:
        0 0 20px rgba(139,92,246,0.12);

    transform: translateY(-1px);
}


/* =========================================================
   SEARCH BOX
   ========================================================= */

div[data-baseweb="input"] {
    background:
        linear-gradient(
            145deg,
            rgba(32,32,44,0.95),
            rgba(20,20,29,0.98)
        ) !important;

    border: 1px solid rgba(255,255,255,0.09) !important;

    border-radius: 15px !important;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.22);

    transition:
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.2s ease;
}

div[data-baseweb="input"]:focus-within {
    border-color: rgba(139,92,246,0.70) !important;

    box-shadow:
        0 0 0 3px rgba(139,92,246,0.10),
        0 0 28px rgba(139,92,246,0.16);

    transform: translateY(-1px);
}

div[data-baseweb="input"] input {
    color: #f5f5f5 !important;
}


/* =========================================================
   MOVIE CARDS
   ========================================================= */

.movie-card {
    border-radius: 16px;

    border: 1px solid rgba(255,255,255,0.07);

    background:
        linear-gradient(
            145deg,
            rgba(30,30,42,0.90),
            rgba(15,15,22,0.96)
        );

    box-shadow:
        0 12px 30px rgba(0,0,0,0.22);

    transition:
        transform 0.28s ease,
        box-shadow 0.28s ease,
        border-color 0.28s ease;
}

.movie-card:hover {
    transform: translateY(-6px);

    border-color: rgba(139,92,246,0.38);

    box-shadow:
        0 18px 45px rgba(0,0,0,0.38),
        0 0 25px rgba(139,92,246,0.10);
}


/* =========================================================
   STREAMLIT BUTTONS
   ========================================================= */

.stButton > button {
    border-radius: 11px !important;

    border: 1px solid rgba(139,92,246,0.30) !important;

    background:
        linear-gradient(
            135deg,
            rgba(124,58,237,0.18),
            rgba(59,130,246,0.12)
        ) !important;

    color: #f5f5f5 !important;

    transition:
        transform 0.2s ease,
        box-shadow 0.25s ease,
        border-color 0.25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);

    border-color: rgba(139,92,246,0.65) !important;

    box-shadow:
        0 8px 25px rgba(124,58,237,0.18);
}


/* =========================================================
   SUBTLE DIVIDERS
   ========================================================= */

hr {
    border: none !important;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(139,92,246,0.35),
            rgba(96,165,250,0.25),
            transparent
        );

    margin: 35px 0;
}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 768px) {

    .hero {
        padding: 35px 18px 30px;
        border-radius: 20px;
    }

    .hero h1 {
        font-size: 38px;
        line-height: 1.08;
    }

    .section-title {
        font-size: 21px;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] {
        border-radius: 12px !important;
    }
}

/* =========================================================
   CINESPHERE — PREMIUM MOBILE UI
   Visual only — no functionality changes
   ========================================================= */

@media (max-width: 768px) {

    /* ---------- Main page spacing ---------- */

    .main .block-container {
        padding-left: 14px !important;
        padding-right: 14px !important;
        padding-top: 12px !important;
        padding-bottom: 30px !important;
    }


    /* ---------- Hero ---------- */

    .hero {
        min-height: 330px;

        display: flex;
        flex-direction: column;
        justify-content: center;

        padding: 38px 20px !important;

        margin-bottom: 25px;

        border-radius: 22px;

        background:
            radial-gradient(
                circle at 50% 10%,
                rgba(139,92,246,0.20),
                transparent 55%
            ),
            linear-gradient(
                145deg,
                rgba(20,18,32,0.98),
                rgba(7,9,16,0.98)
            );

        box-shadow:
            0 20px 50px rgba(0,0,0,0.42);
    }


    .hero h1 {
        font-size: 38px !important;
        line-height: 1.08 !important;
        letter-spacing: -1.3px !important;

        margin-bottom: 14px !important;
    }


    .hero p {
        font-size: 14px !important;
        line-height: 1.6 !important;
    }


    /* ---------- Section headings ---------- */

    .section-title {
        font-size: 22px !important;
        line-height: 1.25;

        margin-top: 28px !important;
        margin-bottom: 8px !important;
    }


    /* ---------- Section description ---------- */

    .section-description {
        font-size: 13px !important;
        line-height: 1.55 !important;
        opacity: 0.72;
    }


    /* ---------- Select boxes ---------- */

    div[data-baseweb="select"] {
        margin-bottom: 10px !important;
    }

    div[data-baseweb="select"] > div {
        min-height: 46px !important;

        border-radius: 12px !important;

        background:
            linear-gradient(
                145deg,
                rgba(35,35,47,0.96),
                rgba(20,20,29,0.98)
            ) !important;
    }


    /* ---------- Search ---------- */

    div[data-baseweb="input"] {
        min-height: 48px !important;

        border-radius: 13px !important;

        margin-top: 8px !important;
    }

    div[data-baseweb="input"] input {
        font-size: 14px !important;
    }


    /* ---------- Buttons ---------- */

    .stButton > button {
        min-height: 44px !important;

        border-radius: 11px !important;

        font-size: 13px !important;
    }


    /* ---------- Movie cards ---------- */

    .movie-card {
        border-radius: 14px;

        overflow: hidden;

        box-shadow:
            0 10px 25px rgba(0,0,0,0.30);
    }

    .movie-card:hover {
        transform: translateY(-3px);
    }


    /* ---------- Movie title ---------- */

    .movie-title {
        font-size: 14px !important;
        line-height: 1.35 !important;
    }


    /* ---------- Small metadata ---------- */

    .movie-meta {
        font-size: 11px !important;
    }


    /* ---------- Images ---------- */

    .movie-card img {
        border-radius: 12px;

        transition:
            transform 0.3s ease,
            filter 0.3s ease;
    }


    /* ---------- Dividers ---------- */

    hr {
        margin: 28px 0 !important;
    }


    /* ---------- Touch feedback ---------- */

    .stButton > button:active {
        transform: scale(0.97);
    }


    /* ---------- Smooth mobile appearance ---------- */

    .stMarkdown,
    .stSelectbox,
    .stTextInput,
    .stButton {
        animation: mobileFadeUp 0.45s ease-out both;
    }

    @keyframes mobileFadeUp {
        from {
            opacity: 0;
            transform: translateY(8px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# CONSTANTS
# =========================================================

IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


# =========================================================
# HELPER
# =========================================================

def poster_url(poster_path):

    if pd.isna(poster_path) or not poster_path:
        return None

    return IMAGE_BASE_URL + str(poster_path)


def display_movie_card(movie, card_key=""):

    poster = poster_url(movie.get("poster_path"))

    if poster:
        st.image(
            poster,
            use_container_width=True
        )
    else:
        st.html("""
        <div style="
            height:320px;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#15161d;
            border-radius:12px;
            color:#777;
            font-size:16px;
        ">
            🎬 No Poster
        </div>
        """)

    title = str(movie.get("title", "Unknown"))

    rating = movie.get("rating", 0)

    release_date = str(
        movie.get("release_date", "")
    )

    year = (
        release_date[:4]
        if len(release_date) >= 4
        else "N/A"
    )

    st.html(f"""
    <div class="movie-info">
        <div class="movie-title">
            {title}
        </div>

        <div class="movie-meta">
            <span class="rating">
                ★ {float(rating):.1f}
            </span>
            &nbsp; • &nbsp;
            {year}
        </div>
    </div>
    """)

    content_id = int(movie.get("content_id"))

    if st.button(
      "View Details",
       key=f"details_{content_id}_{card_key}",
       use_container_width=True
):
     st.session_state["selected_content_id"] = content_id
     st.rerun()
   

        # =========================================================
# MOVIE DETAILS
# =========================================================

if "selected_content_id" in st.session_state:

    selected_content_id = st.session_state["selected_content_id"]

    selected_movie = df[
        df["content_id"] == selected_content_id
    ]
    
    if not selected_movie.empty:
        movie = selected_movie.iloc[0]

        content_type = str(
            movie.get("content_type", "movie")
        ).lower()

        is_tv = content_type == "tv"

        content_label = "Series" if is_tv else "Movie"
        person_label = "Creator" if is_tv else "Director"
        runtime_label = "Episode Runtime" if is_tv else "Runtime"

        # Back button
        if st.button("← Back to CineSphere"):
            del st.session_state["selected_content_id"]
            st.rerun()

        title = str(movie.get("title", "Unknown"))

        rating = float(movie.get("rating", 0))

        release_date = str(
            movie.get("release_date", "")
        )

        year = (
            release_date[:4]
            if len(release_date) >= 4
            else "N/A"
        )

        poster = poster_url(
            movie.get("poster_path")
        )

        genres = str(
            movie.get("genres", "N/A")
        )

        runtime = movie.get(
            "runtime",
            None
        )

        runtime_text = (
            f"{int(runtime)} min"
            if pd.notna(runtime)
            else "N/A"
        )

        director = str(
            movie.get("director", "N/A")
        )

        cast = str(
            movie.get("cast", "N/A")
        )

        overview = str(
            movie.get("overview", "")
        )

        keywords = str(
            movie.get("keywords", "")
        )

        # -------------------------------------------------
        # MOVIE HEADER
        # -------------------------------------------------

        st.html(f"""
        <div style="
            padding:35px;
            margin:20px 0 30px 0;
            border-radius:24px;
            background:
                linear-gradient(
                    135deg,
                    rgba(167,139,250,0.14),
                    rgba(96,165,250,0.06)
                );
            border:1px solid rgba(255,255,255,0.10);
        ">

            <h1 style="
                font-size:42px;
                margin-bottom:10px;
                color:white;
            ">
                {title}
            </h1>

            <div style="
                color:#a7a7b5;
                font-size:15px;
            ">
                ⭐ {rating:.1f}
                &nbsp; • &nbsp;
                {year}
                &nbsp; • &nbsp;
                {runtime_text}
            </div>

        </div>
        """)

        # -------------------------------------------------
        # POSTER + INFORMATION
        # -------------------------------------------------

        col1, col2 = st.columns(
            [1, 2],
            gap="large"
        )

        with col1:

            if poster:

                st.image(
                    poster,
                    use_container_width=True
                )

            else:

                st.html("""
                <div style="
                    height:450px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    background:#15161d;
                    border-radius:16px;
                    color:#777;
                ">
                    🎬 No Poster
                </div>
                """)

        with col2:

            st.html(f"""
            <div style="
                padding:10px 5px;
                color:#ddd;
                line-height:1.7;
            ">
<h3 style="color:white;">
    About the {content_label}
</h3>

                <p style="
                    color:#a7a7b5;
                    font-size:16px;
                ">
                    {overview}
                </p>

                <hr style="
                    border-color:rgba(255,255,255,0.08);
                ">

                <p>
                    <strong>🎭 Genres:</strong>
                    {genres}
                </p>

                <p>
                    <strong>🎬 {person_label}:</strong>
{director}
                </p>

                <p>
                    <strong>👥 Cast:</strong>
                    {cast}
                </p>

                <p>
                    <strong>⏱ {runtime_label}:</strong>
{runtime_text}
                </p>

                <p>
                    <strong>🏷 Keywords:</strong>
                    {keywords if keywords else "N/A"}
                </p>

            </div>
            """)
                # -------------------------------------------------
        # WATCH NOW
        # -------------------------------------------------

        watch_data = get_watch_providers(
            selected_content_id,
            content_type
        )

        watch_link = watch_data.get("link")
        watch_providers = watch_data.get("providers", [])
        st.write("DEBUG WATCH:", watch_data)

        if watch_link and watch_providers:

            provider_text = " • ".join(
                watch_providers[:6]
            )

            st.markdown(
                "### ▶️ Watch Now"
            )

            st.markdown(
                "Available legally in India."
            )

            st.markdown(
                f"**Available on:** {provider_text}"
            )

            st.link_button(
                "▶️ Watch Now",
                watch_link,
                use_container_width=True
            ) 

        # -------------------------------------------------
        # AI RECOMMENDATIONS
        # -------------------------------------------------

        st.markdown(
            """
            <div class="section-title">
                🧠 You May Also Like
            </div>

            <div class="section-subtitle">
                Similar movies selected by CineSphere's
                content-based recommendation engine.
            </div>
            """,
            unsafe_allow_html=True
        )
        recommendations = recommend_catalog(
            selected_content_id,
            6
        )

        if not recommendations.empty:

            columns = st.columns(6)

            for i, (_, rec_movie) in enumerate(
                recommendations.iterrows()
            ):

                 with columns[i]:

                    display_movie_card(
           rec_movie,
        f"similar_{i}"
                    )


        st.stop()

    else:

      del st.session_state["selected_content_id"]
# =========================================================
# HERO
# =========================================================

st.html("""
<div class="hero">
    <div class="hero-badge">✦ MOVIE DISCOVERY • POWERED BY ML</div>

    <h1>Welcome to <span>CineSphere</span></h1>

    <p>
        Discover movies you'll love.
        Explore. Search. Get intelligent recommendations.
    </p>
</div>
""")
# =========================================================
# CONTENT TYPE FILTER
# =========================================================

content_type_options = [
    "All",
    "Movies",
    "TV / Web Series"
]

selected_content_type = st.selectbox(
    "Content Type",
    content_type_options
)

if selected_content_type == "Movies":

    browse_df = df[
        df["content_type"] == "movie"
    ].copy()

elif selected_content_type == "TV / Web Series":

    browse_df = df[
        df["content_type"] == "tv"
    ].copy()

else:

 browse_df = df.copy()
# =========================================================
# GENRE EXPLORER
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🎭 Explore by Genre
    </div>

    <div class="section-subtitle">
        Find movies based on your favourite genre.
    </div>
    """,
    unsafe_allow_html=True
)

genre_options = [
    "All",
    "Action",
    "Adventure",
    "Comedy",
    "Drama",
    "Horror",
    "Science Fiction",
    "Thriller",
    "Fantasy",
    "Animation",
    "Crime",
    "Romance"
]

selected_genre = st.selectbox(
    "Choose a genre",
    genre_options,
    label_visibility="collapsed"
)

industry_options = [
    "All Industries",
    "Bollywood",
    "Hollywood",
    "Telugu / Tollywood",
    "Tamil",
    "Malayalam",
    "Kannada",
    "Bengali",
    "Marathi",
    "Punjabi",
    "Gujarati",
    "Korean",
    "Japanese",
    "Chinese",
    "French",
    "Spanish"
]

selected_industry = st.selectbox(
    "Choose an industry / region",
    industry_options,
    label_visibility="collapsed"
)
# =========================================================
# GENRE FILTER
# =========================================================

if selected_genre != "All" or selected_industry != "All Industries":

    genre_movies = browse_df.copy()

    # Genre filter
    if selected_genre != "All":

        genre_movies = genre_movies[
            genre_movies["genres"]
            .fillna("")
            .str.contains(
                selected_genre,
                case=False,
                na=False
            )
        ]

    # Industry / Region filter
    if selected_industry != "All Industries":

        industry_map = {
            "Bollywood": {
                "language": "Hindi",
                "country": "IN"
            },

            "Hollywood": {
                "language": "English",
                "country": "US"
            },

            "Telugu / Tollywood": {
                "language": "Telugu",
                "country": "IN"
            },

            "Tamil": {
                "language": "Tamil",
                "country": "IN"
            },

            "Malayalam": {
                "language": "Malayalam",
                "country": "IN"
            },

            "Kannada": {
                "language": "Kannada",
                "country": "IN"
            },

            "Bengali": {
                "language": "Bengali",
                "country": "IN"
            },

            "Marathi": {
                "language": "Marathi",
                "country": "IN"
            },

            "Punjabi": {
                "language": "Punjabi",
                "country": "IN"
            },

            "Gujarati": {
                "language": "Gujarati",
                "country": "IN"
            },

            "Korean": {
                "language": "Korean",
                "country": "KR"
            },

            "Japanese": {
                "language": "Japanese",
                "country": "JP"
            },

            "Chinese": {
                "language": "Chinese",
                "country": "CN"
            },

            "French": {
                "language": "French",
                "country": "FR"
            },

            "Spanish": {
                "language": "Spanish",
                "country": "ES"
            }
        }

        selected_filter = industry_map[selected_industry]

        genre_movies = genre_movies[
            (genre_movies["language_name"] == selected_filter["language"]) &
            (genre_movies["country"] == selected_filter["country"])
        ]

    genre_movies = genre_movies.sort_values(
        "popularity",
        ascending=False
    ).head(24)

    st.markdown(
        f"""
        <div class="section-title">
            🎬 {selected_genre if selected_genre != "All" else "All Genres"}
        </div>

        <div class="section-subtitle">
            {selected_industry} • {len(genre_movies)} titles found
        </div>
        """,
        unsafe_allow_html=True
    )

    if genre_movies.empty:

        st.info(
            "No titles found for the selected filters."
        )

    else:

        columns = st.columns(6)

        for i, (_, movie) in enumerate(
            genre_movies.iterrows()
        ):

            with columns[i % 6]:

                display_movie_card(
                    movie,
                    f"genre_{i}"
                )

   

# =========================================================
# SEARCH
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🔍 Search CineSphere
    </div>

    <div class="section-subtitle">
        Search movies, series, actors, genres and keywords.
    </div>
    """,
    unsafe_allow_html=True
)

search_query = st.text_input(
    "Search",
    placeholder="Search any movie or series...",
    label_visibility="collapsed"
)

def normalize_search_text(value):

    text = "" if pd.isna(value) else str(value)

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        ch
        for ch in text
        if not unicodedata.combining(ch)
    )

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


@st.cache_data
def build_search_index(data):

    search_data = data.copy()

    # Normalize searchable columns once
    search_data["_search_title"] = (
        search_data["title"]
        .fillna("")
        .map(normalize_search_text)
    )

    search_data["_search_cast"] = (
        search_data["cast"]
        .fillna("")
        .map(normalize_search_text)
    )

    search_data["_search_director"] = (
        search_data["director"]
        .fillna("")
        .map(normalize_search_text)
    )

    search_data["_search_genres"] = (
        search_data["genres"]
        .fillna("")
        .map(normalize_search_text)
    )

    search_data["_search_text"] = (
        search_data["_search_title"]
        + " "
        + search_data["overview"]
        .fillna("")
        .map(normalize_search_text)
        + " "
        + search_data["_search_genres"]
        + " "
        + search_data["keywords"]
        .fillna("")
        .map(normalize_search_text)
        + " "
        + search_data["_search_cast"]
        + " "
        + search_data["_search_director"]
        + " "
        + search_data["language_name"]
        .fillna("")
        .map(normalize_search_text)
        + " "
        + search_data["content_type"]
        .fillna("")
        .map(normalize_search_text)
    )

    return search_data


search_index = build_search_index(browse_df)


# =========================================================
# FAST SEARCH
# =========================================================

if search_query.strip():

    query = normalize_search_text(
        search_query
    )

    generic_terms = {
        "a", "an", "the",
        "of", "on", "in",
        "to", "for", "and",
        "movie", "movies",
        "film", "films",
        "series", "show",
        "shows", "tv",
        "web", "anime",
        "cartoon"
    }

    query_tokens = [
        token
        for token in query.split()
        if token not in generic_terms
    ]

    search_results = []

    if query_tokens:

        # Start with every record
        mask = pd.Series(
            True,
            index=search_index.index
        )

        # Every meaningful token must exist
        # Vectorized search = much faster than iterrows()
        for token in query_tokens:

            mask &= search_index[
                "_search_text"
            ].str.contains(
                token,
                case=False,
                regex=False,
                na=False
            )

        matched = search_index[mask].copy()

        if not matched.empty:

            # Calculate scores only for matching records
            for index, movie in matched.iterrows():

                title = movie["_search_title"]
                cast = movie["_search_cast"]
                director = movie["_search_director"]
                genres = movie["_search_genres"]

                score = 0

                # Exact title
                if title == query:
                    score += 1000

                # Query inside title
                elif query in title:
                    score += 500

                # Individual tokens in title
                for token in query_tokens:

                    if token in title:
                        score += 100

                # Actor match
                if any(
                    token in cast
                    for token in query_tokens
                ):
                    score += 40

                # Director match
                if any(
                    token in director
                    for token in query_tokens
                ):
                    score += 40

                # Genre match
                if any(
                    token in genres
                    for token in query_tokens
                ):
                    score += 30

                # Popularity
                popularity = float(
                    movie.get("popularity", 0)
                )

                score += min(
                    popularity / 10,
                    20
                )

                search_results.append(
                    (
                        score,
                        index,
                        movie
                    )
                )

            search_results.sort(
                key=lambda x: x[0],
                reverse=True
            )

            search_results = search_results[:8]

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    if not search_results:

        st.info(
            "No matching movies or series found."
        )

    else:

        st.markdown(
            f"""
            <div style="
                margin-top:10px;
                margin-bottom:12px;
                color:#9ca3af;
                font-size:13px;
            ">
                {len(search_results)} suggestions
            </div>
            """,
            unsafe_allow_html=True
        )

        for i, (
            score,
            index,
            movie
        ) in enumerate(search_results):

            content_id = int(
                movie["content_id"]
            )

            title = str(
                movie.get(
                    "title",
                    "Unknown"
                )
            )

            rating = float(
                movie.get(
                    "rating",
                    0
                )
            )

            release_date = str(
                movie.get(
                    "release_date",
                    ""
                )
            )

            year = (
                release_date[:4]
                if len(release_date) >= 4
                else "N/A"
            )

            language = str(
                movie.get(
                    "language_name",
                    "Unknown"
                )
            )

            content_type = str(
                movie.get(
                    "content_type",
                    "movie"
                )
            ).lower()

            type_label = (
                "TV / Web Series"
                if content_type == "tv"
                else "Movie"
            )

            poster = poster_url(
                movie.get("poster_path")
            )

            col1, col2 = st.columns(
                [1, 8],
                gap="small"
            )

            with col1:

                if poster:

                    st.image(
                        poster,
                        width=65
                    )

                else:

                    st.markdown("🎬")

            with col2:

                if st.button(
                    title,
                    key=f"search_suggestion_{content_id}_{i}",
                    use_container_width=True
                ):

                    st.session_state[
                        "selected_content_id"
                    ] = content_id

                    st.rerun()

                st.markdown(
                    f"""
                    <div style="
                        margin-top:-10px;
                        margin-bottom:14px;
                        color:#8f909d;
                        font-size:12px;
                    ">
                        ⭐ {rating:.1f}
                        &nbsp; • &nbsp;
                        {year}
                        &nbsp; • &nbsp;
                        {language}
                        &nbsp; • &nbsp;
                        {type_label}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
# =========================================================
# TRENDING
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🔥 Trending Now
    </div>

    <div class="section-subtitle">
        Popular movies people are discovering.
    </div>
    """,
    unsafe_allow_html=True
)

trending = browse_df.sort_values(
    "popularity",
    ascending=False
).head(6)

columns = st.columns(6)

for i, (_, movie) in enumerate(
    trending.iterrows()
):
    with columns[i]:

        display_movie_card(
            movie,
            f"trending_{i}"
        )


# =========================================================
# TOP RATED
# =========================================================

st.markdown(
    """
    <div class="section-title">
        ⭐ Top Rated
    </div>

    <div class="section-subtitle">
        Highly rated movies and series.
    </div>
    """,
    unsafe_allow_html=True
)

top_rated = browse_df.sort_values(
    "rating",
    ascending=False
).head(6)

columns = st.columns(6)

for i, (_, movie) in enumerate(
    top_rated.iterrows()
):
    with columns[i]:

        display_movie_card(
            movie,
            f"top_rated_{i}"
        )


# =========================================================
# LATEST
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🆕 Latest Releases
    </div>

    <div class="section-subtitle">
        Recently released movies and series.
    </div>
    """,
    unsafe_allow_html=True
)

latest = browse_df.sort_values(
    "release_date",
    ascending=False
).head(6)

columns = st.columns(6)

for i, (_, movie) in enumerate(
    latest.iterrows()
):
    with columns[i]:

        display_movie_card(
            movie,
            f"latest_{i}"
        )


# =========================================================
# ML RECOMMENDATION SHOWCASE
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🧠 AI Recommendations
    </div>

    <div class="section-subtitle">
        Content-based recommendations powered by
        TF-IDF and cosine similarity.
    </div>
    """,
    unsafe_allow_html=True
)

featured_movie = df[
    df["title"]
    .fillna("")
    .str.lower()
    == "spider-man: brand new day"
]

if not featured_movie.empty:

    content_id = int(
        featured_movie.iloc[0]["content_id"]
    )

    recommendations = recommend_catalog(
        content_id,
        6
    )

    if not recommendations.empty:

        columns = st.columns(6)

        for i, (_, movie) in enumerate(
            recommendations.iterrows()
        ):
            with columns[i]:

                display_movie_card(
                    movie,
                    f"ai_{i}"
                )

    else:

        st.info(
            "No AI recommendations available."
        )

else:

    st.info(
        "Featured movie not available in the catalog."
    )
# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <br><br>

    <div style="
        text-align:center;
        color:#666975;
        padding:30px;
        border-top:1px solid rgba(255,255,255,0.08);
    ">
        <strong style="color:#aaa;">
            CineSphere
        </strong>
        <br>
        Intelligent Movie Discovery Platform
        <br><br>
        Built with Python • Streamlit • Machine Learning
    </div>
    """,
    unsafe_allow_html=True
)
