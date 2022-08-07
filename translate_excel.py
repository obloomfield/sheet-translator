from dotenv import dotenv_values
config = dotenv_values(".env")
import os

from flask import Blueprint, jsonify, send_file

from styleframe import StyleFrame
import pandas as pd

import deepl

translate_API = Blueprint('translate_API', __name__, template_folder='templates')

FILE_OUT_PATH = "example\SPRINT_fr_translate.xlsx"
TARGET_LANG = "FR"

translator = deepl.Translator(config["DEEPL_AUTH_KEY"])

@translate_API.route('/translate/', methods=['GET'])
def translate_respond():
  file_in = 'example\SPRINT_eng.xlsx'
  return translate(file_in)


# def translate_document(file_in):
#   try:
#     # Using translate_document_from_filepath() with file paths 
#     translator.translate_document_from_filepath(
#         file_in,
#         FILE_OUT_PATH,
#         target_lang="FR",
#         formality="more"
#     )

#   except deepl.DocumentTranslationException as error:
#       # If an error occurs during document translation after the document was
#       # already uploaded, a DocumentTranslationException is raised. The
#       # document_handle property contains the document handle that may be used to
#       # later retrieve the document from the server, or contact DeepL support.
#       doc_id = error.document_handle.id
#       doc_key = error.document_handle.key
#       print(f"Error after uploading ${error}, id: ${doc_id} key: ${doc_key}")
#   except deepl.DeepLException as error:
#       # Errors during upload raise a DeepLException
#       print(error)

#   return "TRANSLATED DOCUMENT"

def translate(file_in):
  
  xl = pd.ExcelFile(file_in)
  translate_cache = {}
  # print(sf)
  # 
  # return "before translate"
  excel_writer = StyleFrame.ExcelWriter(FILE_OUT_PATH)
  for sheet in xl.sheet_names:
    cur_sf = StyleFrame.read_excel(file_in, read_style=True, sheet_name=str(sheet))
    print("~~ SHEET: " + str(sheet))
    for col in cur_sf.columns:
      print("... TRANSLATING: " + str(col))
      for cell in cur_sf[col]:
        # cell.value = translator.translate_text(cell.value, target_lang="FR")
        if (type(cell.value) == str and cell.value != "nan"):
          init_value = str(cell.value)
          if (init_value not in translate_cache):
            
            cell.value = translator.translate_text(cell.value, target_lang=TARGET_LANG)
            translate_cache[init_value] = cell.value
            # print("translated: " + str(init_value) + " to " + str(cell.value))
          else:
            cell.value = translate_cache[init_value]
            # print("CACHED: translated: " + str(init_value) + " to " + str(cell.value))
    # new_sheet_name = str(translator.translate_text(str(sheet), target_lang=TARGET_LANG))
    cur_sf.to_excel(excel_writer, sheet_name=str(sheet))

  excel_writer.save()

  return send_file(FILE_OUT_PATH)