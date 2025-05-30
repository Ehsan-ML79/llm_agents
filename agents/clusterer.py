from typing import List, Dict
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def cluster_jobs(jobs: List[Dict], n_clusters: int = 3) -> Dict[int, List[Dict]]:
    """
    Cluster job postings into n_clusters based on their description using TF-IDF + KMeans.
    Returns a dict mapping cluster_id -> list of job dicts.
    """
    descriptions = [job["snippet"] for job in jobs]
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(descriptions)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)

    clusters = {i: [] for i in range(n_clusters)}
    for job, label in zip(jobs, labels):
        clusters[label].append(job)
    return clusters