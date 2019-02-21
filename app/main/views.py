from flask import render_template, session, redirect, url_for, request, jsonify
from . import main
from .forms import WordToWord, WordToAll, WordToUser, UserToUser, UserToAll, WordToAllUsers, UserNetwork
from app.models import Term, User
import os
import csv
import numpy as np
from numpy import dot, transpose
import pandas as pd
import networkx as nx
from math import degrees
import json
import time

with open(os.path.join(os.getcwd(), 'app\\static\\data\\terms.csv'), 'r') as f:
    r = csv.reader(f)
    COLUMNS = list(r)

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/comparisons', methods=['GET'])
def comparisons():
    return render_template("comparisons.html")

@main.route('/networks', methods=['GET'])
def networks():
    return render_template("networks.html")

@main.route('/buildNet', methods=['GET', 'POST'])
def buildNet():
    form = UserNetwork()
    user = None
    numUsers = None
    net = None
    nodes = None
    edges = None
    data = None
    bridges=None
    central=None
    if form.validate_on_submit():
        user = form.user.data
        numUsers = form.numUsers.data
        net = buildNetwork(user, numUsers)
        bb = nx.current_flow_betweenness_centrality(net, weight="weight")
        central = sorted(bb.items(), key=lambda kv: kv[1], reverse=True)[0:5]
        nx.set_node_attributes(net, bb, "betweenness")
        degree = nx.degree_centrality(net)
        nx.set_node_attributes(net, degree, "degree")
        data = nx.node_link_data(net)
        bridges= list(nx.bridges(net))
        timeStamp = time.strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(os.getcwd(), f"app\\static\\data\\data_file_{timeStamp}.json"), "w") as write_file:
                json.dump(data, write_file)
        data = f"/static/data/data_file_{timeStamp}.json"#, fp=(os.path.join(os.getcwd(), "\\app\\static\\data\\net.json")))
        #formattedNodes = "nodes: [\n"
        #for node in net.nodes():
        #    fN = '{\n data: { id: %s }\n},\n' %node
        #    formattedNodes += fN
    return render_template("networks.html", form=form, user=user,
                           numUsers=numUsers,net=net,
                           nodes=nodes, edges=edges, data=data,
                           bridges=bridges, central=central)

@main.route('/terms', methods=['GET'])
def termsDic():
    res = Term.query.all()
    list_terms = [r.as_dict() for r in res]
    return jsonify(list_terms)

@main.route('/users', methods=['GET'])
def usersDic():
    res = User.query.all()
    list_users = [r.as_dict() for r in res]
    return jsonify(list_users)

@main.route('/wordToWord', methods=['GET', 'POST'])
def unitUnit():
    form = WordToWord()
    comp = "Word to Word Comparison"
    desc = """This kind of comparison will allow you to get a measure of the <i>distance</i> between
               two terms in the feature space of the <i>Internet Research Agency</i> tweet corpus.
               What the result shows is how similarly the terms function within the context of all of
               the troll's tweets. The measure is based on the 'latent,' or underlying, conceptual
               structure of the term determined by all of its usages within the troll's tweets."""
    dist = None
    firstWord = None
    secondWord = None
    vecs = None
    if form.validate_on_submit():
        firstWord = form.wordOne.data
        secondWord = form.wordTwo.data
        dist, vecs = wordToWord(firstWord, secondWord)
    return render_template('forms.html', form=form, comp=comp, desc=desc,
                           termOne=firstWord, termTwo=secondWord, dist=dist,
                           vecs=vecs)

@main.route('/mostSimilar', methods=['GET', 'POST'])
def mostSimilar():
    form = WordToAll()
    comp = "Most Similar Terms"
    desc = """This search will return those terms that are most similar in function and meaning
              to the given search term."""
    dist = None
    term = None
    numWords = None
    if form.validate_on_submit():
        term = form.term.data
        numWords = form.numWords.data
        dist = mostSimilarTerms(term, numWords)
    return render_template('forms.html', form=form, comp=comp, desc=desc,
                       term=term, dist=dist)

@main.route('/userToUser', methods=['GET', 'POST'])
def userUser():
    form = UserToUser()
    comp = "User to User Comparison"
    desc = """This kind of comparison will allow you to get a measure of the <i>distance</i> between
               two users in the feature space of the <i>Internet Research Agency</i> tweet corpus.
               What the result shows is how similarly the users function within the context of all of
               each user's tweets. The measure is based on the 'latent,' or underlying, conceptual
               structure of the user's entire collection of tweets within the corpus."""
    dist = None
    userOne = None
    userTwo = None
    if form.validate_on_submit():
        userOne = form.userOne.data
        userTwo = form.userTwo.data
        dist = userToUser(userOne, userTwo)
    return render_template('forms.html', form=form, comp=comp, desc=desc,
                           userOne=userOne, userTwo=userTwo, dist=dist)


@main.route('/userToAll', methods=['GET', 'POST'])
def mostSimilarUsers():
    form = UserToAll()
    comp = "Most Similar Users"
    desc = """This search will return the most similar users to the given user.  The
              Similarity is determined by the way that each user employs language;
              that is, the distance between users is determined by the conceptual
              similarity/structure of their language based on their collected
              tweets."""
    user = None
    numUsers = None
    dist = None
    if form.validate_on_submit():
        user = form.user.data
        numUsers = form.numUsers.data
        dist = userToAll(user, numUsers)
    return render_template('forms.html', form=form, comp=comp, desc=desc,
                           user=user, dist=dist)

@main.route('/wordToUser', methods=['GET', 'POST'])
def termToUser():
    form = WordToUser()
    comp = "Word to User"
    desc = """This search will return the distance (similarity) between a User (composed
            of all of their tweets) and a term (as it functions within the entire corpus).
            This can be seen as a measure of how similarly the user's tweets function
            to the way that the term functions within the corpus (how well a term 
            represents a user's tweet history)."""
    user = None
    term = None
    dist = None
    if form.validate_on_submit():
        user = form.user.data
        term = form.term.data
        dist = wordToUser(term, user)
    return render_template('forms.html', form=form, comp=comp, desc=desc,
                           user=user, term=term, dist=dist)

@main.route('/wordToAllUsers', methods=['GET', 'POST'])
def termToAllUsers():
    form = WordToAllUsers()
    comp = "Word to Users"
    desc = """This search will return the distance (similarity) between a term (as its meaning
            is constructed by the corpus) and <i>N</i> users.
            This can be seen as a measure of how similarly the user's tweets function
            to the way that the term functions within the corpus (how well the term 
            represents a user's tweet history)."""
    term = None
    numUsers = None
    dist = None
    if form.validate_on_submit():
        term = form.term.data
        numUsers = form.numUsers.data
        dist = wordToAllUsers(term, numUsers)
    return render_template('forms.html', form=form, comp=comp, desc=desc,
                           term=term, dist=dist)


########################################################
###                 Analysis functions.              ###
########################################################

def cosine(x,y):
    top = dot(x,y)
    bottom = np.sqrt((x*x).sum()) * np.sqrt((y*y).sum())
    cos = top/bottom
    acos = degrees(np.arccos(cos))  # Take the inverse cosine and convert from radians to degrees.
    # This, according to Bellegarda, satisfies the properties of a distance
    # in the feature space.
    return(acos)

def wordToWord(termOne, termTwo):
    u = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\u.csv'), delimiter=',')
    s = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\s.csv'), delimiter=',')
    termOne = Term.query.filter_by(name=termOne)
    termTwo = Term.query.filter_by(name=termTwo)
    us = dot(u, np.diag(s))
    dist = cosine(us[termOne[0].id,], us[termTwo[0].id,])
    vecs = (us[termOne[0].id,], us[termTwo[0].id,])
    return(dist, vecs)

def mostSimilarTerms(term,numTerms):
    u = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\u.csv'), delimiter=',')
    s = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\s.csv'), delimiter=',')
    term = Term.query.filter_by(name=term)[0].id
    columns = Term.query.all()
    us = dot(u,np.diag(s))
    values = {}
    # have to adjust index since columns in database don't include
    # the first empty element, so there's a mismatch by 1 in the
    # term indices. Only affects the display of terms, not calculation.
    for i in range(0, len(columns)):
        dist = 0
        if(i != term):
            dist = cosine(us[term,], us[i,])
            if dist > 0 :
                values[columns[i-1].name] = dist
    values = sorted(values.items(), key=lambda kv: kv[1])[0:numTerms]
    return values

def userToUser(userOne,userTwo):
    v = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\v.csv'), delimiter=',')
    s = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\s.csv'), delimiter=',')
    userOne = User.query.filter_by(username=userOne)[0].id
    userTwo = User.query.filter_by(username=userTwo)[0].id
    # need to transpose v to get the v matrix and do the dot product since v is already transposed from SVD.
    vs = dot(transpose(v),np.diag(s))
    # Need to subtract one from index since vs is indexed to 0 and
    # users are indexed to 1.
    return(cosine(vs[userOne-1,], vs[userTwo-1,]))

def userToAll(user, numUsers):
    v = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\v.csv'), delimiter=',')
    s = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\s.csv'), delimiter=',')
    user = User.query.filter_by(username=user)[0].id-1
    users = User.query.all()
    vs = dot(transpose(v),np.diag(s))
    values = {}
    for i in range(1, len(users)):
        dist = 0
        if(i != user):
            dist = cosine(vs[user,], vs[i,])
            if dist > 0 :
                values[users[i].username] = dist
    values = sorted(values.items(), key=lambda kv: kv[1])[0:numUsers]
    return(values)

def wordToUser(term, user):
    v = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\v.csv'), delimiter=',')
    s = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\s.csv'), delimiter=',')
    u = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\u.csv'), delimiter=',')
    v = transpose(v)
    term = Term.query.filter_by(name=term)[0].id
    user = User.query.filter_by(username=user)[0].id-1
    us = dot(u, np.sqrt(np.diag(s)))
    vs = dot(v, np.sqrt(np.diag(s)))
    dist = cosine(us[term,], vs[user,])
    return(dist)

def wordToAllUsers(term, numUsers):
    v = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\v.csv'), delimiter=',')
    s = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\s.csv'), delimiter=',')
    u = np.genfromtxt(os.path.join(os.getcwd(), 'app\\static\\data\\u.csv'), delimiter=',')
    v = transpose(v)
    term = Term.query.filter_by(name=term)[0].id
    us = dot(u, np.sqrt(np.diag(s)))
    vs = dot(v, np.sqrt(np.diag(s)))
    users = User.query.all()
    values = {}
    for user in users:
        dist = cosine(us[term,], vs[user.id-1,])
        if(dist > 0):
            values[user.username] = dist
    values = sorted(values.items(), key=lambda kv: kv[1])[0:numUsers]
    return(values)

def buildNetwork(user, numUsers, network = nx.Graph()):
    sn = user
    nodes = userToAll(user, numUsers)
    for edge in nodes:
        network.add_edge(sn, edge[0], weight=edge[1])
        secondaryNodes = userToAll(edge[0], numUsers)
        for sec in secondaryNodes:
            network.add_edge(edge[0], sec[0], weight=sec[1])
    return(network)