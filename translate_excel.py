import deepl
import pandas as pd
from styleframe import StyleFrame
from flask import Blueprint, send_file, request, flash, redirect, after_this_request, jsonify
from dotenv import dotenv_values
from pathlib import Path
import os

config = os.environ
if Path(".env").is_file():
    config = dotenv_values(".env")


translate_API = Blueprint('translate_API', __name__,
                          template_folder='templates')

FILE_IN_PATH = "to_translate.xlsx"
FILE_OUT_PATH = "translated.xlsx"
ALLOWED_EXTENSIONS = {'xlsx'}

translator = deepl.Translator(config["DEEPL_AUTH_KEY"])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@translate_API.route('/upload_sheet', methods=['POST'])
def upload():
    print(request.form['lang'])
    if 'excel-input' not in request.files:
        flash('No file specified.')
        return redirect("/")
    if 'lang' not in request.form or request.form['lang'] == '':
        flash('No language specified.')
        return redirect("/")
    f = request.files['excel-input']
    target_lang = request.form['lang']
    print("TRANSLATING TO: " + target_lang)
    if f.filename == '':
        flash('No output file')
        return redirect("/")
    if f and allowed_file(f.filename):
        f.save(FILE_IN_PATH)
        return translate(FILE_IN_PATH, target_lang)

    @after_this_request
    def remove_files(response):
        print("[CLEANUP] removing files post upload/download pair.")
        try:
            os.remove(FILE_OUT_PATH)
            os.remove(FILE_IN_PATH)
        except Exception as error:
            print(error)
        return response
    # print(f.filename)
    # print(allowed_file(f.filename))
    return {"error": "THE INPUTTED FILE IS INVALID"}, 500


@translate_API.route('/get_langs', methods=['GET'])
def get_langs():
    total_langs = set()
    for language_pair in translator.get_glossary_languages():
        total_langs.add(language_pair.target_lang)
    return jsonify(list(total_langs))


def translate(file_in, target_lang):

    usage = translator.get_usage()
    if usage.any_limit_reached:
        flash("TRANSACTION LIMIT REACHED...")
        return redirect("/")

    print(file_in)

    xl = pd.ExcelFile(file_in)
    translate_cache = {}
    # print(sf)
    #
    # return "before translate"
    excel_writer = StyleFrame.ExcelWriter(FILE_OUT_PATH)
    for sheet in xl.sheet_names:
        cur_sf = StyleFrame.read_excel(
            file_in, read_style=True, sheet_name=str(sheet))
        print("~~ SHEET: " + str(sheet))
        for col in cur_sf.columns:
            print("... TRANSLATING: " + str(col))
            for cell in cur_sf[col]:
                # cell.value = translator.translate_text(cell.value, target_lang="FR")
                if (type(cell.value) == str and cell.value != "nan"):
                    init_value = str(cell.value)
                    if (init_value not in translate_cache):

                        cell.value = translator.translate_text(
                            cell.value, target_lang=target_lang)
                        translate_cache[init_value] = cell.value
                        # print("translated: " + str(init_value) + " to " + str(cell.value))
                    else:
                        cell.value = translate_cache[init_value]
                        # print("CACHED: translated: " + str(init_value) + " to " + str(cell.value))
        # new_sheet_name = str(translator.translate_text(str(sheet), target_lang=TARGET_LANG))
        cur_sf.to_excel(excel_writer, sheet_name=str(sheet))

    excel_writer.save()

    return send_file(FILE_OUT_PATH)
