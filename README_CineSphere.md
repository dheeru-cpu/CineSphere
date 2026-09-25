# 🎬 CineSphere

### Intelligent Movie Discovery & Recommendation Platform

CineSphere is a movie and web-series discovery platform that I built to explore how Machine Learning can be turned into something people can actually use.

Instead of only showing a list of movies, CineSphere helps users discover content through search, genres, industries, ratings, popularity and — most importantly — content-based recommendations.

The main idea behind the project was simple:

> **Find a movie you like, understand what makes it similar to other movies, and use that information to discover what you might want to watch next.**

---

## ✨ What can CineSphere do?

CineSphere currently provides:

- 🔍 Search for movies and TV/Web Series
- 🎭 Explore content by genre
- 🌍 Browse different industries and languages
- 🔥 Discover trending content
- ⭐ Explore highly rated titles
- 🆕 Find latest releases
- 📖 Open a detailed movie/series information page
- 🧠 Get similar movie/series recommendations
- 🎬 Explore movies from different regions and languages
- 💎 Use everything through a clean, premium Streamlit interface

---

## 🧠 The Machine Learning Behind CineSphere

The main ML part of CineSphere is a **content-based recommendation system**.

The system does not simply recommend random popular movies. It looks at information about a movie and compares it with other titles in the catalog.

For each title, CineSphere uses information such as:

- Genres
- Keywords
- Cast
- Director / Creator
- Language
- Overview

These details are combined into a single text representation.

For example:

```text
Genres + Keywords + Cast + Director + Language + Overview
```

That combined information is then converted into numerical vectors using **TF-IDF**.

After that, **Cosine Similarity** is used to measure how similar two titles are.

The recommendation system then combines content similarity with signals such as rating, vote count and popularity to rank the final recommendations.

---

## 🔄 How the recommendation system works

The complete flow is:

```text
Movie / Series Metadata
        ↓
Data Cleaning
        ↓
Feature Combination
        ↓
TF-IDF Vectorization
        ↓
Cosine Similarity
        ↓
Similar Content
        ↓
Ranking
        ↓
Recommendations
```

This was the main Machine Learning concept I wanted to implement in the project rather than using a simple hard-coded recommendation list.

---

## 📊 Catalog

The current CineSphere catalog contains:

- **8,492 total records**
- **5,973 movies**
- **2,519 TV/Web Series**

The catalog covers multiple languages and regions, including:

- Hindi
- Telugu
- Tamil
- Malayalam
- Kannada
- Bengali
- Marathi
- Punjabi
- Gujarati
- English
- Korean
- Japanese
- Chinese
- French
- Spanish

Movie and TV metadata is collected using the **TMDB API** for this educational project.

---

## 📈 Recommendation System Evaluation

I also tested the recommendation engine on a sample of **20 catalog items**.

The recorded evaluation produced:

| Metric | Result |
|---|---:|
| Successful recommendation tests | 20 / 20 |
| Average recommendations returned | 5 |
| Average cosine similarity | 0.259 |
| Minimum cosine similarity | 0.105 |
| Maximum cosine similarity | 0.675 |

These numbers describe the behavior of the recommendation system on the tested catalog. They should not be interpreted as classification accuracy, because this is a content-based recommendation system rather than a supervised classification problem.

---

## 🖥️ Application Flow

A simplified view of CineSphere is:

```text
                TMDB API
                   ↓
          Data Collection
                   ↓
       Data Enrichment / Repair
                   ↓
          CineSphere Catalog
                   ↓
       Recommendation Model
                   ↓
        Streamlit Application
                   ↓
     ┌─────────────┼─────────────┐
     ↓             ↓             ↓
   Search        Filters    Recommendations
     │             │             │
     └─────────────┼─────────────┘
                   ↓
             Movie Details
```

---

## 🛠️ Tech Stack

### Programming
- Python

### Machine Learning
- Scikit-learn
- TF-IDF
- Cosine Similarity
- Pandas
- Joblib

### Application
- Streamlit

### Data
- TMDB API

### Development
- Python Virtual Environment
- Git / GitHub

---

## 📁 Project Structure

```text
CineSphere/
│
├── app.py
├── collect_movies.py
├── repair_catalog.py
├── add_classics.py
├── build_catalog_model.py
├── catalog_recommendation_engine.py
├── evaluate_recommendations.py
│
├── data/
│   ├── catalog_enriched_final.csv
│   └── ...
│
├── models/
│   ├── catalog_tfidf_vectorizer.pkl
│   ├── catalog_similarity_matrix.pkl
│   └── catalog_processed.csv
│
├── .env
├── .gitignore
└── README.md
```

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CineSphere
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it on Windows

```powershell
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install streamlit pandas scikit-learn joblib requests python-dotenv
```

### 5. Add your TMDB API key

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_tmdb_api_key
```

Keep the `.env` file private and never upload it to GitHub.

### 6. Run CineSphere

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🎯 Why I Built This Project

I built CineSphere as an **ML-focused project**, not just as a movie UI.

While working on it, I wanted to understand the complete journey of an ML-based application:

```text
Collect Data
     ↓
Clean & Prepare Data
     ↓
Create Features
     ↓
Build ML Model
     ↓
Generate Recommendations
     ↓
Evaluate the System
     ↓
Connect ML with a Web App
```

This made the project a practical way for me to work with Python, data processing, NLP-style text features, machine learning and application development together.

---

## 🚧 Current Scope

The current version intentionally focuses on the core recommendation and discovery experience.

Features such as:

- User accounts
- Personalized watch history
- Collaborative filtering
- User-specific recommendations
- Watchlists
- Real-time recommendation updates

are not part of the current version.

They can be explored later if the project is expanded.

---

## 🔮 Future Improvements

If I continue developing CineSphere, some possible improvements would be:

- Hybrid recommendation using content + collaborative filtering
- Personalized recommendations
- User watch history
- Recommendation feedback
- Better ranking models
- Automated catalog updates
- Cloud deployment
- More advanced NLP features

---

## 👨‍💻 Author

**Dhiraj Kumar**

B.Tech — Computer Science Engineering  
AI & Data Science

CineSphere was developed as an educational and internship-focused Machine Learning project.

---

## 📌 Data & Project Note

CineSphere uses movie and TV metadata provided through the **TMDB API**.

This project is intended for educational, learning and demonstration purposes.
