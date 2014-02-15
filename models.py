from flask import g
import sqlite3,random
from collections import defaultdict
#FULL = 18 
FULL = 20
HIGH_GRADE_COUNT = 10 
#HIGH_GRADE = '5'
HIGH_GRADE = '4'

#SHUFFLE_TYPE = 'none'
#SHUFFLE_TYPE = 'all'
SHUFFLE_TYPE = '4then3'

def connect_db():
    conn = sqlite3.connect('data/yac.db3')
    conn.row_factory = sqlite3.Row
    return conn

def clear_db():
    cur = g.db.execute('delete from student;')
    cur = g.db.execute("delete from sqlite_sequence where name='student';")
    cur = g.db.execute('delete from author;')
    cur = g.db.execute('delete from teacher;')
    cur = g.db.execute('delete from changes;')
    g.db.commit()

def record_counts():
    cur = g.db.execute('select complete,error from student;')
    inc = com = err = tot = 0
    for row in cur:
        tot += 1
        if row['error'] == 'Y':
            err += 1
        if row['complete'] == "Y":
            com += 1
        else:
            inc += 1
    student_cnt = (inc,com,err,tot)
    cur = g.db.execute('select count(*) from teacher;')
    teacher_cnt = cur.fetchone()[0]
    cur = g.db.execute('select id,name,sess_1_cnt,sess_2_cnt,choice_count_1,choice_count_2,choice_count_3,choice_count_4,choice_count_5 from author;')
    author_stats = cur.fetchall()
    return student_cnt,teacher_cnt,author_stats

def load_author_data(data,skip=True):
    cnt = 0
    first = True
    for line in data.split('\n'):
        if skip and first:
            first = False
            continue
        line = line.rstrip('\r')
        if not line:
            continue
        cnt += 1
        flds = line.split('\t')
        last_name = flds[1].split()[-1]
        flds.append(last_name)
        if flds:
            g.db.execute('insert into author (id,name,room,host,last_name) values(?,?,?,?,?);',flds)
    g.db.commit()
    return cnt

def get_author_ids():
    cur = g.db.execute('select id from author;')
    return set(rec['id'] for rec in cur.fetchall())

def update_choice_counts(authors,choices):
    for i,c in enumerate(choices):
        if c not in authors:
            authors[c] = [0,0,0,0,0]
        authors[c][i] += 1

def int_or_zero(val):
    try:
        out = int(val)
    except ValueError:
        out = 0
    return out

def load_student_data(data,skip=True):
    author_ids = get_author_ids()
    cnt = 0
    first = True
    teachers = set()
    authors = {}
    session_counts = defaultdict(int)
    for line in data.split('\n'):
        if skip and first:
            first = False
            continue
        line = line.rstrip('\r')
        if not line:
            continue
        cnt += 1
        flds = line.split('\t')
        #grade = flds[0]
        grade,teacher,name,c1,c2,c3,c4,c5,s1,s2,note = flds
        if flds:
            error_flag = 'N'
            choices = [int_or_zero(c) for c in (c1,c2,c3,c4,c5)]
            for c in choices:
                if c not in author_ids:
                    error_flag = 'Y'
            update_choice_counts(authors,choices)
            if s1.strip():
                sess_1_lock = 'Y'
                session_counts["%s_1" % (s1,)] += 1
                if grade == HIGH_GRADE:
                    session_counts["%s_1_h" % (s1,)] += 1
                if int(s1) not in author_ids:
                    error_flag = 'Y'
            else:
                s1 = 0
                sess_1_lock = 'N'
            if s2.strip():
                sess_2_lock = 'Y'
                session_counts["%s_2" % (s2,)] += 1
                if grade == HIGH_GRADE:
                    session_counts["%s_2_h" % (s2,)] += 1
                if int(s2) not in author_ids:
                    error_flag = 'Y'
            else:
                s2 = 0
                sess_2_lock = 'N'
            if sess_1_lock == 'Y' and sess_2_lock == 'Y':
                complete = 'Y'
            else:
                complete = 'N'
            #flds.extend([sess_1_lock,sess_2_lock,complete,error_flag])
            rec = [grade,teacher,name,note,c1,c2,c3,c4,c5,s1,s2,sess_1_lock,sess_2_lock,complete,error_flag]
            g.db.execute('insert into student (grade,teacher,name,note,choice_1,choice_2,choice_3,choice_4,choice_5,sess_1,sess_2,sess_1_lock,sess_2_lock,complete,error) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);',rec)
            if teacher not in teachers:
                teachers.add(flds[1])
                g.db.execute('insert into teacher (name) values(?);',[teacher])
    for a,cc in authors.items():
        # also update session counts for locked sessions
        cnt_1 = session_counts.get("%s_1" % (a,),0)
        cnt_1_h = session_counts.get("%s_1_h" % (a,),0)
        cnt_2 = session_counts.get("%s_2" % (a,),0)
        cnt_2_h = session_counts.get("%s_2_h" % (a,),0)
        update_author_counts(a,cc,cnt_1,cnt_1_h,cnt_2,cnt_2_h)

    g.db.commit()
    update_all_scores()
    return cnt

def update_author_counts(a_id,choice_counts,sess_cnt_1,sess_cnt_1_high,sess_cnt_2,sess_cnt_2_high):
    sql = "update author set choice_count_1=?,choice_count_2=?,choice_count_3=?,choice_count_4=?,choice_count_5=?,sess_1_cnt=?,sess_1_high_cnt=?,sess_2_cnt=?,sess_2_high_cnt=? where id = ?;"
    cur = g.db.execute(sql,choice_counts+[sess_cnt_1,sess_cnt_1_high,sess_cnt_2,sess_cnt_2_high]+[a_id])
    g.db.commit()

def get_student_choices(sid):
    sql = """select s.id as s_id,s.name as name,sess_1,sess_1_lock,sess_2,sess_2_lock,complete,grade,
    choice_1,a1.sess_1_cnt as c1_sess_1,a1.sess_1_high_cnt as c1_sess_1_high,a1.sess_2_cnt as c1_sess_2,a1.sess_2_high_cnt as c1_sess_2_high,
    choice_2,a2.sess_1_cnt as c2_sess_1,a2.sess_1_high_cnt as c2_sess_1_high,a2.sess_2_cnt as c2_sess_2,a2.sess_2_high_cnt as c2_sess_2_high,
    choice_3,a3.sess_1_cnt as c3_sess_1,a3.sess_1_high_cnt as c3_sess_1_high,a3.sess_2_cnt as c3_sess_2,a3.sess_2_high_cnt as c3_sess_2_high,
    choice_4,a4.sess_1_cnt as c4_sess_1,a4.sess_1_high_cnt as c4_sess_1_high,a4.sess_2_cnt as c4_sess_2,a4.sess_2_high_cnt as c4_sess_2_high,
    choice_5,a5.sess_1_cnt as c5_sess_1,a5.sess_1_high_cnt as c5_sess_1_high,a5.sess_2_cnt as c5_sess_2,a5.sess_2_high_cnt as c5_sess_2_high
    from student s
    left join author a1 on (s.choice_1 = a1.id)
    left join author a2 on (s.choice_2 = a2.id)
    left join author a3 on (s.choice_3 = a3.id)
    left join author a4 on (s.choice_4 = a4.id)
    left join author a5 on (s.choice_5 = a5.id)
    where s.id =?;"""
    cur = g.db.execute(sql,[sid,])
    return cur.fetchone()

def get_student_list_for_auto_assign():
    if SHUFFLE_TYPE in ('all','none'):
        cur = g.db.execute("select id from student where error <> 'Y' order by id;")
        students = [rec['id'] for rec in cur.fetchall()]
        if SHUFFLE_TYPE == 'all':
            random.shuffle(students)
    elif SHUFFLE_TYPE == '4then3':
        student_3 = [rec['id'] for rec in g.db.execute("select id from student where error <> 'Y' and grade = '3';").fetchall()]
        student_4 = [rec['id'] for rec in g.db.execute("select id from student where error <> 'Y' and grade = '4';").fetchall()]
        random.shuffle(student_3)
        random.shuffle(student_4)
        students = student_4 + student_3
    return students


def demux_choice(choice,student):
    author = student['choice_%i' % (choice,)]
    if student['sess_1']:
        count_1 = None
        count_1_high = None
    else:
        count_1 = student['c%i_sess_1' % (choice,)]
        count_1_high = student['c%i_sess_1_high' % (choice,)]
    if student['sess_2']:
        count_2 = None
        count_2_high = None
    else:
        count_2 = student['c%i_sess_2' % (choice,)]
        count_2_high = student['c%i_sess_2_high' % (choice,)]
    return author,count_1,count_1_high,count_2,count_2_high

def assign_session_auto(s_id,grade,a_id,sess,new_count,new_high_cnt,add_msg):
    add_msg("I","student %s author %s session %i count %i" % (s_id,a_id,sess,new_count))
    #print "student",s_id,"author",a_id,"session",sess,"session count",new_count
    sql = "update student set sess_%i = ? where id=?" % (sess,)
    cur = g.db.execute(sql,[a_id,s_id])
    sql = "update author set sess_%i_cnt=?,sess_%i_high_cnt=? where id=?" % (sess,sess)
    cur = g.db.execute(sql,[new_count,new_high_cnt,a_id])
    g.db.commit()

def update_author_assignment(sess,a_id,grade,delta):
    set_clauses = []
    sess = int(sess)
    set_clauses.append('sess_%i_cnt=sess_%i_cnt + ?' % (sess,sess))
    values = [delta,]
    if grade == HIGH_GRADE:
        set_clauses.append('sess_%i_high_cnt=sess_%i_high_cnt + ?' % (sess,sess))
        values.append(delta)
    values.append(a_id)
    set_clauses = ",".join(set_clauses)
    sql = "update author set %s where id=?" % (set_clauses)
    cur = g.db.execute(sql,values)

def chg_history(s_id,sess,prev,new):
    g.db.execute('insert into changes (s_id,sess,prev,new) values(?,?,?,?);',[s_id,sess,prev,new])
    g.db.commit()

def chg_assignments(s_id,grade,s1,s1prev,s2,s2prev):
    s1 = s1.lstrip('0')
    s1prev = s1prev.lstrip('0')
    s2 = s2.lstrip('0')
    s2prev = s2prev.lstrip('0')
    if s1 == s1prev and s2 == s2prev:
        return "Nothing to change",'OK'
    set_clauses = []
    if s1 != s1prev:
        set_clauses.append('sess_1=%s' % str(s1))
    if s2 != s2prev:
        set_clauses.append('sess_2=%s' % str(s2))
    if s1 and s2:
        set_clauses.append("complete='Y'")
    else:
        set_clauses.append("complete='N'")
    set_clauses = 'set %s' % (",".join(set_clauses),)
    sql = 'update student %s where id = ?' % set_clauses
    cur = g.db.execute(sql,[s_id])
    if s1 != s1prev:
        chg_history(s_id,'1',s1prev,s1)
        update_author_assignment('1',s1,grade,1)
        update_author_assignment('1',s1prev,grade,-1)
    if s2 != s2prev:
        chg_history(s_id,'2',s2prev,s2)
        update_author_assignment('2',s2,grade,1)
        update_author_assignment('2',s2prev,grade,-1)

    g.db.commit()
    update_score(s_id)
    return '','OK'

def update_score(s_id):
    sql = 'select * from student where id = ?;'
    upd_sql = 'update student set score = ? where id = ?'
    rec = g.db.execute(sql,[s_id]).fetchone()
    choices = (rec['choice_1'],rec['choice_2'],rec['choice_3'],rec['choice_4'],rec['choice_5'])
    sessions = (rec['sess_1'],rec['sess_2'])
    score = calc_score(choices,sessions)
    g.db.execute(upd_sql,[score,rec['id']])
    g.db.commit()

def update_all_scores():
    sql = 'select * from student;'
    upd_sql = 'update student set score = ? where id = ?'
    for rec in g.db.execute(sql):
        choices = (rec['choice_1'],rec['choice_2'],rec['choice_3'],rec['choice_4'],rec['choice_5'])
        sessions = (rec['sess_1'],rec['sess_2'])
        score = calc_score(choices,sessions)
        g.db.execute(upd_sql,[score,rec['id']])
    g.db.commit()

def calc_score(choices,sessions):
    score_lookup = dict(zip(choices,range(1,6)))
    score = 0
    for s in sessions:
        if s:
            score += score_lookup.get(s,10)
    return score

def mark_as_complete():
    sql = "update student set complete = 'Y' where sess_1 <> 0 and sess_2 <> 0;"
    cur = g.db.execute(sql)
    g.db.commit()

def auto_assign():
    messages = []
    def add_msg(mtype,msg,messages=messages):
        print mtype,msg
        messages.append((mtype,msg))

    students = get_student_list_for_auto_assign()
    for datapass in (1,2):
        #add_msg('D','pass %i' % datapass)
        for s_id in students:
            student = get_student_choices(s_id)
            if student['complete'] == 'Y':
                #add_msg('D','student %i is complete' % s_id)
                continue
            for i in range(1,6):
                author,count_1,count_1_high,count_2,count_2_high = demux_choice(i,student)
                #add_msg('D','student %i trying choice %i which is %i (%s,%s)' % (s_id,i,author,str(count_1),str(count_2)))
                if author in (student['sess_1'],student['sess_2']):
                    #add_msg('D',"student %i already in a session for author %i" % (s_id,author))
                    continue # this author has already been chosen
                if (count_1 is not None and 
                    count_1 < FULL and 
                    ((student['grade'] != HIGH_GRADE) or 
                     (student['grade'] == HIGH_GRADE and 
                      count_1_high < HIGH_GRADE_COUNT))):
                    if student['grade'] == HIGH_GRADE:
                        count_1_high += 1
                    assign_session_auto(s_id,student['grade'],author,1,count_1 + 1,count_1_high,add_msg)
                    break
                if (count_2 is not None and 
                    count_2 < FULL and 
                    ((student['grade'] != HIGH_GRADE) or 
                     (student['grade'] == HIGH_GRADE and 
                      count_2_high < HIGH_GRADE_COUNT))):
                    if student['grade'] == HIGH_GRADE:
                        count_2_high += 1
                    assign_session_auto(s_id,student['grade'],author,2,count_2 + 1,count_2_high,add_msg)
                    #grade
                    break
                #if count_2 is not None and count_2 < FULL:
                #    assign_session_auto(s_id,student['grade'],author,2,count_2 + 1,add_msg)
                #    break
                continue # no space left in this choice, on to next 
            else:
                add_msg("E","%s (%s) can not be assigned." % (student['name'],student['grade']))
    mark_as_complete()
    update_all_scores()
    return messages

def get_student_data_for_assignment_table():
    def zp(val):
        if val:
            return str(val).zfill(2)
        else:
            return ''
    g.db.create_function('zp',1,zp)
    sql = """select id,complete,name,grade,teacher,zp(sess_1) as sess_1,sess_1_lock,zp(sess_2) as sess_2,sess_2_lock,zp(choice_1) as choice_1,zp(choice_2) as choice_2,zp(choice_3) as choice_3,zp(choice_4) as choice_4,zp(choice_5) as choice_5,zp(score) as score from student order by id;"""
    cur = g.db.execute(sql)
    return cur.fetchall()

def get_author_data_for_assignment_table():
    sql = """select id,name,last_name,sess_1_cnt,sess_1_high_cnt,sess_2_cnt,sess_2_high_cnt from author order by id;"""
    cur = g.db.execute(sql)
    return cur.fetchall()

COLUMNS = []
# heading, filter widget
COLUMNS.append(("complete","Complete",10,'input',3))
COLUMNS.append(("name","Name",10,'input',20))
COLUMNS.append(("sess_1","Sess 1",10,'input',5))
COLUMNS.append(("sess_1_lock","S1 Lock",10,'input',5))
COLUMNS.append(("sess_2","Sess 2",10,'input',5))
COLUMNS.append(("sess_2_lock","S2 Lock",10,'input',5))
COLUMNS.append(("score","Score",10,'input',3))
COLUMNS.append(("choices","Choices",10,'input',10))
COLUMNS.append(("grade","Grade",10,'input',3))
COLUMNS.append(("teacher","Teacher",10,'input',10))
COLUMNS.append(("id","ID",0,'',0))

def get_table_names():
    return [x[0] for x in COLUMNS]

def get_table_headings():
    return [x[1] for x in COLUMNS]

def get_table_filters():
    return [(x[0],x[-2],x[-1]) for x in COLUMNS]

