import models
from flask import Flask,url_for,g,render_template,request,jsonify
import json
app = Flask(__name__)
app.debug = True

@app.before_request
def before_request():
    g.db = models.connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route("/")
def index():
    data = {}
    sc,tc,a_stats = models.record_counts()
    data['s_inc_cnt'],data['s_com_cnt'],data['s_err_cnt'],data['s_cnt'] = sc
    data['teacher_cnt'] = tc
    data['author_stats'] = a_stats
    data['author_cnt'] = len(a_stats)
    return render_template('index.html',**data)

@app.route("/assign/")
def assign_index():
    data = {}
    data['authors'] = models.get_author_data_for_assignment_table()
    data['AUTHOR_IDS'] = json.dumps([a['id'] for a in data['authors']])
    data['headings'] = models.get_table_headings()
    data['filters'] = models.get_table_filters()
    data['FULL'] = models.FULL
    data['HIGH_GRADE_COUNT'] = models.HIGH_GRADE_COUNT
    data['HIGH_GRADE'] = models.HIGH_GRADE

    return render_template('assign_index.html',**data)

@app.route("/assign/ajax/")
def assign_ajax():
    students = models.get_student_data_for_assignment_table()
    col_names = models.get_table_names()
    aaData = []
    out = {"aaData":aaData}
    for rec in students:
        outrec = []
        rec = dict(rec)
        for name in col_names:
            if name == 'choices':
                indexes = [str(i) for i in range(1,6)]
                choices = ",".join(rec.get('choice_'+i) for i in indexes) 
                if choices == ',,,,':
                    choices = ''
                outrec.append(choices)
            else:
                outrec.append(rec.get(name))
        aaData.append(outrec)
    return jsonify(out)

@app.route("/assign/auto/")
def auto_assign():
    messages = models.auto_assign()
    with open('data/autoassign.log','w') as f:
        for m in messages:
            f.write("%s - %s\n" % m)
    return render_template('auto_assign.html',messages=messages)

@app.route("/assign/change/")
def chg_student_assign():
    print "chg_student_assign"
    s_id = request.values.get('s_id')
    grade = request.values.get('grade')
    sess_1 = request.values.get('sess_1')
    sess_1_prev = request.values.get('sess_1_prev')
    sess_2 = request.values.get('sess_2')
    sess_2_prev = request.values.get('sess_2_prev')
    err,message = models.chg_assignments(s_id,grade,sess_1,sess_1_prev,sess_2,sess_2_prev)
    return jsonify({'err':err,'message':message})

@app.route("/data/")
def data_index():
    return render_template('data_index.html')

@app.route("/data/cleardb/")
def clear_db():
    models.clear_db()
    data = {}
    data['message'] = 'Database has been cleared'
    data['return_url'] = url_for('data_index')
    data['return_url_text'] = 'Back to Data'
    return render_template('message.html',**data)

@app.route("/data/sampledata/")
def sample_data():
    models.clear_db()
    with open('data/authors.txt','r') as f:
        author_data = f.read()
        cnt = models.load_author_data(author_data)

    with open('data/students.txt','r') as f:
        student_data = f.read()
        cnt = models.load_student_data(student_data)
    data = {}
    data['message'] = 'Sample data loaded.'
    data['return_url'] = url_for('index')
    data['return_url_text'] = 'Return to Home.'
    return render_template('message.html',**data)

@app.route("/data/loadauthors/",methods=['POST'])
def load_authors():
    if request.method == 'POST':
        data = request.form['data']
        cnt = models.load_author_data(data)
    data = {}
    data['message'] = '%i Authors loaded.' % (cnt,)
    data['return_url'] = url_for('data_index')
    data['return_url_text'] = 'Back to Data page.'
    return render_template('message.html',**data)

@app.route("/data/loadstudents/",methods=['POST'])
def load_students():
    if request.method == 'POST':
        data = request.form['data']
        cnt = models.load_student_data(data)
    data = {}
    data['message'] = '%i Students loaded.' % (cnt,)
    data['return_url'] = url_for('data_index')
    data['return_url_text'] = 'Back to Data page.'
    return render_template('message.html',**data)

@app.route("/inquiry/author/<int:a_id>")
def inq_author(a_id):
    return render_template('inq_author.html')

@app.route("/inquiry/teacher/<tname>")
def inq_teacher(tname):
    return render_template('inq_teacher.html')

@app.route("/inquiry/student/<int:s_id>")
def inq_author(s_id):
    return render_template('inq_student.html')

@app.route("/report/")
def report_index():
    return render_template('report_index.html')

if __name__ == "__main__":
    app.run()
