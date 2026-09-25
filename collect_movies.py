import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env file")


BASE_URL = "https://api.themoviedb.org/3"

OUTPUT_FILE = "data/catalog_enriched.csv"


# =========================================================
# REQUEST HELPER
# =========================================================

def tmdb_get(endpoint, params):

    url = f"{BASE_URL}/{endpoint}"

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        if response.status_code != 200:

            print(
                f"API Error {response.status_code}: "
                f"{response.text[:200]}"
            )

            return None

        return response.json()

    except Exception as e:

        print(f"Request error: {e}")

        return None


# =========================================================
# DISCOVER CONFIGURATION
# =========================================================

# language_code, display_name, country
MOVIE_SOURCES = [

    ("hi", "Hindi", "IN"),
    ("te", "Telugu", "IN"),
    ("ta", "Tamil", "IN"),
    ("ml", "Malayalam", "IN"),
    ("kn", "Kannada", "IN"),
    ("bn", "Bengali", "IN"),
    ("mr", "Marathi", "IN"),
    ("pa", "Punjabi", "IN"),
    ("gu", "Gujarati", "IN"),
    ("en", "English", "US"),
    ("ko", "Korean", "KR"),
    ("ja", "Japanese", "JP"),
    ("zh", "Chinese", "CN"),
    ("fr", "French", "FR"),
    ("es", "Spanish", "ES"),
]


movies = []
tv_shows = []


# =========================================================
# STEP 1: COLLECT MOVIES
# =========================================================

print("\n")
print("=" * 70)
print("CINESPHERE MOVIE COLLECTION")
print("=" * 70)


for language_code, language_name, country_code in MOVIE_SOURCES:

    print(
        f"\nCollecting {language_name} movies..."
    )

    for page in range(1, 21):

        print(
            f"  Page {page}/5"
        )

        params = {
            "api_key": API_KEY,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": page,
            "with_original_language": language_code,
            "with_origin_country": country_code
        }

        data = tmdb_get(
            "discover/movie",
            params
        )

        if not data:
            continue

        for movie in data.get(
            "results",
            []
        ):

            movies.append({

                "content_id":
                    movie.get("id"),

                "content_type":
                    "movie",

                "title":
                    movie.get("title"),

                "overview":
                    movie.get("overview"),

                "release_date":
                    movie.get("release_date"),

                "rating":
                    movie.get("vote_average"),

                "vote_count":
                    movie.get("vote_count"),

                "popularity":
                    movie.get("popularity"),

                "language":
                    movie.get(
                        "original_language"
                    ),

                "language_name":
                    language_name,

                "country":
                    country_code,

                "poster_path":
                    movie.get("poster_path"),

                "backdrop_path":
                    movie.get("backdrop_path")
            })

        time.sleep(0.15)


# =========================================================
# STEP 2: COLLECT TV / WEB SERIES
# =========================================================

print("\n")
print("=" * 70)
print("CINESPHERE TV / WEB SERIES COLLECTION")
print("=" * 70)


for language_code, language_name, country_code in MOVIE_SOURCES:

    print(
        f"\nCollecting {language_name} series..."
    )

    for page in range(1, 11):

        print(
            f"  Page {page}/3"
        )

        params = {
            "api_key": API_KEY,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": page,
            "with_original_language": language_code,
            "with_origin_country": country_code
        }

        data = tmdb_get(
            "discover/tv",
            params
        )

        if not data:
            continue

        for show in data.get(
            "results",
            []
        ):

            tv_shows.append({

                "content_id":
                    show.get("id"),

                "content_type":
                    "tv",

                "title":
                    show.get("name"),

                "overview":
                    show.get("overview"),

                "release_date":
                    show.get("first_air_date"),

                "rating":
                    show.get("vote_average"),

                "vote_count":
                    show.get("vote_count"),

                "popularity":
                    show.get("popularity"),

                "language":
                    show.get(
                        "original_language"
                    ),

                "language_name":
                    language_name,

                "country":
                    country_code,

                "poster_path":
                    show.get("poster_path"),

                "backdrop_path":
                    show.get("backdrop_path")
            })

        time.sleep(0.15)


# =========================================================
# STEP 3: COMBINE CATALOG + EXISTING DATA
# =========================================================

print("\n")
print("=" * 70)
print("COMBINING CATALOG")
print("=" * 70)


# ---------------------------------------------------------
# NEW DATA COLLECTED FROM TMDB
# ---------------------------------------------------------

new_catalog = pd.DataFrame(
    movies + tv_shows
)


# Remove duplicates inside the newly collected data
new_catalog = new_catalog.drop_duplicates(
    subset=[
        "content_type",
        "content_id"
    ]
).reset_index(drop=True)


print(
    f"New unique TMDB items: "
    f"{len(new_catalog)}"
)


# ---------------------------------------------------------
# LOAD EXISTING CATALOG
# ---------------------------------------------------------

if os.path.exists(OUTPUT_FILE):

    print(
        f"\nExisting catalog found: "
        f"{OUTPUT_FILE}"
    )

    existing_catalog = pd.read_csv(
        OUTPUT_FILE
    )

    print(
        f"Existing catalog items: "
        f"{len(existing_catalog)}"
    )

else:

    print(
        "\nNo existing catalog found. "
        "Creating a new catalog."
    )

    existing_catalog = pd.DataFrame()


# ---------------------------------------------------------
# MERGE EXISTING + NEW
# ---------------------------------------------------------

if not existing_catalog.empty:

    combined_catalog = pd.concat(
        [
            existing_catalog,
            new_catalog
        ],
        ignore_index=True
    )

else:

    combined_catalog = new_catalog.copy()


# ---------------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------------

before_dedup = len(
    combined_catalog
)


combined_catalog = combined_catalog.drop_duplicates(
    subset=[
        "content_type",
        "content_id"
    ],
    keep="first"
).reset_index(drop=True)


duplicates_removed = (
    before_dedup
    - len(combined_catalog)
)


print(
    f"Duplicates skipped: "
    f"{duplicates_removed}"
)


print(
    f"Total catalog after merge: "
    f"{len(combined_catalog)}"
)


# ---------------------------------------------------------
# IMPORTANT
# ---------------------------------------------------------
# Only NEW items need detailed TMDB API requests.
#
# Existing items already contain:
# genres
# keywords
# cast
# director
# runtime
#
# So we will process only records that are not already
# present in the existing catalog.
# ---------------------------------------------------------

if not existing_catalog.empty:

    existing_keys = set(
        zip(
            existing_catalog["content_type"],
            existing_catalog["content_id"]
        )
    )

    basic_catalog = combined_catalog[
        combined_catalog.apply(
            lambda row:
                (
                    row["content_type"],
                    row["content_id"]
                ) not in existing_keys,
            axis=1
        )
    ].reset_index(drop=True)

else:

    basic_catalog = combined_catalog.copy()


print(
    f"New items requiring details: "
    f"{len(basic_catalog)}"
)

# =========================================================
# STEP 4: FETCH DETAILS
# =========================================================

detailed_catalog = []


for i, item in basic_catalog.iterrows():

    content_id = item["content_id"]

    title = item["title"]

    content_type = item["content_type"]


    print(
        f"\nDetails "
        f"{i + 1}/{len(basic_catalog)}: "
        f"{title}"
    )


    if content_type == "movie":

        endpoint = f"movie/{content_id}"

    else:

        endpoint = f"tv/{content_id}"


    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "append_to_response":
            "credits,keywords"
    }


    data = tmdb_get(
        endpoint,
        params
    )


    if not data:

        detailed_catalog.append({

            **item.to_dict(),

            "genres": "",
            "keywords": "",
            "cast": "",
            "director": "",
            "runtime": None

        })

        continue


    # -----------------------------------------------------
    # GENRES
    # -----------------------------------------------------

    genres = [
        genre.get("name", "")
        for genre in data.get(
            "genres",
            []
        )
    ]


    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    keywords_data = data.get(
        "keywords",
        {}
    )


    if content_type == "movie":

        keyword_list = keywords_data.get(
            "keywords",
            []
        )

    else:

        keyword_list = keywords_data.get(
            "results",
            []
        )


    keywords = [
        keyword.get("name", "")
        for keyword in keyword_list
    ]


    # -----------------------------------------------------
    # CAST
    # -----------------------------------------------------

    credits = data.get(
        "credits",
        {}
    )


    cast_data = credits.get(
        "cast",
        []
    )


    cast = [
        person.get("name", "")
        for person in cast_data[:8]
    ]


    # -----------------------------------------------------
    # DIRECTOR / CREATOR
    # -----------------------------------------------------

    director = ""


    if content_type == "movie":

        crew = credits.get(
            "crew",
            []
        )

        directors = [
            person.get("name", "")
            for person in crew
            if person.get("job") == "Director"
        ]

        if directors:

            director = directors[0]

    else:

        creators = data.get(
            "created_by",
            []
        )

        if creators:

            director = creators[0].get(
                "name",
                ""
            )


    # -----------------------------------------------------
    # RUNTIME
    # -----------------------------------------------------

    if content_type == "movie":

        runtime = data.get(
            "runtime"
        )

    else:

        episode_runtime = data.get(
            "episode_run_time",
            []
        )

        runtime = (
            episode_runtime[0]
            if episode_runtime
            else None
        )


    # -----------------------------------------------------
    # SAVE DETAIL
    # -----------------------------------------------------

    detailed_catalog.append({

        **item.to_dict(),

        "genres":
            ", ".join(genres),

        "keywords":
            ", ".join(keywords),

        "cast":
            ", ".join(cast),

        "director":
            director,

        "runtime":
            runtime

    })


    time.sleep(0.1)


# =========================================================
# STEP 5: FINAL DATASET
# =========================================================

new_detailed_df = pd.DataFrame(
    detailed_catalog
)


# ---------------------------------------------------------
# COMBINE EXISTING + NEW DETAILED RECORDS
# ---------------------------------------------------------

if not existing_catalog.empty:

    final_df = pd.concat(
        [
            existing_catalog,
            new_detailed_df
        ],
        ignore_index=True
    )

else:

    final_df = new_detailed_df.copy()


# ---------------------------------------------------------
# FINAL DUPLICATE PROTECTION
# ---------------------------------------------------------

final_df = final_df.drop_duplicates(
    subset=[
        "content_type",
        "content_id"
    ],
    keep="first"
).reset_index(drop=True)


print(
    f"\nFinal unique catalog items: "
    f"{len(final_df)}"
)


# =========================================================
# STEP 6: CREATE DATA FOLDER
# =========================================================

os.makedirs(
    "data",
    exist_ok=True
)


# =========================================================
# STEP 7: SAVE
# =========================================================

final_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)


# =========================================================
# STEP 8: SUMMARY
# =========================================================

print("\n")
print("=" * 70)
print("CINESPHERE CATALOG COLLECTION COMPLETE")
print("=" * 70)


print(
    f"Total catalog items: "
    f"{len(final_df)}"
)


print(
    f"Movies: "
    f"{len(final_df[final_df['content_type'] == 'movie'])}"
)


print(
    f"TV / Web Series: "
    f"{len(final_df[final_df['content_type'] == 'tv'])}"
)


print(
    f"Dataset saved to: "
    f"{OUTPUT_FILE}"
)


print("\nColumns:")

print(
    final_df.columns.tolist()
)


print("\nContent types:")

print(
    final_df["content_type"]
    .value_counts()
)


print("\nLanguages:")

print(
    final_df["language_name"]
    .value_counts()
)


print("\nSample:")

print(
    final_df[
        [
            "content_id",
            "content_type",
            "title",
            "language_name",
            "country",
            "genres",
            "rating"
        ]
    ].head(10)
)


print("\nDone! ✅")