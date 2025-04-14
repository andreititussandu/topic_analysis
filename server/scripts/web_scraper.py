"""
Utilități pentru extragerea textului din pagini web pentru aplicația de analiză a topicurilor
"""
import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
from .preprocess import preprocess_text

def scrape_text_from_url(url, timeout = 60):
    """
    Extrage textul dintr-un URL
    
    Args:
        url: URL-ul de la care se extrage textul
        timeout: Timpul maxim de așteptare în secunde
        
    Returns:
        Textul prelucrat extras din URL
    """
    try:
        response = requests.get(url, timeout=timeout)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        return preprocess_text(text)
    except Timeout:
        print(f"Timeout apărut în timpul încercării de a extrage {url}")
        return ''