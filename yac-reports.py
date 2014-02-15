from operator import attrgetter,itemgetter
import itertools as it
import copy,os
import sqlite3

def empty(x):
    return ''

def padspace(seq):
    return it.chain(seq, it.repeat(''))

def make_length_getter(attrname):
    def inner(a,attrname=attrname):
        return len(getattr(a,attrname))
    return inner
    
sess1len = make_length_getter('session_1')
sess2len = make_length_getter('session_2')
   


def assigned_sess_1(s):
    a_nbr = s.get_session_assignment_1()
    if a_nbr is None:
        return "Unassigned"
    a = authors[a_nbr]
    return "%s (%s)" % (a.name,a.nbr)

def assigned_room_1(s):
    a_nbr = s.get_session_assignment_1()
    if a_nbr is None:
        return "Unassigned"
    a = authors[a_nbr]
    return a.room

def assigned_sess_2(s):
    a_nbr = s.get_session_assignment_2()
    if a_nbr is None:
        return "Unassigned"
    a = authors[a_nbr]
    return "%s (%s)" % (a.name,a.nbr)

def assigned_room_2(s):
    a_nbr = s.get_session_assignment_2()
    if a_nbr is None:
        return "Unassigned"
    a = authors[a_nbr]
    return a.room

teacher_html = """<table border="0" width="90%%" align="center">
<tr><td colspan="5" align="center">2014 Young Authors Conference</td></tr>
<tr><td colspan="5" align="center"><hr></td></tr>
<tr><td align="left" colspan="5"><b>Teacher:</b> %s</td></tr>
<tr><td colspan="5">&nbsp;</td></tr>
<tr><th align="left">Name</th><th align="left">Session 1</th><th align="left">Room</th><th align="left">Session 2</th><th align="left">Room</th></tr>
%s
</table>
<div><pdf:nextpage /></div>
%s
"""
student_row_html = """<tr><td>%(name)s</td><td>%(auth1)s</td><td>%(room1)s</td><td>%(auth2)s</td><td>%(room2)s</td></tr>"""
    
student_dtl_html = """<table border="0" width="50%%" align="center">
<tr><td colspan="4" align="center">2014 Young Authors Conference</td></tr>
<tr><td colspan="4" align="center"><hr></td></tr>
<tr><td>Student:</td><td colspan="3">%(name)s</td></tr>
<tr><td>&nbsp;</td><td colspan="3">%(teacher)s - %(gradelvl)s grade</td></tr>
<tr><td colspan="4" align="center"><hr></td></tr>
<tr><td colspan="4"><h3>Session: 1</h3></td></tr>
<tr><td>Room: %(room1)s</td><td >&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Speaker:</td><td>%(auth1)s</td></tr>
<tr><td colspan="4" align="center"><hr></td></tr>
<tr><td colspan="4"><h3>Session: 2</h3></td></tr>
<tr><td>Room: %(room2)s</td><td>&nbsp;&nbsp;&nbsp;&nbsp;</td><td>Speaker:</td><td>%(auth2)s</td></tr>
</table><br><br><br><br><br>"""

conn = sqlite3.connect('data/yac.db3')
conn.row_factory = sqlite3.Row
base_html = open('report_base.html','r').read()

sql = """select 
s.name,s.teacher,s.grade,
a1.name as auth1,a1.room as room1,a2.name as auth2,a2.room as room2
from student s
left join author a1 on (s.sess_1 = a1.id)
left join author a2 on (s.sess_2 = a2.id)
order by s.grade,s.teacher,s.name;"""

students_by_teacher = conn.execute(sql).fetchall()
for t_key,t_iter in it.groupby(students_by_teacher,itemgetter('teacher')):
    t_list = list(t_iter)
    html=[]
    dtl = []
    cnt = 0
    for s in t_list:
        cnt += 1
        temp = {}
        temp['name'] = s['name']
        temp['teacher'] = s['teacher']
        temp['gradelvl'] = s['grade']
        temp['auth1'] = s['auth1']
        temp['room1'] = s['room1']
        temp['auth2'] = s['auth2']
        temp['room2'] = s['room2']
        html.append(student_row_html % temp)
        dtl.append(student_dtl_html % temp)
        if cnt % 4 == 0:
            dtl.append("<div><pdf:nextpage /></div>")
    student_rows = "\n".join(html)
    student_dtl = "\n".join(dtl) 
    all = teacher_html % (t_key,student_rows,student_dtl)

    f = open('reports/yac-2014-teacher-%s.html' % (t_key,),'w')
    f.write(base_html % (all,))
    f.close()
    os.system('pisa reports/yac-2014-teacher-%s.html' % (t_key,))

# MASTER

master_html = """<table border="0" width="90%%" align="center">
<tr><td colspan="6" align="center">2014 Young Authors Conference</td></tr>
<tr><td colspan="6" align="center"><hr></td></tr>
<tr><td colspan="6">&nbsp;</td></tr>
<tr><th align="left">Student Name</th><th align="left">Teacher</th><th align="left">Session 1</th><th align="left">Room</th><th align="left">Session 2</th><th align="left">Room</th></tr>
%s
</table>
"""
master_row_html = """<tr><td>%(name)s</td><td>%(teacher)s (%(grade)s)</td><td>%(auth1)s</td><td>%(room1)s</td><td>%(auth2)s</td><td>%(room2)s</td></tr>"""


sql = """select 
s.name,s.teacher,s.grade,
a1.name as auth1,a1.room as room1,a2.name as auth2,a2.room as room2
from student s
left join author a1 on (s.sess_1 = a1.id)
left join author a2 on (s.sess_2 = a2.id)
order by s.name;"""

students_by_name = conn.execute(sql).fetchall()
html=[]
dtl = []
for s in students_by_name:
    temp = {}
    temp['name'] = s['name']
    temp['teacher'] = s['teacher']
    temp['grade'] = s['grade']
    temp['auth1'] = s['auth1']
    temp['room1'] = s['room1']
    temp['auth2'] = s['auth2']
    temp['room2'] = s['room2']
    dtl.append(master_row_html % temp)
student_dtl = "\n".join(dtl) 
all = master_html % (student_dtl)

f = open('reports/yac-2014-Master.html','w')
f.write(base_html % (all,))
f.close()
os.system('pisa reports/yac-2014-Master.html')


# HOST
host_html = """<table border="0" width="90%%" align="center">
<tr><td colspan="4" align="center">2014 Young Authors Conference</td></tr>
<tr><td colspan="4" align="center"><hr></td></tr>
<tr><td colspan="4">&nbsp;</td></tr>
<tr><td colspan="4"><b>Author: %s</b></td></tr>
<tr><td colspan="4"><b>Host: %s</b></td></tr>
<tr><td colspan="4"><b>Room: %s</b></td></tr>
<tr><th width="5%%">&nbsp;</th><th align="left">Session 1</th><th>&nbsp;&nbsp;</th><th align="left">Session 2</th></tr>
%s
</table>
"""
host_row_html = """<tr><td>%(cnt)s</td><td>%(col_1)s</td><td>&nbsp;</td><td>%(col_2)s</td></tr>"""

sql_a = """select id,name,last_name,room,host from author order by id;"""
sql_1 = """select name,grade
from student where sess_1 = ?
order by name;"""
sql_2 = """select name,grade
from student where sess_2 = ?
order by name;"""

authors = conn.execute(sql_a).fetchall()

for a_rec in authors:
    sess_1 = conn.execute(sql_1,[str(a_rec['id'])]).fetchall()
    sess_2 = conn.execute(sql_2,[str(a_rec['id'])]).fetchall()
    maxcnt = max(len(sess_1),len(sess_2))
    rows=[]
    for cnt in range(1,maxcnt+1):
        temp = {}
        temp['cnt'] = cnt 
        try:
            s1 = tuple(sess_1[cnt-1])
            temp['col_1'] = "%s (%s)" % s1
        except IndexError:
            temp['col_1'] = "&nbsp;"
        try:
            s2 = tuple(sess_2[cnt-1])
            temp['col_2'] = "%s (%s)" % s2
        except IndexError:
            temp['col_2'] = "&nbsp;"
        rows.append(host_row_html % temp)
    rows = "\n".join(rows)
    all = host_html % (a_rec['name'],a_rec['host'],a_rec['room'],rows)

    f = open('reports/yac-2014-Host-%s.html' % (a_rec['last_name'],),'w')
    f.write(base_html % (all,))
    f.close()
    os.system('pisa reports/yac-2014-Host-%s.html' % (a_rec['last_name'],))
