import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk

def create_inverted_index(jobs):
    inverted_index = {}
    for job in jobs:
        job_skills = job.skills.split(',') 
        for skill in job_skills:
            skill = skill.strip().lower()
            if skill not in inverted_index:
                inverted_index[skill] = set()
            inverted_index[skill].add(job.job_id)  # Use job.job_id instead of job.id
    return inverted_index


# def download_nltk_data():
#     try:
#         # Check if data is available, will raise an exception if not found
#         nltk.data.find('tokenizers/punkt')
#         nltk.data.find('corpora/wordnet')
#         nltk.data.find('corpora/stopwords')
#     except LookupError:
#         # Data not found, proceed with download
#         nltk.download('punkt')
#         nltk.download('wordnet')
#         nltk.download('stopwords')

def prepro(text):
    # Convert text to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove stopwords
    stop_words = set(nltk.corpus.stopwords.words('english'))
    words = word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    
    # Combine words back to string
    preprocessed_text = ' '.join(lemmatized_words)
    
    return preprocessed_text

def refine_mbti_with_baseline(initial_mbti, predictions, confidences, thresholds):
    refined_mbti = ''
    dimensions = ['I-E', 'N-S', 'T-F', 'J-P']

    for i, dimension in enumerate(dimensions):
        if confidences[dimension] < thresholds[dimension]:
            refined_mbti += initial_mbti[i]
        else:
            refined_mbti += predictions[dimension]

    return refined_mbti
