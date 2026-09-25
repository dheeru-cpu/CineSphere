import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(
    DATA_DIR,
    "catalog_enriched.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "catalog_enriched_repaired.csv"
)

load_dotenv(
    os.path.join(BASE_DIR, ".env")
)

API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    raise ValueError(
        "TMDB_API_KEY not found in .env"
    )

BASE_URL = "https://api.themoviedb.org/3"


# =========================================================
# LOAD CATALOG
# =========================================================

print("=" * 70)
print("CINESPHERE CATALOG REPAIR")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

print(
    f"\nCatalog loaded: {len(df)} items"
)


# =========================================================
# TMDB REQUEST WITH RETRIES
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

    for attempt in range(1, retries + 1):

        try:

            response = requests.get(
                url,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()

            print(
                f"  HTTP {response.status_code} "
                f"(attempt {attempt}/{retries})"
            )

        except requests.RequestException as error:

            print(
                f"  Network error "
                f"(attempt {attempt}/{retries}): "
                f"{error}"
            )

        if attempt < retries:
            wait_time = attempt * 3

            print(
                f"  Retrying in "
                f"{wait_time}s..."
            )

            time.sleep(wait_time)

    return None


# =========================================================
# FIND RECORDS NEEDING REPAIR
# =========================================================

repair_mask = (
    df["genres"].fillna("").astype(str).str.strip().eq("")
    |
    df["cast"].fillna("").astype(str).str.strip().eq("")
    |
    df["director"].fillna("").astype(str).str.strip().eq("")
)

repair_indexes = df.index[repair_mask].tolist()

print(
    f"\nRecords needing repair: "
    f"{len(repair_indexes)}"
)

print(
    "\nRepair will update:"
)
print("  - genres")
print("  - keywords")
print("  - cast")
print("  - director")
print("  - runtime")


# =========================================================
# BACKUP CURRENT DATA
# =========================================================

backup_file = os.path.join(
    DATA_DIR,
    "catalog_enriched_before_repair.csv"
)

if not os.path.exists(backup_file):

    df.to_csv(
        backup_file,
        index=False,
        encoding="utf-8"
    )

    print(
        f"\nBackup created:\n"
        f"{backup_file}"
    )

else:

    print(
        "\nBackup already exists. "
        "Keeping existing backup."
    )


# =========================================================
# REPAIR LOOP
# =========================================================

successful = 0
failed = 0

total = len(repair_indexes)

for position, index in enumerate(
    repair_indexes,
    start=1
):

    row = df.loc[index]

    content_id = int(
        row["content_id"]
    )

    content_type = str(
        row["content_type"]
    ).lower().strip()

    title = str(
        row["title"]
    )

    print(
        f"\n[{position}/{total}] "
        f"{title}"
    )

    if content_type == "movie":
        endpoint = f"/movie/{content_id}"
    else:
        endpoint = f"/tv/{content_id}"

    data = tmdb_get(
        endpoint,
        params={
            "language": "en-US",
            "append_to_response": "credits,keywords"
        }
    )

    if not data:

        print(
            "  FAILED - keeping existing data"
        )

        failed += 1

        continue


    # =====================================================
    # GENRES
    # =====================================================

    genres = data.get(
        "genres",
        []
    )

    genre_names = [
        str(g.get("name", "")).strip()
        for g in genres
        if g.get("name")
    ]

    genres_text = ", ".join(
        genre_names
    )


    # =====================================================
    # KEYWORDS
    # =====================================================

    keyword_data = data.get(
        "keywords",
        {}
    )

    keyword_list = keyword_data.get(
        "keywords",
        []
    )

    if content_type == "tv":

        keyword_list = keyword_data.get(
            "results",
            []
        )

    keyword_names = [
        str(k.get("name", "")).strip()
        for k in keyword_list
        if k.get("name")
    ]

    keywords_text = ", ".join(
        keyword_names
    )


    # =====================================================
    # CAST
    # =====================================================

    credits = data.get(
        "credits",
        {}
    )

    cast_list = credits.get(
        "cast",
        []
    )

    cast_names = [
        str(person.get("name", "")).strip()
        for person in cast_list[:8]
        if person.get("name")
    ]

    cast_text = ", ".join(
        cast_names
    )


    # =====================================================
    # DIRECTOR / CREATOR
    # =====================================================

    director_text = ""

    if content_type == "movie":

        crew = credits.get(
            "crew",
            []
        )

        directors = [
            str(person.get("name", "")).strip()
            for person in crew
            if person.get("job") == "Director"
            and person.get("name")
        ]

        director_text = ", ".join(
            directors[:3]
        )

    else:

        creators = data.get(
            "created_by",
            []
        )

        creator_names = [
            str(person.get("name", "")).strip()
            for person in creators
            if person.get("name")
        ]

        director_text = ", ".join(
            creator_names[:3]
        )


    # =====================================================
    # RUNTIME
    # =====================================================

    if content_type == "movie":

        runtime = data.get(
            "runtime"
        )

    else:

        episode_runtimes = data.get(
            "episode_run_time",
            []
        )

        if episode_runtimes:

            runtime = episode_runtimes[0]

        else:

            runtime = None


    # =====================================================
    # UPDATE ONLY AVAILABLE DATA
    # =====================================================

    if genres_text:
        df.at[
            index,
            "genres"
        ] = genres_text

    if keywords_text:
        df.at[
            index,
            "keywords"
        ] = keywords_text

    if cast_text:
        df.at[
            index,
            "cast"
        ] = cast_text

    if director_text:
        df.at[
            index,
            "director"
        ] = director_text

    if runtime is not None:
        df.at[
            index,
            "runtime"
        ] = runtime

    successful += 1

    print("  ✓ Repaired")

    # Small delay to reduce API pressure
    time.sleep(0.25)


# =========================================================
# SAVE REPAIRED CATALOG
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print(
    "\n" + "=" * 70
)

print(
    "REPAIR COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Total records: {len(df)}"
)

print(
    f"Successfully processed: {successful}"
)

print(
    f"Failed requests: {failed}"
)

print(
    f"\nSaved repaired catalog:"
)

print(
    OUTPUT_FILE
)


# =========================================================
# FINAL QUALITY CHECK
# =========================================================

print(
    "\n" + "-" * 70
)

print(
    "QUALITY CHECK"
)

print(
    "-" * 70
)

print(
    "Missing genres:",
    df["genres"].fillna("").eq("").sum()
)

print(
    "Missing keywords:",
    df["keywords"].fillna("").eq("").sum()
)

print(
    "Missing cast:",
    df["cast"].fillna("").eq("").sum()
)

print(
    "Missing director:",
    df["director"].fillna("").eq("").sum()
)