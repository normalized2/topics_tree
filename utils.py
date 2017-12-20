# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division


#import time
import re
#from os.path import exists, isfile, join
#from optparse import OptionParser
#import os
import json
from collections import OrderedDict
from functools import reduce
#import codecs
import uuid

#import requests
import bs4
import pandas as pd
import numpy as np
from IPython.core.display import display, HTML  # , Markdown

import treelib
from treelib import Tree  # , Node
import mistune


reMainTopicId = re.compile(r'https://glav.su/forum/(\d+)/')
reTopicId = re.compile(r'https://glav.su/forum/(\d+)/(\d+)/')
re_author_id = re.compile('https://glav.su/members/(\d+)/')

tag_columns = ['tag1', 'tag2', 'tag3', 'tag4']


def load_json(fname):
    with open(fname) as f:
        return json.load(f)


def save_json(fname, d, pretty=False):
    with open(fname, 'w') as f:
        if pretty:
            json.dump(d, f, indent=4, sort_keys=True)
        else:
            json.dump(d, f)


def parse_tree(tree_md):
    r = mistune.markdown(tree_md)
    #doc = bs4.BeautifulSoup(r, 'lxml')
    doc = bs4.BeautifulSoup(r, 'html.parser')

    tree = Tree()
    tree.create_node('root', -1)

    def find_li(element, parent_id=-1, main_tid=None):
        res = []
        for ul in element('ul', recursive=False):
            for li in ul('li', recursive=False):
                d = {}

                a = li.find('a')
                data = {}

                if a is not None:
                    text = a.text
                    data['href'] = a.attrs['href']
                    m = reMainTopicId.match(a.attrs['href'])
                    main_tid = int(m.groups()[0])
                else:
                    text = li.find(text=True, recursive=False)

                d['text'] = text

                data['is_category'] = True

                tag_id = u"{} {}".format(main_tid, text)

                tree.create_node(text, tag_id, parent=parent_id, data=data)

                d['children'] = find_li(
                    li, parent_id=tag_id, main_tid=main_tid)
                res.append(d)
        return res

    try:
        data = find_li(doc)
        del data
    except treelib.exceptions.DuplicatedNodeIdError as e:
        print(u'{}'.format(e))
    return tree


def get_unique_tags(df_topics, tag_columns=tag_columns):
    res = []
    groups = df_topics.groupby('main_tid')
    for main_tid, g in groups:
        u = [g[pd.notnull(g[tag_column])][tag_column].unique()
             for tag_column in tag_columns]
        u = np.unique(np.hstack(u))
        u = [u'{} {}'.format(main_tid, tag) for tag in u]
        res += u
    return res


def check_tags(tree, df_topics, tag_columns=tag_columns):
    tree_tags = set(tree._nodes.keys())
    topics_tags = set(get_unique_tags(df_topics, tag_columns))

    absents = topics_tags.difference(tree_tags)
    re_tid_tag = re.compile(r'(\d+) (.*)')

    indices = []

    for absent in absents:
        m = re_tid_tag.match(absent)
        assert m is not None
        groups = m.groups()
        main_tid = int(groups[0])
        tag = groups[1]

        idx_main_tid = df_topics['main_tid'] == main_tid

        idx_absent_tag = []
        for tag_column in ['tag1', 'tag2', 'tag3']:
            idx_absent_tag.append(df_topics[tag_column] == tag)

        idx_absent_tag = reduce((lambda x, y: x | y), idx_absent_tag)
        idx = idx_main_tid & idx_absent_tag

        indices.append(idx)

    return absents, indices


def print_absents(absents, indices, df_topics):
    if len(absents) == 0:
        return
    display(HTML(u'<h3>Отсутсвующие тэги:</h3>'))
    for absent, idx in zip(absents, indices):
        display(HTML(u'<b>Тэг:</b> "{}"'.format(absent)))
        s_list = []
        for i, row in df_topics[idx].iterrows():
            s = u'<li>{} <a href="{}">{}</a></li>'.format(
                i, row['href'], row['title'])
            s_list.append(s)
        s = u"<ul>{}</ul>".format(u'\n'.join(s_list))
        display(HTML(s))


def create_topics_tree(tree, df_topics, tag_columns=tag_columns):

    topics_tree = Tree(tree.subtree(tree.root), deep=True)
    groups = df_topics.groupby('main_tid')
    for main_tid, g in groups:
        for i, row in g.iterrows():
            tags = [row[tag_column]
                    for tag_column in tag_columns
                    if not pd.isnull(row[tag_column])]
            tags = [u'{} {}'.format(main_tid, tag) for tag in tags]

            for tag in tags:
                topics_tree_id = uuid.uuid4()
                text = row['title']
                try:
                    topics_tree.create_node(text, topics_tree_id, parent=tag,
                                            data=dict(row))
                except treelib.exceptions.DuplicatedNodeIdError as e:
                    print(u'{}'.format(e))
                except treelib.exceptions.NodeIDAbsentError as e:
                    print(u'{}'.format(e))

    return topics_tree


def topics_tree_2_markdown(tree):
    res = u''

    for i, n in enumerate(walk(tree, tree)):
        if i != 0:
            is_bold = n.data.get('is_bold', False)
            is_blocked = n.data.get('is_blocked', False)
            href = n.data.get('href', False)
            if is_bold:
                bold_chars = "**"
            else:
                bold_chars = ""
            if is_blocked:
                bold_chars = "~~"

            if href:
                s = u"[{}]({})".format(n.tag, href)
            else:
                s = n.tag

            s = u"{}{}{}{}".format(
                "  " * n.level + "- ",
                bold_chars,
                s,
                bold_chars)
            res += s + "\n"
    return res


def walk(tree, node):
    if isinstance(node, Tree):
        node.tag = 'root'
        node.level = 0
        yield node
        parent_id = -1
    else:
        yield node
        parent_id = node.identifier

    childs = tree.children(parent_id)

    for child in childs:
        child.level = node.level + 1

        is_category = child.data.get('is_category', False)
        if not is_category:
            yield child

    for child in childs:
        child.level = node.level + 1

        is_category = child.data.get('is_category', False)
        if is_category:
            for n in walk(tree, child):
                yield n


def topics_tree_2_dict(tree):
    def get_chidlrens(tree, node):
        res = []
        if tree == node:
            _id = -1
        else:
            _id = node.identifier

        for child in tree.children(_id):
            d = OrderedDict()
            d['name'] = child.tag
            d['children'] = get_chidlrens(tree, child)
            d['is_category'] = child.data.get('is_category', False)
            if not d['is_category']:
                d['href'] = child.data.get('href')
                d['is_blocked'] = child.data.get('is_blocked', False)
            res.append(d)
        return res

    res = OrderedDict()

    res['name'] = 'root'
    res['children'] = get_chidlrens(tree, tree)
    return res
