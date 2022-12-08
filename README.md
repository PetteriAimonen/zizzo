Zizzo series solver
===================

This is a solver for simple alphanumeric series, made in Python.
Originally created for an [Ohjelmointiputka competition](https://www.ohjelmointiputka.net/kilpa.php?tunnus=alyo) in 2006.

Example usage:

    python clitest.py A50X B100XX C200XXX D400XXXX

    Initial series: 
       A50X
       B100XX
       C200XXX
       D400XXXX

    Next 10 entries: 
       E800XXXXX
       F1600XXXXXX
       G3200XXXXXXX
       H6400XXXXXXXX
       I12800XXXXXXXXX
       J25600XXXXXXXXXX
       K51200XXXXXXXXXXX
       L102400XXXXXXXXXXXX
       M204800XXXXXXXXXXXXX
       N409600XXXXXXXXXXXXXX

Try it online
-------------

Online version is available here: [https://jpa.kapsi.fi/zizzo](https://jpa.kapsi.fi/zizzo).

Running test cases
------------------

To run the test case sets, use:

    python clitest.py testcases/testi1.txt
    python clitest.py testcases/testi2.txt

There are a few test cases that currently do not get the answer defined in the file, but a different answer by less obvious logic.

