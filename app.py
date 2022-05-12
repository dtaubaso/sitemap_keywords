from flask import Flask, render_template, Markup, send_from_directory, request
import gspread
import pandas as pd
from google.oauth2 import service_account
from utils import *
import functools, operator, os, base64, pickle
from collections import Counter

pvk_string = os.environ['encoded_key']
private_key = pickle.loads(base64.b64decode(pvk_string))

gc = gspread.service_account_from_dict(private_key)

app = Flask(__name__, static_folder='static', static_url_path='/static')


@app.route("/<sheet_name>", methods=['GET'])
def main(sheet_name):
  page_title = sheet_name.replace('_', ' ').title()
  try:
    df = pd.DataFrame(gc.open(sheet_name).get_worksheet(0).get_all_records())
    plot_list = []
    for index, row in df.iterrows():
      titles = get_titles(row['url'], row['category'])
      tokens = []
      for i in range(1,row['max_ngrams']+1):
        tokens_ngrams = word_tokenize(titles, i)
        tokens.extend(tokens_ngrams)
      tokens_flat = functools.reduce(operator.iconcat, tokens, [])
      tokens_top = Counter(tokens_flat).most_common(100)
      df_tokens_top = pd.DataFrame(tokens_top, columns=['word', 'freq'])
      plot_list.append([df_tokens_top, row['name'], len(titles)])
    viz = create_graph(plot_list)
    return render_template('graph.html', title=page_title, viz=viz)
  except Exception as e:
    if page_title != 'Robots.Txt' or page_title != 'Favicon.Ico':
      mensaje = f'*{page_title}*\nOcurrió un error: {e}'[:150]
      send_slack(mensaje)
      return 'Error'

@app.route('/robots.txt')
@app.route('/favicon.ico')
def static_from_root():
  return send_from_directory(app.static_folder, request.path[1:])

if __name__ == '__main__':
    app.run(debug=True, port=5001)


