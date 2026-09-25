import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz


# -----------------------------
# PATHS
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "catalog_enriched_final.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# -----------------------------
# LOAD DATASET
# -----------------------------

print("Loading CineSphere catalog...")

df = pd.read_csv(DATA_PATH)

print(f"Total records loaded: {len(df)}")


# -----------------------------
# CLEAN TEXT FEATURES
# -----------------------------

text_columns = [
    "overview",
    "genres",
    "keywords",
    "cast",
    "director",
    "language_name"
]

for column in text_columns:
    df[column] = df[column].fillna("").astype(str)


# -----------------------------
# COMBINED FEATURES
# -----------------------------

df["combined_features"] = (
    df["genres"] + " " +
    df["keywords"] + " " +
    df["cast"] + " " +
    df["director"] + " " +
    df["language_name"] + " " +
    df["overview"]
)


# -----------------------------
# TF-IDF
# -----------------------------

print("Building TF-IDF matrix...")

tfidf = TfidfVectorizer(
    stop_words="english",
    max_features=15000,
    ngram_range=(1, 2)
)

tfidf_matrix = tfidf.fit_transform(
    df["combined_features"]
)

print(
    f"TF-IDF matrix shape: {tfidf_matrix.shape}"
)


# -----------------------------
# SAVE MODEL
# -----------------------------

tfidf_path = os.path.join(
    MODEL_DIR,
    "catalog_tfidf_vectorizer.pkl"
)

tfidf_matrix_path = os.path.join(
    MODEL_DIR,
    "catalog_tfidf_matrix.npz"
)

processed_path = os.path.join(
    MODEL_DIR,
    "catalog_processed.csv"
)


# Save TF-IDF vectorizer

joblib.dump(
    tfidf,
    tfidf_path
)


# Save sparse TF-IDF matrix

save_npz(
    tfidf_matrix_path,
    tfidf_matrix
)


# Save processed catalog

df.to_csv(
    processed_path,
    index=False,
    encoding="utf-8"
)


# -----------------------------
# COMPLETE
# -----------------------------

print("\n" + "=" * 50)
print("CINESPHERE CATALOG ML MODEL COMPLETE")
print("=" * 50)

print(f"Records: {len(df)}")
print(f"TF-IDF features: {len(tfidf.vocabulary_)}")
print(f"TF-IDF matrix: {tfidf_matrix.shape}")

print("\nSaved files:")

print(tfidf_path)
print(tfidf_matrix_path)
print(processed_path)