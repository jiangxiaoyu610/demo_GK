from flask import Flask, render_template, redirect
from forms import SearchForm
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_nav import Nav
from flask_nav.elements import *
import pandas as pd
from pyecharts import Graph
import pyecharts.echarts.events as events
from pyecharts_javascripthon.dom import window
from pyecharts_javascripthon.dom import Document

app = Flask(__name__)
app.config.from_pyfile('config')
bootstrap = Bootstrap(app)
app.config['DEBUG'] = True
nav = Nav(app)
manager = Manager(app)

nav.register_element('top', Navbar('知识图谱', View('主页', 'index')))

REMOTE_HOST = "https://cdn.bootcss.com/echarts/4.1.0.rc2"

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if request.method == 'POST':
        data = request.form['查询内容']
        graph = create_Graph(data)
        if graph == '404':
            return render_template('404.html'), 404
        else:
            return render_template('pyecharts.html', myechart=graph.render_embed(),
                               host=REMOTE_HOST,script_list=graph.get_js_dependencies())
    return render_template('index.html', title='Hello World', form=form)

def on_click(params):
    form = document.createElement("form");
    form.action = window.location.href;
    form.method = 'POST';
    input = document.createElement("input");
    input.type = "hidden";
    input.name = '查询内容';
    input.value = params.name;
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();

def create_Graph(data):
    # 先查找出搜索内容，并将三元组存入links
    item = str(data)
    spo = pd.read_excel(r'final_spo.xlsx')

    person_search = spo[spo['name'].str.contains('%s.?' % item)]
    company_search = spo[spo['company'].str.contains(item)]

    if person_search.empty and company_search.empty:
        return '404'
    else:
        if person_search.empty:
            result = company_search
        else:
            result = person_search

    links = []
    for i in range(result.shape[0]):
        links.append(
            {'source': result.iloc[i, 2], 'target': result.iloc[i, 8], 'category': 1, "value": result.iloc[i, 6],
             'label': {'normal': {'show': True, 'formatter': "{c}"}}})

    # 查找相关企业和人物，存入nodes

    nodes = []
    person_nodes = result.drop_duplicates('name', keep='first')
    for i in range(person_nodes.shape[0]):
        nodes.append({'name': person_nodes.iloc[i, 2], 'category': 0, 'symbolSize': 10, 'draggable': True})

    company_nodes = result.drop_duplicates('company', keep='first')
    for i in range(company_nodes.shape[0]):
        nodes.append(
            {'name': company_nodes.iloc[i, 8], 'category': 1, 'symbolSize': 20, 'draggable': True, 'symbol': 'square'})

    # 画图
    graph = Graph('%s的关系图' % item, width=1200, height=600)
    graph.add('', nodes, links, categories=['个人', '企业'], label_pos='right', graph_repulsion=400,
              is_legend_show=True, line_curve=0, label_text_color=None, is_label_show=True,
              is_symbol_show=True)
    graph.on(events.MOUSE_CLICK, on_click)
    return graph

if __name__ == '__main__':
    manager.run()
