from flask import Flask, render_template, Markup, send_from_directory, request
import gspread
import pandas as pd
from google.oauth2 import service_account
from utils import *
import functools, operator, os, base64, pickle
from collections import Counter
import traceback

pvk_string = os.environ['encoded_key']
private_key = pickle.loads(base64.b64decode(pvk_string))

gc = gspread.service_account_from_dict(private_key)

app = Flask(__name__, static_folder='static', static_url_path='/static')


@app.route("/<sheet_name>", methods=['GET'])
def main(sheet_name):
  page_title = sheet_name.replace('_', ' ').title()
  max_ngrams = None
  ngrams = None
  min_ngrams = None
  try:
    df = pd.DataFrame(gc.open(sheet_name).get_worksheet(0).get_all_records())
    plot_list = []
    if request.args.get('ngrams') is not None:
      max_ngrams = request.args.get('ngrams', type=int)
      min_ngrams = max_ngrams
      ngrams = max_ngrams
    else:
      min_ngrams = 1
      max_ngrams = 2
    for index, row in df.iterrows():
      try:
        titles = get_titles(row['url'], row['category'])
        tokens = []
        for i in range(min_ngrams, max_ngrams+1):
          tokens_ngrams = word_tokenize(titles, i)
          tokens.extend(tokens_ngrams)
      except xmltodict.expat.ExpatError as e:
        message = f'*Sitemaps {page_title}*\nOcurrió un error: {e} en {row["name"]}'
        send_slack(mensaje)
      except Exception:
        message = f'*Sitemaps {page_title}*\nOcurrió un error: {e} en {row["name"]}'
        send_slack(message)
      tokens_flat = functools.reduce(operator.iconcat, tokens, [])
      tokens_top = Counter(tokens_flat).most_common(100)
      df_tokens_top = pd.DataFrame(tokens_top, columns=['word', 'freq'])
      plot_list.append([df_tokens_top, row['name'], len(titles)])
    viz = create_graph(plot_list, ngrams)
    return render_template('graph.html', title=page_title, viz=viz, sheet_name=sheet_name)
  except Exception:
    if page_title != 'Robots.Txt' or page_title != 'Favicon.Ico':
      mensaje = f'*{page_title}*\nOcurrió un error:\n{traceback.format_exc()}'
      send_slack(mensaje)
      return 'Error'

@app.route('/robots.txt')
@app.route('/favicon.ico')
def static_from_root():
  return send_from_directory(app.static_folder, request.path[1:])

if __name__ == '__main__':
    app.run(debug=True, port=5001)


