05/07/2012     
build my small web app on django
using template and inheritance

05/08/2012
string.append() VS string.extend()
>>> a = [1,2,3]
>>> a.append([4, 5])
>>> a
[1, 2, 3, [4, 5]]
>>> a.extend([6, 7])
>>> a
[1, 2, 3, [4, 5], 6, 7]

use of lambda:
 processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
http://www.kuqin.com/diveinto_python_document/apihelper_lambda.html
good points: u can depart if logic from function


05/09/2012
#combine use of range() and len():
>>> a = ['Mary', 'had', 'a', 'little', 'lamb']
>>> for i in range(len(a)):
...     print i, a[i]
...
0 Mary
1 had
2 a
3 little
4 lamb
#Another way is to use enumerate():
>>> for i, v in enumerate(['tic', 'tac', 'toe']):
...     print i, v
...
0 tic
1 tac
2 toe
#To loop two or more sequence at the same time, use zip():
>>> questions = ['name', 'quest', 'favorite color']
>>> answers = ['lancelot', 'the holy grail', 'blue']
>>> for q, a in zip(questions, answers):
...     print 'What is your {0}?  It is {1}.'.format(q, a)
...
What is your name?  It is lancelot.
What is your quest?  It is the holy grail.
What is your favorite color?  It is blue.

#string.append() is more efficient than +
#  one reason could be append do not need new string, + does

#For function def The default value is evaluated only once.:
def f(a, L=[]):
    L.append(a)
    return L
print f(1)
print f(2)
print f(3)

will print:
[1]
[1, 2]
[1, 2, 3]
#Otherwise u can do it like this:
def f(a, L=None):
    if L is None:
       L= []
    L.append(a)
    return L

# u can unpack a list into a tuple by using *:
>>> range(3, 6)             # normal call with separate arguments
[3, 4, 5]
>>> args = [3, 6]
>>> range(*args)            # call with arguments unpacked from a list
[3, 4, 5]
# similiarly u can unpack a dictionary into a tuple by **:
>>> def parrot(voltage, state='a stiff', action='voom'):
...     print "-- This parrot wouldn't", action,
...     print "if you put", voltage, "volts through it.",
...     print "E's", state, "!"
...
>>> d = {"voltage": "four million", "state": "bleedin' demised", "action": "VOOM"}
>>> parrot(**d)
-- This parrot wouldn't VOOM if you put four million volts through it. E's bleedin' demised !

