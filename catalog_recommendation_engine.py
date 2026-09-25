import os
import joblib
import pandas as pd
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity
import requests
from dotenv import load_dotenv
from functools import lru_cache
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# =========================================================
# CineSphere - Catalog Recommendation Engine
# 2313 Movies + TV / Web Series
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

TFIDF_PATH = os.path.join(
    MODEL_DIR,
    "catalog_tfidf_vectorizer.pkl"
)

TFIDF_MATRIX_PATH = os.path.join(
    MODEL_DIR,
    "catalog_tfidf_matrix.npz"
)

CATALOG_PATH = os.path.join(
    MODEL_DIR,
    "catalog_processed.csv"
)


# ---------------------------------------------------------
# Load ML model and catalog
# ---------------------------------------------------------

tfidf = joblib.load(TFIDF_PATH)

tfidf_matrix = load_npz(
    TFIDF_MATRIX_PATH
)

df = pd.read_csv(CATALOG_PATH)

df = df.reset_index(drop=True)

@lru_cache(maxsize=512)
def get_watch_providers(content_id, content_type="movie"):
    """
    Get legal streaming/watch options for India from TMDB.
    Returns provider names and the official TMDB watch link.
    """

    if not TMDB_API_KEY:
        return {
            "link": None,
            "providers": []
        }

    media_type = "tv" if str(content_type).lower() == "tv" else "movie"

    url = f"{TMDB_BASE_URL}/{media_type}/{int(content_id)}/watch/providers"

    try:
        response = requests.get(
            url,
            params={
                "api_key": TMDB_API_KEY
            },
            timeout=8
        )

        response.raise_for_status()

        data = response.json()

        india_data = data.get("results", {}).get("IN", {})

        watch_link = india_data.get("link")

        providers = []

        # Subscription / streaming services
        for provider in india_data.get("flatrate", []):

            provider_name = provider.get("provider_name")

            if provider_name and provider_name not in providers:
                providers.append(provider_name)

        # Free legal services
        for provider in india_data.get("free", []):

            provider_name = provider.get("provider_name")

            if provider_name and provider_name not in providers:
                providers.append(provider_name)

        # Rent / Buy options
        for provider in india_data.get("rent", []):

            provider_name = provider.get("provider_name")

            if provider_name and provider_name not in providers:
                providers.append(provider_name)

        for provider in india_data.get("buy", []):

            provider_name = provider.get("provider_name")

            if provider_name and provider_name not in providers:
                providers.append(provider_name)

        return {
            "link": watch_link,
            "providers": providers
        }

    except Exception:
        return {
            "link": None,
            "providers": []
        }
# ---------------------------------------------------------
# Get item by content_id
# ---------------------------------------------------------

def get_catalog_item_by_id(content_id):

    result = df[
        df["content_id"] == content_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


# ---------------------------------------------------------
# Search Movies / TV Shows
# ---------------------------------------------------------

def search_catalog(query, limit=12):

    query = str(query).strip().lower()

    if not query:
        return pd.DataFrame()

    results = df[
        df["title"]
        .fillna("")
        .str.lower()
        .str.contains(
            query,
            na=False
        )
    ]

    return results.head(limit)



# ---------------------------------------------------------
# Fast ML Content-Based Recommendations
# ---------------------------------------------------------

def recommend_catalog(
    content_id,
    num_recommendations=6
):

    matches = df.index[
        df["content_id"] == content_id
    ].tolist()

    if not matches:
        return pd.DataFrame()

    item_index = matches[0]

    selected_title = str(
        df.loc[item_index, "title"]
    ).strip().lower()

    # -----------------------------------------------------
    # Get similarity scores
    # -----------------------------------------------------

    scores = cosine_similarity(
    tfidf_matrix[item_index],
    tfidf_matrix
    ).flatten()
    # -----------------------------------------------------
    # Get only the strongest candidates first
    #
    # We do NOT sort all 8,492 records.
    # -----------------------------------------------------

    candidate_count = min(
        100,
        len(scores)
    )

    top_indices = scores.argsort()[
        -candidate_count:
    ][::-1]

    candidates = []

    for index in top_indices:

        index = int(index)

        # Skip selected item
        if index == item_index:
            continue

        current_title = str(
            df.loc[index, "title"]
        ).strip().lower()

        # Avoid duplicate same-title recommendations
        if current_title == selected_title:
            continue

        similarity_score = float(
            scores[index]
        )

        # Ignore very weak content matches
        if similarity_score < 0.10:
            continue

        rating = float(
            df.loc[index, "rating"]
        )

        vote_count = float(
            df.loc[index, "vote_count"]
        )

        popularity = float(
            df.loc[index, "popularity"]
        )

        # -------------------------------------------------
        # Quality signals
        # -------------------------------------------------

        rating_score = min(
            max(rating / 10.0, 0.0),
            1.0
        )

        vote_score = min(
            vote_count / 1000.0,
            1.0
        )

        popularity_score = min(
            max(popularity / 100.0, 0.0),
            1.0
        )

        # -------------------------------------------------
        # Final recommendation score
        # -------------------------------------------------

        final_score = (
            similarity_score * 0.75
            + rating_score * 0.10
            + vote_score * 0.10
            + popularity_score * 0.05
        )

        candidates.append({

            "content_id":
                df.loc[index, "content_id"],

            "content_type":
                df.loc[index, "content_type"],

            "title":
                df.loc[index, "title"],

            "genres":
                df.loc[index, "genres"],

            "rating":
                rating,

            "vote_count":
                vote_count,

            "popularity":
                popularity,

            "similarity_score":
                round(
                    similarity_score,
                    3
                ),

            "recommendation_score":
                round(
                    final_score,
                    3
                ),

            "release_date":
                df.loc[index, "release_date"],

            "poster_path":
                df.loc[index, "poster_path"],

            "overview":
                df.loc[index, "overview"],

            "language_name":
                df.loc[index, "language_name"],

            "runtime":
                df.loc[index, "runtime"],

            "director":
                df.loc[index, "director"]
        })

    # -----------------------------------------------------
    # Final ranking
    # -----------------------------------------------------

    candidates.sort(
        key=lambda x: x["recommendation_score"],
        reverse=True
    )

    return pd.DataFrame(
        candidates[:num_recommendations]
    )
# ---------------------------------------------------------
# Quick standalone test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("CINESPHERE CATALOG RECOMMENDATION ENGINE")
    print("=" * 55)

    print(f"Catalog records: {len(df)}")
    print(
    f"TF-IDF matrix: "
    f"{tfidf_matrix.shape}"
)

    test_item = df.iloc[0]

    print("\nTest item:")
    print(
        f"{test_item['title']} "
        f"({test_item['content_type']})"
    )

    recommendations = recommend_catalog(
        test_item["content_id"],
        5
    )

    print("\nRecommendations:")

    if recommendations.empty:

        print("No recommendations found.")

    else:

        for _, movie in recommendations.iterrows():

            print(
                f"- {movie['title']} | "
                f"{movie['content_type']} | "
                f"Similarity: "
                f"{movie['similarity_score']}"
            )

    print("\nEngine test complete.")