"""
Matnli javoblarni TF-IDF + K-Means yordamida kategoriyalarga ajratadi.
Internetga ulanish yoki API kerak emas — to'liq lokal ishlaydi.
"""
import re
from collections import Counter


def _clean(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    text = re.sub(r'\s+', ' ', text)
    return text


def categorize_text_answers(question_text: str, answers: list) -> list:
    """
    Matnli javoblarni klasterlarga ajratadi.
    Qaytaradi: [{'category': '...', 'count': N, 'percent': X.X, 'examples': [...]}]
    """
    answers = [a for a in answers if a and str(a).strip()]
    if not answers:
        return []

    n = len(answers)

    # Kamida 3 ta javob bo'lmasa, klasterlash shart emas
    if n < 3:
        return [{
            'category': 'Barcha javoblar',
            'count': n,
            'percent': 100.0,
            'examples': answers[:2],
        }]

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans
        import numpy as np

        cleaned = [_clean(a) for a in answers]

        # Klaster soni: 3 dan 6 gacha (javob soniga qarab)
        n_clusters = min(6, max(3, n // 5))

        vectorizer = TfidfVectorizer(
            max_features=200,
            min_df=1,
            analyzer='char_wb',  # har qanday tilda ishlaydi (lotin, kirill, o'zbek)
            ngram_range=(3, 5),
        )
        X = vectorizer.fit_transform(cleaned)

        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(X)

        # Har bir klaster uchun eng ko'p uchraydigan so'zlar asosida nom yasash
        feature_names = vectorizer.get_feature_names_out()
        categories = []

        for cluster_id in range(n_clusters):
            cluster_indices = [i for i, l in enumerate(labels) if l == cluster_id]
            if not cluster_indices:
                continue

            count = len(cluster_indices)
            percent = round(count / n * 100, 1)

            # Klaster markazi asosida kalit so'zlar
            center = km.cluster_centers_[cluster_id]
            top_indices = np.argsort(center)[::-1][:5]
            keywords = [feature_names[i] for i in top_indices if len(feature_names[i]) > 3]

            # Klaster nomi: birinchi namunaviy javobdan qisqa nom
            examples = [answers[i] for i in cluster_indices[:3]]
            # Eng qisqa javobni nom sifatida ol (lekin 60 belgidan oshmasin)
            shortest = min(examples, key=len)
            category_name = shortest[:60] + ('...' if len(shortest) > 60 else '')

            categories.append({
                'category': category_name,
                'count': count,
                'percent': percent,
                'examples': examples[:2],
            })

        # Foiz bo'yicha kamayish tartibida
        categories.sort(key=lambda x: x['percent'], reverse=True)
        return categories

    except Exception as e:
        print(f"Kategoriyalashtirish xatosi: {e}")
        # Fallback: barcha javoblarni bitta kategoriyada ko'rsat
        return [{
            'category': 'Barcha javoblar',
            'count': n,
            'percent': 100.0,
            'examples': answers[:3],
        }]
