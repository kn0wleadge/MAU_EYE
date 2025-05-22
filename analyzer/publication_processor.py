from .sentiment_analyze import predict
from database.models import Publication
import logging
import re

def check_university_mentions(text:str):
    pattern = r'''(?ix)  # i: ignore case, x: allow comments and whitespace
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

def get_assesment(publications:list):
    p
    analyzed_publications = []
    for publication in publications:
        analyzed_publication = {"url" : None, 
                                "assesment" : None}
        predict = predict(publication["ptext"])
        analyzed_publication["url"] = publication["url"]
        analyzed_publication["assesment"] = predict
    return analyzed_publications