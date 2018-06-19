from flask import Flask, render_template, redirect
from flask_script import Manager
from flask_nav import Nav
from flask_nav.elements import *
import pandas as pd
from pyecharts import Graph
import pyecharts.echarts.events as events
from pyecharts_javascripthon.dom import window
from pyecharts_javascripthon.dom import Document

# flask的app的一些初始化设置
app = Flask(__name__)
app.config.from_pyfile('config')
app.config['DEBUG'] = True
nav = Nav(app)
manager = Manager(app)

# echarts的加速器
REMOTE_HOST = "https://cdn.bootcss.com/echarts/4.1.0.rc2"

# 设置主页路由，获取页面表单内容作为查询内容，以此生成关系图
@app.route('/', methods=['GET', 'POST'])
def index():
    # 如果请求方法是post说明向服务器提供了搜索内容，进行搜索
    if request.method == 'POST':
        data = request.form['查询内容']
        graph = create_Graph(data)
        if graph == '404':
            return render_template('404.html'), 404
        else:
            return render_template('pyecharts.html', myechart=graph.render_embed(),
                               host=REMOTE_HOST,script_list=graph.get_js_dependencies())
    else:
        # 如果请求方法是GET说明是第一次登陆页面，is_begin_index表示是初始界面,
        graph = create_Graph(data='is_begin_index')
        return render_template('pyecharts.html', myechart=graph.render_embed(),
                               host=REMOTE_HOST, script_list=graph.get_js_dependencies())

# 根据点击节点的label修改表单内容
# parames.name会自动返回点击的节点的名称！！！！！！
def on_click(params):
    form = document.createElement("form")
    form.action = window.location.href
    form.method = 'POST'
    input = document.createElement("input")
    input.type = "hidden"
    input.name = '查询内容'
    input.value = params.name
    form.appendChild(input)
    document.body.appendChild(form)
    form.submit()

# 创建关系图的方法
def create_Graph(data):
    # 如果是进入主页则展示所有企业的关系图
    if data == 'is_begin_index':
        spo = pd.read_excel(r'c2c.xlsx')
        company = pd.read_excel(r'company.xlsx')

        # 将节点间的关系存入links
        links = []
        for i in range(spo.shape[0]):
            links.append(
                {'source': spo.iloc[i, 1], 'target':spo.iloc[i, 3], 'category':1, "value": spo.iloc[i, 2],
                 'label': {'normal': {'show': True, 'formatter': "{c}"}}}
            )

        # 将节点存入nodes
        nodes = []
        for i in range(company.shape[0]):
            nodes.append({'name': company.iloc[i, 1], 'category': 1, 'symbolSize': 10, 'draggable': True, 'symbol': 'square'})

        # 画图
        graph = Graph('知识图谱服务', width=1200, height=600)
        graph.add('', nodes, links, categories=['个人', '企业'], label_pos='right', graph_repulsion=200,
                      is_legend_show=True, line_curve=0, label_text_color=None, is_label_show=True,
                      is_symbol_show=True, graph_edge_symbol=[None, 'arrow'])
        # 监听鼠标点击事件
        graph.on(events.MOUSE_CLICK, on_click)

    # 如果有请求搜索的内容则进入下面的代码块
    else:
        item = str(data)
        spo = pd.read_excel(r'final_spo.xlsx')
        company = pd.read_excel(r'company.xlsx')

        # 以正则表达式匹配人名，有些人名后有数字，以此来分辨是否为同一个人
        object_search = spo[spo['object'].str.contains('%s[1-9]?$' % item)]
        object2_search = spo[spo['object_2'].str.contains('%s[1-9]?$' % item)]


        links = []
        # 如果没找到搜索内容则返回404
        if object_search.empty and object2_search.empty:
            return '404'
        # 找到了则进行如下处理
        else:
            # 由于数据库的布局，公司名称一定出现在object_2这一列，所以如果object列搜索结果为空，而object_2搜索不为空，则说明搜索的一定为企业，则把属于该企业的所有人都显示出
            if object_search.empty:
                # 找出该企业的所有人
                grouped_spo = spo.groupby('company')
                for name, group in grouped_spo:
                    if name == object2_search.iloc[0,2]:
                        result = group

                # 存入结点间的关系
                for i in range(result.shape[0]):
                    links.append(
                        {'source': result.iloc[i, 0], 'target': result.iloc[i, 2], 'category': 1, "value": result.iloc[i, 1],
                         'label': {'normal': {'show': True, 'formatter': "{c}"}}})

                # 存入相关结点
                nodes = []
                person_nodes = result.drop_duplicates('object', keep='first')
                for i in range(person_nodes.shape[0]):
                    nodes.append({'name': person_nodes.iloc[i, 0], 'category': 0, 'symbolSize': 10, 'draggable': True})

                company_nodes = result.drop_duplicates('company', keep='first')
                for i in range(company_nodes.shape[0]):
                    nodes.append(
                        {'name': company_nodes.iloc[i, 3], 'category': 1, 'symbolSize': 20, 'draggable': True,
                         'symbol': 'square'})

            # 如果object有搜索结果，则说明搜索内容不是公司，而是人物
            else:
                # 将结点间的关系存入links
                for i in range(object_search.shape[0]):
                    links.append(
                        {'source': object_search.iloc[i, 0], 'target': object_search.iloc[i, 2], 'category': 1,
                         "value": object_search.iloc[i, 1],
                         'label': {'normal': {'show': True, 'formatter': "{c}"}}})

                # 搜索出来的是人物的话，把他所属的公司也一并显示出来
                links.append(
                    {'source': object_search.iloc[0, 0], 'target': object_search.iloc[0, 3], 'category': 1,
                     "value": '属于',
                     'label': {'normal': {'show': True, 'formatter': "{c}"}}})

                for i in range(object2_search.shape[0]):
                    links.append(
                        {'source': object2_search.iloc[i, 0], 'target': object2_search.iloc[i, 2], 'category': 1,
                         "value": object2_search.iloc[i, 1],
                         'label': {'normal': {'show': True, 'formatter': "{c}"}}})

                # 将相关结点存入nodes，由于在object和object_2两列搜索，所以要将两列的相关结点都存入，所以要存两遍（此处处理方法并不好，应该有更简单的处理方法和代码形式）
                # 此处存入object搜索结果
                nodes = []

                person_nodes = object_search.drop_duplicates('object', keep='first')
                for i in range(person_nodes.shape[0]):
                    nodes.append({'name': person_nodes.iloc[i, 0], 'category': 0, 'symbolSize': 10, 'draggable': True})

                # 这里虽然叫company_nodes，但是可能是公司也可能是人物
                company_nodes = object_search.drop_duplicates('object_2', keep='first')
                for i in range(company_nodes.shape[0]):
                    # 在object2中如果是公司的话就用公司的结点大小与形状，如果不是就用个人的
                    if company_nodes.iloc[i, 2] in list(company['company']):
                        nodes.append(
                            {'name': company_nodes.iloc[i, 2], 'category': 1, 'symbolSize': 20, 'draggable': True,
                             'symbol': 'square'})
                    else:
                        nodes.append(
                            {'name': object_search.iloc[i, 2], 'category': 0, 'symbolSize': 10, 'draggable': True})

                # 如果搜索出来的是人物的话，把公司结点也加入进去，以便显示其公司节点
                nodes.append({'name': company_nodes.iloc[0, 3], 'category': 1, 'symbolSize': 20, 'draggable': True,
                             'symbol': 'square'})

                # 此处存入object_2的搜索结果
                person_nodes = object2_search.drop_duplicates('object', keep='first')
                for i in range(person_nodes.shape[0]):
                    nodes.append({'name': person_nodes.iloc[i, 0], 'category': 0, 'symbolSize': 10, 'draggable': True})

                company_nodes = object2_search.drop_duplicates('object_2', keep='first')
                for i in range(company_nodes.shape[0]):
                    if company_nodes.iloc[i, 2] in list(company['company']):
                        nodes.append(
                            {'name': company_nodes.iloc[i, 2], 'category': 1, 'symbolSize': 20, 'draggable': True,
                             'symbol': 'square'})
                    else:
                        nodes.append(
                            {'name': company_nodes.iloc[i, 2], 'category': 0, 'symbolSize': 10, 'draggable': True})

                # 一般搜索内容的结点会重复存入一次，所以在此处删除重复结点
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        if nodes[i]['name'] == nodes[j]['name']:
                            nodes.pop(j)
                            break

        # 画图
        graph = Graph('%s关系图' % item, width=1200, height=600)
        graph.add('', nodes, links, categories=['个人', '企业'], label_pos='right', graph_repulsion=500,
                  is_legend_show=True, line_curve=0, label_text_color=None, is_label_show=True,
                  is_symbol_show=True, graph_edge_symbol=[None, 'arrow'])
        # 监听鼠标点击事件
        graph.on(events.MOUSE_CLICK, on_click)

    return graph

if __name__ == '__main__':
    manager.run()
