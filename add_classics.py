import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

INPUT_FILE = os.path.join(
    DATA_DIR,
    "catalog_enriched_repaired.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "catalog_enriched_final.csv"
)

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)

API_KEY = os.getenv(
    "TMDB_API_KEY"
)

if not API_KEY:
    raise ValueError(
        "TMDB_API_KEY not found in .env"
    )

BASE_URL = "https://api.themoviedb.org/3"


# =========================================================
# LOAD EXISTING CATALOG
# =========================================================

print("=" * 70)
print("CINESPHERE CLASSIC MOVIE ADDITION")
print("=" * 70)

df = pd.read_csv(
    INPUT_FILE
)

print(
    f"\nExisting catalog: {len(df)} items"
)


# =========================================================
# TMDB REQUEST
# =========================================================

def tmdb_get(
    endpoint,
    params=None,
    retries=5
):

    if params is None:
        params = {}

    params["api_key"] = API_KEY

    url = BASE_URL + endpoint

    for attempt in range(
        1,
        retries + 1
    ):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()

            print(
                f"HTTP {response.status_code} "
                f"(attempt {attempt}/{retries})"
            )

        except requests.RequestException as error:

            print(
                f"Network error "
                f"(attempt {attempt}/{retries}): "
                f"{error}"
            )

        if attempt < retries:

            wait_time = attempt * 3

            print(
                f"Retrying in "
                f"{wait_time}s..."
            )

            time.sleep(
                wait_time
            )

    return None


# =========================================================
# SEARCH TMDB
# =========================================================

def search_movie(title):

    data = tmdb_get(
        "/search/movie",
        {
            "query": title,
            "language": "en-US",
            "include_adult": "false"
        }
    )

    if not data:
        return None

    results = data.get(
        "results",
        []
    )

    if not results:
        return None

    return results[0]


# =========================================================
# MOVIES WE WANT TO ADD
# =========================================================

classic_movies = [
    "Baahubali: The Beginning",
    "Baahubali 2: The Conclusion"
]


# =========================================================
# ADD MOVIES
# =========================================================

added = 0
skipped = 0
failed = 0


for title in classic_movies:

    print(
        "\n" + "-" * 60
    )

    print(
        f"Searching TMDB: {title}"
    )

    result = search_movie(
        title
    )

    if not result:

        print(
            "❌ Movie not found"
        )

        failed += 1
        continue


    content_id = result.get(
        "id"
    )

    tmdb_title = result.get(
        "title",
        title
    )

    release_date = result.get(
        "release_date",
        ""
    )

    print(
        f"Found: {tmdb_title}"
    )

    print(
        f"TMDB ID: {content_id}"
    )

    print(
        f"Release: {release_date}"
    )


    # =====================================================
    # DUPLICATE CHECK
    # =====================================================

    existing = df[
        (
            df["content_type"]
            == "movie"
        )
        &
        (
            df["content_id"]
            == content_id
        )
    ]

    if not existing.empty:

        print(
            "⚠ Already exists. Skipping."
        )

        skipped += 1
        continue


    # =====================================================
    # GET FULL DETAILS
    # =====================================================

    details = tmdb_get(
        f"/movie/{content_id}",
        {
            "language": "en-US",
            "append_to_response":
                "credits,keywords"
        }
    )

    if not details:

        print(
            "❌ Details request failed"
        )

        failed += 1
        continue


    # =====================================================
    # GENRES
    # =====================================================

    genres = details.get(
        "genres",
        []
    )

    genre_names = [
        g.get("name", "")
        for g in genres
        if g.get("name")
    ]

    genres_text = ", ".join(
        genre_names
    )


    # =====================================================
    # KEYWORDS
    # =====================================================

    keyword_data = details.get(
        "keywords",
        {}
    )

    keyword_list = keyword_data.get(
        "keywords",
        []
    )

    keyword_names = [
        k.get("name", "")
        for k in keyword_list
        if k.get("name")
    ]

    keywords_text = ", ".join(
        keyword_names
    )


    # =====================================================
    # CAST
    # =====================================================

    credits = details.get(
        "credits",
        {}
    )

    cast_list = credits.get(
        "cast",
        []
    )

    cast_names = [
        person.get("name", "")
        for person in cast_list[:8]
        if person.get("name")
    ]

    cast_text = ", ".join(
        cast_names
    )


    # =====================================================
    # DIRECTOR
    # =====================================================

    crew = credits.get(
        "crew",
        []
    )

    directors = [
        person.get("name", "")
        for person in crew
        if person.get("job") == "Director"
        and person.get("name")
    ]

    director_text = ", ".join(
        directors[:3]
    )


    # =====================================================
    # RUNTIME
    # =====================================================

    runtime = details.get(
        "runtime"
    )


    # =====================================================
    # BUILD RECORD
    # =====================================================

    new_record = {
        "content_id": content_id,
        "content_type": "movie",
        "title": details.get(
            "title",
            tmdb_title
        ),
        "overview": details.get(
            "overview",
            ""
        ),
        "release_date": details.get(
            "release_date",
            ""
        ),
        "rating": details.get(
            "vote_average",
            0
        ),
        "vote_count": details.get(
            "vote_count",
            0
        ),
        "popularity": details.get(
            "popularity",
            0
        ),
        "language": details.get(
            "original_language",
            ""
        ),
        "language_name": "Telugu",
        "country": "India",
        "poster_path": details.get(
            "poster_path"
        ),
        "backdrop_path": details.get(
            "backdrop_path"
        ),
        "genres": genres_text,
        "keywords": keywords_text,
        "cast": cast_text,
        "director": director_text,
        "runtime": runtime
    }


    # =====================================================
    # APPEND
    # =====================================================

    df = pd.concat(
        [
            df,
            pd.DataFrame(
                [new_record]
            )
        ],
        ignore_index=True
    )

    added += 1

    print(
        "✓ Added successfully"
    )

    time.sleep(1)


# =========================================================
# FINAL DUPLICATE PROTECTION
# =========================================================

df = df.drop_duplicates(
    subset=[
        "content_type",
        "content_id"
    ],
    keep="first"
).reset_index(
    drop=True
)


# =========================================================
# SAVE
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)


# =========================================================
# SUMMARY
# =========================================================

print(
    "\n" + "=" * 70
)

print(
    "CLASSIC MOVIE ADDITION COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Original records: 8492"
)

print(
    f"Added: {added}"
)

print(
    f"Already existed: {skipped}"
)

print(
    f"Failed: {failed}"
)

print(
    f"Final records: {len(df)}"
)

print(
    f"\nSaved to:"
)

print(
    OUTPUT_FILE
)


# =========================================================
# VERIFY BAahUBALI
# =========================================================

print(
    "\n" + "-" * 70
)

print(
    "BAAHUBALI VERIFICATION"
)

print(
    "-" * 70
)

bahubali = df[
    df["title"]
    .fillna("")
    .str.contains(
        "bahubali|baahubali",
        case=False,
        na=False
    )
]

print(
    bahubali[
        [
            "content_id",
            "title",
            "content_type",
            "language_name",
            "release_date"
        ]
    ].to_string(
        index=False
    )
)