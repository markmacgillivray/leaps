
from flask import Blueprint, request, flash, abort, render_template, redirect
from flask_login import current_user

import time

from flask_weasyprint import HTML, render_pdf

from portality.core import app
import portality.models as models
from portality.view.leaps.forms import dropdowns
import portality.util as util

from datetime import datetime, date


blueprint = Blueprint('interviews', __name__)


# restrict everything in admin to logged in users
@blueprint.before_request
def restrict():
    adminsettings = models.Account.pull(app.config['SUPER_USER'][0]).data.get('settings',{})
    if not adminsettings.get('schools_unis',False) and not current_user.view_admin:
        return render_template('leaps/admin/closed.html')
    if current_user.is_anonymous:
        return redirect('/account/login?next=' + request.path)
    dp = current_user.data['last_updated'].split(' ')[0].split('-')
    if date(int(dp[0]),int(dp[1]),int(dp[2])) < date(2018,8,1) and current_user.data.get('agreed_policy',False) == True:
        current_user.data['previously_agreed_policy'] = True
        current_user.data['agreed_policy'] = False
        current_user.save()
    if not current_user.agreed_policy and not current_user.view_admin:
        return redirect('/account/policy?next=' + request.path)
    if not current_user.perform_interviews:
        abort(401)
    

# view students of the logged-in interviewer
@blueprint.route('/')
def index():
    interviewers = []
    users = models.Account.query(q={"query":{"query_string":{"query": "perform_interviews:*"}},"sort":{'id.exact':{'order':'asc'}}, "size":100000})
    if users['hits']['total'] != 0:
        for i in users['hits']['hits']:
            if i.get('_source',{}).get('perform_interviews',False): interviewers.append(i['_source']['id'])

    interviewer = current_user.perform_interviews
    qry = {'sort':[{'created_date.exact':{'order':'desc'}}],'query':{'bool':{'must':[{'term':{'archive.exact':'current'}}, {'term':{'status.exact':'allocated_to_interviewer'}}]}},'size':10000}
    if not isinstance(interviewer,bool):
        qry['query']['bool']['must'].append({'term':{'interviewer.exact':interviewer}})
    q = models.Student().query(q=qry)
    students = [i['_source'] for i in q.get('hits',{}).get('hits',[])]
    return render_template('leaps/interviews/index.html', students=students, interviewers=interviewers)

@blueprint.route('/allocate')
def allocate():
    counter = 0
    interviewer = current_user.perform_interviews
    if request.values.get('students', False):
        if request.values.get('interviewer',False): interviewer = request.values['interviewer']
        if interviewer and not isinstance(interviewer,bool):
            for sid in request.values['students'].split(','):
                student = models.Student.pull(sid)
                if student is not None and student.data.get('interviewer', False) != interviewer and not student.data.get('interview', {}).get('status', False):
                    student.data['interviewer'] = interviewer
                    student.data['status'] = 'allocated_to_interviewer'
                    student.save()
                    counter += 1
            flash(str(counter) + ' additional students have been allocated to ' + interviewer, 'success')
            return redirect('/interviews')
        else:
            flash('You are not logged in as a user who can perform and/or manage interviews', 'success')

    qry = {'sort':[{'last_name.exact':{'order':'asc'}}],'query':{'bool':{'minimum_should_match': 1, 'should': [], 'must':[{'term':{'archive.exact':'current'}}]}},'size':10000}
    # "not_eligible_interviewed", "not_eligible_not_interviewed", 
    # "allocated_to_interviewer", "interviewed", "query", "paes_requested", "paes_in_progress", "paes_complete", "complete"
    for s in ["new", "absent", "not_applying_interviewed", "not_applying_not_interviewed"]:
        qry['query']['bool']['should'].append({'term':{'status.exact':s}})
    if request.values.get('school',False): qry['query']['bool']['must'].append({'term':{'school.exact': request.values['school']}})
    if not isinstance(interviewer,bool):
        qry['query']['bool']['must_not'] = [{'term':{'interviewer.exact':interviewer}}]
    q = models.Student().query(q=qry)
    students = [i['_source'] for i in q.get('hits',{}).get('hits',[])]
    return render_template('leaps/interviews/allocate.html', students=students, schools=dropdowns('school'), selected_school=request.values.get('school',False))

@blueprint.route('/<sid>.pdf')
def interviewPDF(sid):
    interviewer = current_user.perform_interviews
    student = models.Student.pull(sid)
    if student is None:
        abort(404)
    elif interviewer != True and interviewer != student.data.get('interviewer') and not current_user.view_admin:
        abort(401)
    else:
        thepdf = render_template('leaps/admin/student_pdf', students=[student.data])
        return render_pdf(HTML(string=thepdf))

@blueprint.route('/<sid>/form', methods=['GET', 'POST'])
def interviewForm(sid):
    student = models.Student.pull(sid)
    interviewer = current_user.perform_interviews
    
    selections={
        "schools": dropdowns('school'),
        "advancedsubjects": dropdowns('advancedsubject'),
        "institutions": dropdowns('institution'),
        "advancedlevels": dropdowns('advancedlevel')
    }

    if student is None:
        abort(404)
    elif interviewer != True and interviewer != student.data.get('interviewer') and not current_user.view_admin:
        abort(401)
    elif request.method == 'GET':
        return render_template('leaps/interviews/form.html', student=student, selections=selections)
    elif request.form.get('submit_reference_notes', False):
        if not student.data.get('interview',False): student.data['interview'] = {}
        student.data['interview']['pre_interview_notes'] = request.form['pre_interview_notes']
        student.save()
        flash('The pre-interview notes have been saved.', 'success')
        return render_template('leaps/interviews/form.html', student=student, selections=selections)
    elif request.form.get('submit_checker_notes', False):
        if student.data.get('interview',{}).get('status',False):
            student.data['interview']['leaps_admin_notes'] = request.form['leaps_admin_notes']
            student.save()
            flash('The admin notes have been saved.', 'success')
        else:
            flash('Admin notes cannot be added until some data is saved above.', 'success')
        return render_template('leaps/interviews/form.html', student=student, selections=selections)
    else:
        # save the form into the student record
        '''if not student.data.get('interview',False):
            student.data['interview'] = {"status": "saved", "applications": [], "form_date": datetime.now().strftime("%Y-%m-%d %H%M")}
        else:
            ed = student.data['interview'].get('emailed_date', False)
            cd = student.data['interview'].get('completed_date', False)
            st = student.data['interview'].get('status', 'saved')
            student.data['interview'] = {"status": st, "form_date": student.data['interview']['form_date'], "updated_date": datetime.now().strftime("%Y-%m-%d %H%M")}
            if ed != False: student.data['interview']['emailed_date'] = ed
            if cd != False: student.data['interview']['completed_date'] = cd'''
        if not student.data.get('interview',False): student.data['interview'] = {}
        if not student.data['interview'].get('status',False): student.data['interview']['status'] = 'saved'
        if not student.data['interview'].get('form_date',False): 
            student.data['interview']['form_date'] = datetime.now().strftime("%Y-%m-%d %H%M")
        else:
            student.data['interview']['updated_date'] = datetime.now().strftime("%Y-%m-%d %H%M")
        # reset this each time and refill from the form inputs, which will replicate any previous ones, so deletions can also be tracked easily
        student.data['interview']['applications'] = []
        for k,v in enumerate(request.form.getlist('application_subject')):
            if v is not None and len(v) > 0 and v != " ":
                appn = {
                    "subject": v,
                    "institution": request.form.getlist('application_institution')[k],
                    "level": request.form.getlist('application_level')[k]
                }
                student.data["interview"]["applications"].append(appn)
        for field in request.form.keys():
            if not field.startswith('submit') and not field.startswith('application_'):
                val = request.form[field]
                if val == "yes" or val == "on":
                    val = True
                elif val == "no" or val == "off":
                    val = False
                if field in ['update_email', 'update_mobile']:
                    wf = 'email' if field == 'update_email' else 'mobile_phone'
                    if val != student.data.get(wf,False):
                        student.data[wf] = val
                        student.data['interview'][field] = val
                else:
                    student.data['interview'][field] = val
            elif field in ['submit_and_complete'] and not student.data['interview'].get('completed_date', False):
                student.data['interview']['completed_date'] = datetime.now().strftime("%d/%m/%Y")
                student.data['interview']['status'] = 'complete'
        student.save()
        flash('The post-interview form has been saved.', 'success')
        return render_template('leaps/interviews/form.html', student=student, selections=selections)
        
@blueprint.route('/<sid>/absent', methods=['GET', 'POST'])
def interviewAbsent(sid):
    student = models.Student.pull(sid)
    interviewer = current_user.perform_interviews
    if student is None:
        abort(404)
    elif interviewer != True and interviewer != student.data.get('interviewer') and not current_user.view_admin:
        abort(401)
    else:
        student.data['status'] = 'absent'
        del student.data['interviewer']
        student.save()
        flash('The student has been recorded as absent', 'success')
        return redirect('/interviews')


# print a PAE form for a student
@blueprint.route('/<sid>/plan.pdf')
def interviewPlanPDF(sid,giveback=False):
    try:
        sidtest = sid.data.get('interviewer',False)
        student = sid
    except:
        student = models.Student.pull(sid)
    interviewer = current_user.perform_interviews
    if student is None: 
        abort(404)
    elif interviewer != True and interviewer != student.data.get('interviewer') and not current_user.view_admin:
        abort(401)
    else:
        thepdf = render_template('leaps/admin/student_action_plan', record=student)
        if giveback:
            return HTML(string=thepdf).write_pdf()
        else:
            return render_pdf(HTML(string=thepdf))



# email an interview form to a student
@blueprint.route('/<sid>/email')
def interviewEmail(sid):
    if current_user.do_admin:
        if sid == "unemailed":
            # get all the interviews that have action plans completed but not yet emailed
            interviews = _get_interviews_awaiting_email()
            if 's' in request.values: interviews = interviews[0:int(request.values['s'])]
            for sn in interviews:
                time.sleep(1)
                student = models.Student.pull(sn['id'])
                _email_interview(student, False)
            time.sleep(1)
            flash(str(len(interviews)) + ' interviews were emailed','success')
            return redirect('/admin')
        else:
            student = models.Student.pull(sid)
            if student is None:
                abort(404)
            else:
                _email_interview(student)
                return redirect('/admin')
    else:
        abort(401) 
           

def _email_interview(student, flashable=True):
    try:
        fro = app.config['LEAPS_EMAIL']
        to = [app.config['LEAPS_EMAIL']]
        #if app.config.get('ADMIN_EMAIL',False):
        #    to.append(app.config['ADMIN_EMAIL'])
        if student.data.get('email', False):
            to.append(student.data['email'])

        try:
            studentname = student.data['first_name'] + " " + student.data['last_name']
            #studentname = studentname.encode("ascii","ignore")
            if not all(ord(char) < 128 for char in studentname):
                studentname = 'student'
        except:
            studentname = 'student'
        text = 'Dear ' + studentname + ',\n\n'

        school = models.School.pull_by_name(student.data['school'])
        if school is not None:
            foundone = False
            for contact in school.data.get('contacts',[]):
                if contact.get('email',False):
                    to.append(contact['email'])
                    if not foundone:
                        foundone = True
                        text += '( and copied to school contact '
                    else:
                        text += ', '
                    if contact.get('name',"") != "":
                        text += contact['name']
                    else:
                        text += contact['email']
            if foundone:
                text += " )\n\n"

        text += '''
Thank you for attending your recent LEAPS interview. We hope you found it helpful. Please find
attached a copy of the action plan that your interviewer has prepared for you. It should reflect the
conversation that you had in your interview, and give you some steps to help you move forward with
your plans.

Your help please - complete below survey on how you feel about applying to uni / college (and enter prize draw for thirty pounds Amazon voucher!)

LEAPS want to explore the effectiveness of the LEAPS Pre-UCAS 1:1 Interview,
and we ask for your help to do this! We invite you to complete this short online questionnaire to help us gather a sense of
how LEAPS-eligible pupils feel about applying to university shortly after their LEAPS
Pre-UCAS Interview.

The questionnaire should take no more than 5 minutes to complete. Completing the
questionnaire allows us to make sure LEAPS support is as effective as possible for
future LEAPS pupils. You can complete the questionnaire here: 

https://app.onlinesurveys.jisc.ac.uk/s/edinburgh/leaps-pre-ucas-interviews-2025-post-interview-questionnaire-1

(You might have completed a questionnaire before your interview - if so, thank you! We
ask you to also complete this questionnaire so we can find out more about the impact of
your interview. Don't worry if you didn't complete a previous questionnaire - we still ask
you to complete this one!).

Please remember LEAPS is always available should you need any more help as you go forward,

Good luck and best wishes

The LEAPS TEAM'''

        subject = "LEAPS interview action plan"

        files = [{
            'content': interviewPlanPDF(student,giveback=True), 
            'filename': 'LEAPS_interview_' + studentname.replace(" ","_") + '_action_plan.pdf'
        }]

        util.send_mail(to=to, fro=fro, subject=subject, text=text, files=files)

        student.data['interview']['emailed_date'] = datetime.now().strftime("%d/%m/%Y")
        student.data['status'] = 'interviewed'
        student.save()

        if flashable:
            flash('Interview action plan has been emailed to ' + ",".join(to), "success")
    except:
        if flashable:
            flash('There was an error processing the email. Please check and try again.')



def _get_interviews_awaiting_email():
    qry = {
        'query':{
            'bool':{
                'must':[
                    {'term':
                        {'archive'+app.config['FACET_FIELD']:'current'}
                    },
                    {'query_string':
                        {'query':'*','default_field':'interview.completed_date'}
                    }
                ],
                'must_not':[
                    {'term':
                        {'school'+app.config['FACET_FIELD']:'TEST'}
                    },
                    {'query_string':
                        {'query':'*','default_field':'interview.emailed_date'}
                    }
                ]
            }
        },
        "sort":[{"interview.completed_date"+app.config['FACET_FIELD']:{"order":"desc"}}],
        'size':10000
    }

    q = models.Student().query(q=qry)
    return [i['_source'] for i in q.get('hits',{}).get('hits',[])]



