#!/usr/bin/env python

from flask import Flask, request, render_template, url_for, redirect, session


app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/', methods=['GET', 'POST'])
