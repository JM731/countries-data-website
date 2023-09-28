from flask import Flask, render_template, redirect, url_for, request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import requests
import os

URL = "https://restcountries.com/v3.1/"
CATEGORY = ["Name", "Full Name", "Code", "Currency", "Demonym", "Language",
            "Capital City", "Region", "Subregion", "Translation Name"]


def build_search_url(term: str, category: str):
    params = {}
    if category == "Full Name":
        category = "name"
        params["fullText"] = "true"
    elif category == "Code":
        category = "alpha"
    elif category == "Language":
        category = "lang"
    elif category == "Capital City":
        category = "capital"
    elif category == "Translation Name":
        category = "translation"
    else:
        category = category.lower()
    url = URL + category + "/" + term
    params["fields"] = "name,flags"
    return url, params


def check_not_found(data):
    if isinstance(data, dict) and 'status' in data and data['status'] == 404:
        return True
    return False


def get_data(url, params=None):
    response = requests.get(url, params=params)
    data = response.json()
    return data


class SearchForm(FlaskForm):
    search_term = StringField(validators=[DataRequired()],
                              render_kw={"placeholder": "Search for countries by..."})
    category = SelectField(choices=CATEGORY)
    submit = SubmitField("Search")


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


@app.route('/', methods=["GET", "POST"])
def home():
    search_form = SearchForm(csrf_enabled=False)
    if search_form.validate_on_submit():
        search_term = search_form.search_term.data
        category = search_form.category.data
        return redirect(url_for('search', search_term=search_term, category=category))
    return render_template("index.html", form=search_form)


@app.route('/search', methods=["GET", "POST"])
def search():
    search_form = SearchForm(csrf_enabled=False)
    if search_form.validate_on_submit():
        search_term = search_form.search_term.data
        category = search_form.category.data
        return redirect(url_for('search', search_term=search_term, category=category))
    search_term = request.args.get("search_term", "")
    category = request.args.get("category", "Name").title()
    if not search_term or category not in CATEGORY:
        data = []
    else:
        url, params = build_search_url(search_term, category)
        data = get_data(url, params)
        if check_not_found(data):
            data = []
        else:
            data = sorted(data, key=lambda x: x['name']['common'])
    return render_template('search.html', form=search_form, data=data, search_term=search_term, category=category)


@app.route('/country/<string:name>')
def country(name: str):
    url = URL + "name/" + name
    data = get_data(url)[0]
    if check_not_found(data):
        abort(404)
    else:
        return render_template('country.html', data=data)


if __name__ == "__main__":
    app.run()
