
# -*- coding: UTF-8 -*-

import time
script_start = time.time()

import cgi
import cgitb
cgitb.enable()

import lib

print('Content-Type: text/html; charset=utf-8')
print()
print()

print('''
<html>
<head>
<title>Zizzo</title>
<link rel="Shortcut Icon" href="kuvake.png">
</head>
<body>
<h1>Zizzo &epsilon;</h1>
<p>
<b>Ei en&auml;&auml; kovin uutta!</b> Zizzon lähdekoodi on 
julkaistu:<br />
<a href="http://kapsi.fi/~jpa/stuff/other/zizzo.tgz">Unix-rivinvaihdoilla</a><br />
<a href="http://kapsi.fi/~jpa/stuff/other/zizzo.zip">Windows-rivinvaihdoilla</a>
</p>
<p>
Zizzon älykkyys voi vaikuttaa ihmeeltä, mutta loppujen lopuksi <a href="http://kapsi.fi/~jpa/stuff/pix/zizzorelations2.png">logiikka tämän taustalla on hyvin yksinkertainen</a>.
</p>
<p>
Zizzo on fiksu otus ja ratkoo sarjoja. Sarjoissa saa olla merkkejä A-Z ja 0-9.
Syötä termit välilyönnillä erotettuina ja klikkaa Hähhää!
</p>
<form method="GET" action="zizzo.cgi">
<input type="text" name="sarja" size="50" /><br />
Näytä <select name="maara">
        <option value="10">10</option>
        <option value="25">25</option>
        <option value="50">50</option>
</select> seuraavaa termiä
<br /><br />
<input type="submit" value="Hähhää!" />
</form>
<hr>''')

def footer():
    print('''</body></html>''')
    raise SystemExit

form = cgi.FieldStorage()
if 'sarja' not in form:
    footer()

try:
    maara = int(form['maara'].value)
except KeyError:
    maara = 10

sarja = lib.alphabet.split(form['sarja'].value.upper())

if len(sarja) < 3:
    print('''<h1 style="color:#F00">Zizzoa ei kiinnosta lukea ajatuksiasi! Syötä vähintään kolme termiä.</h1>''')
    footer()

try:
    mysolver = lib.Solver(sarja)
except lib.UnsolvableException:
    print('''
        <p>Tapahtui harvinainen poikkeus! Fiksu-Zizzo ei osannutkaan ratkaista sarjaasi.</p>
        <h1 style="color:#F00">Taisit huijata ja syöttää jotain puppua!</h1>''')
    footer()

print('''<p>Annetut termit: %s<br/>''' % ', '.join(map(str,sarja)))
print('''Seuraavat %d termiä:''' % maara)

lst = mysolver.generatelist(maara)

if max([len(s) for s in lst]) > 6:
    print('<ul>')
    for s in lst:
        print('''<li>%s</li>''' % s)
    print('</ul>')
else:
    print(', '.join(lst))

print('</p>')

print('''<h2>Näin Zizzo ratkaisi naurettavan helpon tehtäväsi:</h2>''')

def htmllines(solver):
    print("<b>" + solver.name() + " (helppous %2.0f%%)" % (solver.score() * 100) + "</b>")
    print("<ul>")
    
    items = list(solver.params().items()) + [('_sequence', solver.series)]
    items.sort(key = lambda x: x[0]) # Sort by key
    
    for key, value in items:
        print("<li>%s: " % key, end=' ')
        if isinstance(value, lib.base.Solver):
            htmllines(value)
        else:
            print(str(value), end=' ')
        print("</li>")
    
    print("</ul>")

htmllines(mysolver)

time_used = time.time() - script_start

print('''<p style="font-size:x-small">Zizzon älyä kuormitettiin %0.1f sekunnin ajan.</p>''' % time_used)
footer()
