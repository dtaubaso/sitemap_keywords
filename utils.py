from flask import Markup
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.offline import plot
from datetime import datetime
import pytz, re, math, os, json
import requests
import gzip
from io import BytesIO
import xmltodict
from unicodedata import normalize
from user_agent import ua
import random

stopwords = requests.get("https://raw.githubusercontent.com/dtaubaso/aux/main/stopwords").text.split("\n")

def get_time_date():
    now_raw = pytz.timezone('UTC').localize(datetime.utcnow())
    now = now_raw.astimezone(pytz.timezone('America/Buenos_Aires'))
    today = datetime.strftime(now, '%d/%m/%Y %H:%M')
    return today


def get_titles(url, category):
    headers = {'User-Agent': random.choice(ua)}
    r = requests.get(url, headers=headers)
    if '.gz' in url:
        raw = gzip.GzipFile(fileobj=BytesIO(r.content)).read()
    else:
        raw = r.content
    parsed_raw = xmltodict.parse(raw)
    if category == 'RSS':
        titles = [a['title'] for a in parsed_raw['rss']['channel']['item']]
    elif category == 'Sitemap News':
        n = None
        if 'news:news' in parsed_raw['urlset']['url'][0].keys():
            n = 'news'
        elif 'n:news' in parsed_raw['urlset']['url'][0].keys():
            n = 'n'
    titles = [a[f'{n}:news'][f'{n}:title'] for a in parsed_raw['urlset']['url']]
    titles = [re.sub("( \-.*)", "", a) for a in titles]
    titles = [a.replace('quote', '') for a in titles]
    titles = [a.replace('quot', '') for a in titles]
    titles = [a.replace('dot', '') for a in titles]
    titles = list(set(titles))
    titles = [normalizar(palabra) for palabra in titles]
    return titles


def normalizar(palabra):
    palabra  = palabra.lower()
    palabra = re.sub(r'[^A-Za-záéíóúÁÉÍÓÚüÜÑñàçéíïl·lòóúü ]+', '', palabra)
    palabra = palabra.replace('ñ', '\001')
    palabra = normalize('NFKD', palabra).encode('ASCII', 'ignore').decode().replace('\001', 'ñ')
    palabra = [a.lower() for a in palabra.split() if a.lower() not in stopwords and len(a.lower())>1]
    palabra = " ".join(palabra)
    return palabra


def word_tokenize(text_list, phrase_len):
  split = [text.lower().split() for text in text_list]
  return [[' '.join(s[i:i + phrase_len])
             for i in range(len(s) - phrase_len + 1)] for s in split]

def create_graph(plot_list, ngrams):
    figures = []
    #barcolors = plotly.colors.qualitative.Set1
    n_colors = len(plot_list)
    barcolors = px.colors.sample_colorscale('turbo', [n/(n_colors) for n in range(n_colors)])
    for i, pp in enumerate(plot_list):
        fig = plot_word_counts(plot_list[i][0][:35], plot_list[i][1], plot_list[i][2])
        fig.data[0].marker.color = barcolors[i]
        fig.layout.title.font.color = '#416649'
        figures.append(fig)
    rows = int(math.ceil((len(plot_list)/2)))
    fig = make_subplots(rows=rows, cols=2, vertical_spacing=0.05, horizontal_spacing=0.1,
                        subplot_titles=[f.layout.title.text for f in figures])
    indexcols = [1, 2]
    indexrows = [(g // 2) + 1 for g in list(range(len(plot_list)))]
    for j in range(len(plot_list)):
        fila = indexrows[j]
        columna = indexcols[0] if j % 2 == 0 else indexcols[1]
        fig.add_trace(trace=figures[j].data[0], row=fila, col=columna)
    fig.layout.height = 600 * rows
    fig.layout.template = 'gridon'
    fig.layout.margin.l = 160
    fig.layout.margin.t = 150
    fig.update_layout(margin_pad=5)
    for a in range(1, len(plot_list) + 1):
        fig.layout[f'yaxis{a}'].dtick = 1
    if ngrams == None:
        ngrams = '1 y 2'
    fig.layout.title = f'<b>Palabras más usadas en títulos | {ngrams} grams<b><br>{get_time_date()}'
    viz = plot(fig, config={'displayModeBar': False}, output_type='div',
               include_plotlyjs='cdn', auto_open=False)
    viz = Markup(viz)
    return viz


def plot_word_counts(df, name, num_articles):
    fig = px.bar(df[::-1], x='freq', y='word', orientation='h',
                 height=600, width=650, hover_name='word',
                 title=f'<b>{name}</b> - ({num_articles} artículos)',
                 template='none', labels=df['word'].to_list())
    fig.layout.margin.l = 250
    fig.layout.xaxis.zeroline = False
    fig.layout.showlegend = False
    return fig

def send_slack(mensaje):
    webhook_url = os.environ['webhook']
    slack_data = {'text': mensaje}
    response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})


