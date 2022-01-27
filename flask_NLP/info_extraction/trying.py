import spacy

nlp = spacy.load("en_core_web_sm")
def fine_tune_sents(paragraph):
    doc = nlp("I. Introduction")
    new_paragraph = ""
    for sent in doc.sents:
        if sent[0].is_title and sent[-1].is_punct:
            has_noun = 2
            has_verb = 1
            for token in sent:
                if token.pos_ in ["NOUN", "PROPN", "PRON"]:
                    has_noun -= 1
                elif token.pos_ == "VERB":
                    has_verb -= 1
            if has_noun < 1 and has_verb < 1:
                added_sent = "\n "+str(sent)
                new_paragraph.append(added_sent)
    return new_paragraph