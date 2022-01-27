from flask import Flask, render_template, url_for, request

# NLP pkgs
import spacy
from spacy import displacy
nlp = spacy.load('en_core_web_sm')

from flaskext.markdown import Markdown

# init app
app = Flask(__name__)
Markdown(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['GET','POST'])
def extract():
    if request.method == 'POST':
        rawtext = request.form["rawtext"]
        doc = nlp(rawtext)
        result = displacy.render(doc, style='ent')
    return render_template('results.html',rawtext=rawtext, result=result)

if __name__ == '__main__':
    app.run(debug=True)