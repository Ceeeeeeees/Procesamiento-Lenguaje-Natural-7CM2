#Importamos la biblioteca spacy
import spacy
from spacy import displacy
#conda install -c conda-forge spacy-model-en_core_web_sm
#python -m spacy download en_core_web_sm

cadena = "Understanding the Limits of Lifelong Knowledge Editing in LLMs"


#Se carga el corpus para el tagger en español
nlp = spacy.load("en_core_web_sm")
#Se realiza el análisis de la cadena
doc = nlp(cadena)


for token in doc:
    print(token.text, token.pos_, token.lemma_)
    # ~ print(token.text, token.pos_, token.dep_, token.lemma_)
    # ~ print(token.text, token.pos_, token.dep_, token.lemma_, spacy.explain(token.tag_), spacy.explain(token.dep_))
# ~ displacy.serve(doc, style="dep")    

# ~ for entity in doc.ents:
    # ~ print(entity.text, entity.label_)