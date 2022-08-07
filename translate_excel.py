from flask import Blueprint, jsonify

from styleframe import StyleFrame, tests

translate_API = Blueprint('translate_API', __name__, template_folder='templates')

@translate_API.route('/translate/', methods=['GET'])
def translate_respond():
  response = {}
  response["TEST"] = translate()
  return jsonify(response)


def translate():
  sf = StyleFrame.read_excel('example\SPRINT_eng.xlsx', read_style=True)
  print(sf)
  return "..."