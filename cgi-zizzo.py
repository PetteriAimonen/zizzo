
# -*- coding: UTF-8 -*-

import time
script_start = time.time()

import cgi
import cgitb
cgitb.enable()

import base
import combinedsolver

print 'Content-Type: text/html; charset=utf-8'
print
print

print '''
<html>
<body>
<h1>Zizzo &Delta;</h1>
<p>
Zizzo on fiksu otus ja ratkoo sarjoja. Sarjoissa saa olla merkkejä A-Z ja 0-9.
Syötä termit välilyönnillä erotettuina ja klikkaa Hähhää!
</p>
<p>
Zizzo is a smart thingy that solves sequences. Series may consist of characters A-Z and numbers 0-9.
Write terms separated by spaces.
</p>
<form method="GET" action="zizzo.cgi">
<input type="text" name="sarja" size="50" /><br /><br />
<input type="submit" value="Hähhää!" />
</form>
<hr>'''

def footer():
    print '''</body></html>'''
    raise SystemExit

form = cgi.FieldStorage()
if not form.has_key('sarja'):
    footer()

sarja = form['sarja'].value.split(' ')
sarja = [e.strip(' \n,') for e in sarja]
sarja = [e.upper() for e in sarja if e != ""]

if len(sarja) < 3:
    print '''<h1 style="color:#F00">Zizzoa ei kiinnosta lukea ajatuksiasi! Syötä vähintään kolme termiä.<br>
    Zizzo is not interested in reading your thoughts. Input atleast three entries.</h1>'''
    footer()

try:
    mysolver = combinedsolver.CombinedSolver(sarja)
except base.UnsolvableException:
    print '''
        <p>Tapahtui harvinainen poikkeus! Fiksu-Zizzo ei osannutkaan ratkaista sarjaasi.</p>
        <p>A rare exception occurred! The smart Zizzo couldn't solve your series.</p>
        <h1 style="color:#F00">Taisit huijata ja syöttää jotain puppua!<br>
        You probably tried to fool it and wrote some nonsense!</h1>'''
    footer()

print '''<p>Annetut termit (Input terms): %s<br/>''' % ', '.join(map(str,sarja))
print '''Seuraavat 10 termiä (Next 10 terms): %s</p>''' % ', '.join(map(str,mysolver.generatelist(10)))
print '''<h2>Näin Zizzo ratkaisi naurettavan helpon tehtäväsi:<br>
This is how Zizzo solved this ridicuously simple task:</h2>'''

def htmllines(solver):
    print "<b>" + solver.name() + " (helppous/easiness %2.0f%%)" % (solver.score() * 100) + "</b>"
    print "<ul>"
    
    items = solver.params().items()
    items.sort(lambda a,b: cmp(a[0], b[0])) # Sort by key
    
    for key, value in items:
        print "<li>%s: " % key,
        if isinstance(value, base.Solver):
            htmllines(value)
        else:
            print str(value),
        print "</li>"
    
    print "</ul>"

htmllines(mysolver)

time_used = time.time() - script_start

print '''<p style="font-size:x-small">Zizzon älyä kuormitettiin %0.1f sekunnin ajan.
Todellisuudessa aika riippuu vain palvelimen kuormasta.</p>''' % time_used
footer()
