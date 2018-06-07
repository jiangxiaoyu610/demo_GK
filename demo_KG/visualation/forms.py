from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    text = StringField('text', validators=[DataRequired()])
    submit = SubmitField('Search')