import pandas as pd

from catalog_recommendation_engine import (
    df,
    recommend_catalog
)


# ---------------------------------------------------------
# CineSphere ML Recommendation Evaluation
# ---------------------------------------------------------

print("=" * 65)
print("CINESPHERE ML RECOMMENDATION EVALUATION")
print("=" * 65)

print(f"\nTotal catalog records: {len(df)}")

# ---------------------------------------------------------
# Select test items
# ---------------------------------------------------------

test_items = df[
    df["poster_path"].notna()
    & df["title"].notna()
    & (df["rating"] > 0)
].copy()

# Use a fixed sample so evaluation is reproducible
test_items = test_items.sample(
    n=min(20, len(test_items)),
    random_state=42
)

print(f"Test items: {len(test_items)}")


# ---------------------------------------------------------
# Evaluate recommendations
# ---------------------------------------------------------

all_similarity_scores = []
recommendation_counts = []

successful_tests = 0

print("\nRunning recommendation tests...\n")

for _, movie in test_items.iterrows():

    content_id = movie["content_id"]

    recommendations = recommend_catalog(
        content_id,
        num_recommendations=5
    )

    if recommendations.empty:
        continue

    successful_tests += 1

    recommendation_counts.append(
        len(recommendations)
    )

    scores = recommendations[
        "similarity_score"
    ].astype(float)

    all_similarity_scores.extend(
        scores.tolist()
    )


# ---------------------------------------------------------
# Calculate evaluation statistics
# ---------------------------------------------------------

if all_similarity_scores:

    similarity_series = pd.Series(
        all_similarity_scores
    )

    average_similarity = (
        similarity_series.mean()
    )

    minimum_similarity = (
        similarity_series.min()
    )

    maximum_similarity = (
        similarity_series.max()
    )

else:

    average_similarity = 0
    minimum_similarity = 0
    maximum_similarity = 0


average_recommendations = (
    sum(recommendation_counts)
    / len(recommendation_counts)
    if recommendation_counts
    else 0
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print("=" * 65)
print("EVALUATION RESULTS")
print("=" * 65)

print(
    f"\nSuccessful recommendation tests : "
    f"{successful_tests}/{len(test_items)}"
)

print(
    f"Average recommendations returned : "
    f"{average_recommendations:.2f}"
)

print(
    f"Average cosine similarity         : "
    f"{average_similarity:.3f}"
)

print(
    f"Minimum cosine similarity         : "
    f"{minimum_similarity:.3f}"
)

print(
    f"Maximum cosine similarity         : "
    f"{maximum_similarity:.3f}"
)


# ---------------------------------------------------------
# Show sample recommendations
# ---------------------------------------------------------

print("\n" + "=" * 65)
print("SAMPLE RECOMMENDATIONS")
print("=" * 65)

sample_items = test_items.head(5)

for _, movie in sample_items.iterrows():

    print(
        f"\nInput: {movie['title']}"
    )

    recommendations = recommend_catalog(
        movie["content_id"],
        num_recommendations=5
    )

    if recommendations.empty:

        print("  No recommendations found.")
        continue

    for _, recommendation in recommendations.iterrows():

        print(
            f"  → {recommendation['title']} "
            f"| Similarity: "
            f"{recommendation['similarity_score']}"
        )


print("\n" + "=" * 65)
print("ML EVALUATION COMPLETE")
print("=" * 65)