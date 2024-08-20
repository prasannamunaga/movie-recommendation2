from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel

app = Flask(__name__)

# Global variables for datasets and models
credits = None
movies = None
movies_cleaned = None
tfv_matrix = None
tfv = None
sig = None
indices = None

# Load datasets
def load_data():
    global credits, movies
    try:
        credits = pd.read_csv("tmdb_5000_credits.csv", encoding='ISO-8859-1')
        movies = pd.read_csv("tmdb_5000_movies.csv", encoding='ISO-8859-1')
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")


# Data preprocessing
def preprocess_data():
    global movies_cleaned
    try:
        if credits is None or movies is None:
            raise ValueError("Data not loaded properly.")
        
        credits_renamed = credits.rename(columns={"movie_id": "id"})
        merged_data = movies.merge(credits_renamed, on='id')
        cleaned_data = merged_data.drop(columns=['homepage', 'title_x', 'title_y', 'status', 'production_countries'])
        cleaned_data['overview'] = cleaned_data['overview'].fillna('')
        movies_cleaned = cleaned_data
        print("Data preprocessing completed.")
    except Exception as e:
        print(f"Error in data preprocessing: {e}")

# TF-IDF Vectorization
def compute_tfidf():
    global tfv_matrix, tfv
    try:
        if movies_cleaned is None:
            raise ValueError("Data not preprocessed properly.")
        
        tfv = TfidfVectorizer(min_df=3, max_features=None, strip_accents='unicode',
                              analyzer='word', token_pattern=r'\w{1,}', ngram_range=(1, 3), stop_words='english')
        tfv_matrix = tfv.fit_transform(movies_cleaned['overview'])
        print("TF-IDF computation completed.")
    except Exception as e:
        print(f"Error in TF-IDF computation: {e}")


# Compute the sigmoid kernel
def compute_sigmoid_kernel():
    global sig
    try:
        if tfv_matrix is None:
            raise ValueError("TF-IDF matrix not computed properly.")
        
        sig = sigmoid_kernel(tfv_matrix, tfv_matrix)
        print("Sigmoid kernel computation completed.")
    except Exception as e:
        print(f"Error in sigmoid kernel computation: {e}")

# Reverse mapping of indices and movie titles
def create_indices():
    global indices
    try:
        if movies_cleaned is None:
            raise ValueError("Data not preprocessed properly.")
        
        indices = pd.Series(movies_cleaned.index, index=movies_cleaned['original_title']).drop_duplicates()
        print("Indices created.")
    except Exception as e:
        print(f"Error in creating indices: {e}")

# Recommendation function
def give_recommendations(title):
    try:
        if title not in indices:
            return [{"original_title": "Movie not found", "overview": ""}]
        
        idx = indices[title]
        sig_scores = list(enumerate(sig[idx]))
        sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
        sig_scores = sig_scores[1:11]  # Exclude the input movie itself
        movie_indices = [i[0] for i in sig_scores]
        
        recommendations = movies_cleaned.iloc[movie_indices]
        return recommendations[['original_title', 'overview']].to_dict(orient='records')
    except Exception as e:
        print(f"Error in recommendation function: {e}")
        return [{"original_title": "Error occurred", "overview": ""}]
# Initialize data
def initialize():
    load_data()
    preprocess_data()
    compute_tfidf()
    compute_sigmoid_kernel()
    create_indices()

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to get recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        title = request.form['title']
        recommendations = give_recommendations(title)
        return jsonify(recommendations)
    except Exception as e:
        print(f"Error in /recommend route: {e}")
        return jsonify([{"original_title": "Error occurred", "overview": ""}])

if __name__ == '__main__':
    initialize()
    app.run(debug=True)
