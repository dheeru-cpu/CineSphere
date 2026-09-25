import os
import joblib
import pandas as pd


# ---------------------------------------------------
# Paths
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, "models")

TFIDF_PATH = os.path.join(
    MODEL_DIR,
    "tfidf_vectorizer.pkl"
)

SIMILARITY_PATH = os.path.join(
    MODEL_DIR,
    "similarity_matrix.pkl"
)

MOVIES_PATH = os.path.join(
    MODEL_DIR,
    "movies_processed.csv"
)


# ---------------------------------------------------
# Load ML model and movie data
# ---------------------------------------------------

tfidf = joblib.load(TFIDF_PATH)

similarity_matrix = joblib.load(
    SIMILARITY_PATH
)

df = pd.read_csv(
    MOVIES_PATH
)

# Make sure index is clean
df = df.reset_index(drop=True)


# ---------------------------------------------------
# Find movie by ID
# ---------------------------------------------------

def get_movie_by_id(movie_id):

    result = df[
        df["movie_id"] == movie_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


# ---------------------------------------------------
# Search movies by title
# ---------------------------------------------------

def search_movies(query, limit=10):

    query = query.strip().lower()

    if not query:
        return pd.DataFrame()

    results = df[
        df["title"]
        .str.lower()
        .str.contains(query, na=False)
    ]

    return results.head(limit)


# ---------------------------------------------------
# Recommend similar movies
# ---------------------------------------------------

def recommend_movies(
    movie_id,
    num_recommendations=5
):

    # Find selected movie
    matches = df.index[
        df["movie_id"] == movie_id
    ].tolist()

    if not matches:
        return pd.DataFrame()

    movie_index = matches[0]

    selected_title = (
        str(df.loc[movie_index, "title"])
        .strip()
        .lower()
    )

    # Similarity scores
    similarity_scores = list(
        enumerate(
            similarity_matrix[movie_index]
        )
    )

    similarity_scores.sort(
        key=lambda x: x[1],
        reverse=True
    )

    recommendations = []

    for index, score in similarity_scores:

        # Skip selected movie
        if index == movie_index:
            continue

        current_title = (
            str(df.loc[index, "title"])
            .strip()
            .lower()
        )

        # Skip same-title movie
        if current_title == selected_title:
            continue

        recommendations.append({
            "movie_id": int(
                df.loc[index, "movie_id"]
            ),

            "title": df.loc[
                index, "title"
            ],

            "genres": df.loc[
                index, "genres"
            ],

            "rating": float(
                df.loc[index, "rating"]
            ),

            "similarity_score": round(
                float(score),
                3
            ),

            "release_date": df.loc[
                index, "release_date"
            ],

            "poster_path": df.loc[
                index, "poster_path"
            ],

            "overview": df.loc[
                index, "overview"
            ]
        })

        if len(recommendations) >= num_recommendations:
            break

    return pd.DataFrame(
        recommendations
    )


# ---------------------------------------------------
# Test
# ---------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("CINESPHERE RECOMMENDATION ENGINE")
    print("=" * 60)

    print(
        f"Movies loaded: {len(df)}"
    )

    print(
        f"Similarity matrix: "
        f"{similarity_matrix.shape}"
    )

    print("\nSearching for Spider-Man...")

    results = search_movies(
        "Spider-Man"
    )

    print(
        results[
            [
                "movie_id",
                "title",
                "release_date",
                "rating"
            ]
        ].to_string(index=False)
    )

    if not results.empty:

        selected_movie_id = int(
            results.iloc[0]["movie_id"]
        )

        print(
            f"\nRecommendations for: "
            f"{results.iloc[0]['title']}"
        )

        recommendations = recommend_movies(
            selected_movie_id,
            5
        )

        print(
            recommendations[
                [
                    "movie_id",
                    "title",
                    "rating",
                    "similarity_score"
                ]
            ].to_string(index=False)
        )

    print("\nRecommendation engine working! ✅")