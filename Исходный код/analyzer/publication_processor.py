from .sentiment_analyze import predict
from database.models import Publication
import logging
import re
from typing import Union, List
def check_university_mentions(text:str):
    pattern = r'''(?ix)  
    \b(
        мау |                                      # аббревиатура
        мурманск(ий|ого|ому|им|ом|ом|ие|их|ими)?    # прилагательное "Мурманский" во всех падежах
        \s+
        (
            арктическ(ий|ого|ому|им|ом|ом|ие|их|ими)?\s+)?   # (опционально) "Арктический"
            (
                государствен(ный|ого|ому|ым|ом|ом|ые|ых|ыми)?\s+)?  # (опционально) "Государственный"
            (университет|институт)(е|а|у|ом|ом|ов|ам|ами|ах)?  # существительное
    )\b
    '''
    return re.search(pattern, text) is not None

def check_keyword_mentions(keywords: Union[str, List[str]], text: str) -> bool:
    """
    Проверяет наличие слов и всех их возможных форм в тексте.
    
    Args:
        keywords: Слово или список слов для поиска (в начальной форме)
        text: Текст, в котором осуществляется поиск
    
    Returns:
        bool: True если слова или их формы найдены в тексте (в любом порядке), иначе False
    """
    if isinstance(keywords, str):
        keywords = keywords.split()
    
    # Создаем паттерны для каждого слова
    word_patterns = []
    for word in keywords:
        # Базовый паттерн для слова с возможными окончаниями
        base_pattern = rf'\b{word}[а-я]*\b'
        word_patterns.append(f'(?i:{base_pattern})')
    
    # Комбинируем паттерны - все слова должны присутствовать в любом порядке
    combined_pattern = r'(?i)(?=.*' + r')(?=.*'.join(word_patterns) + r')'
    
    # Проверяем
    return re.search(combined_pattern, text) is not None

def get_assesment(publications:list):
    analyzed_publications = []
    for publication in publications:
        analyzed_publication = {"url" : None, 
                                "assesment" : None}
        predict = predict(publication["ptext"])
        analyzed_publication["url"] = publication["url"]
        analyzed_publication["assesment"] = predict
    return analyzed_publications