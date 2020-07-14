from django.shortcuts import render
from blog.process import ERA, SAA, SM
from firebase import firebase
firebase = firebase.FirebaseApplication('https://smartanalyzer-s3hp.firebaseio.com/')


def home(request):
    return render(request, 'blog/home.html')

def about(request):
    return render(request, 'blog/about.html',{'title':'About'})


def era_view(request):
    if "GET" == request.method:
        return render(request, 'blog/era.html',
                      {'title': 'Exam Result Analysis'})
    else:
        excel_file = request.FILES["excel_file"]
        e_name = str(request.POST.get('e_name', None))
        max_score = int(request.POST.get('max_score', None))
        q_count = int(request.POST.get('q_count', None))

        return render(
            request, 'blog/era_output.html',
            ERA.evaluate_era_output(excel_file, e_name, max_score, q_count))


def saa_view(request):
    return render(request, 'blog/saa.html',
                  {'title': 'Student Attendance Analysis'})


def saa_se_a_view(request):
    return render(request, 'blog/saa_se_a.html', SAA.se_a())


def sm_view(request):
    return render(request, 'blog/sm.html', {'title': 'Schedule Manager'})

def sm_view_display(request):
    if "GET" == request.method:
        classes = firebase.get('classes/', None)
        return render(request, 'blog/sm_display.html', {
            'title': 'Schedule Manager',
            'classes': classes,
        })
    else:
        return render(request, 'blog/sm_display.html', SM.display_schedule(request))


def sm_view_manage(request):
    if "GET" == request.method:
        classes = firebase.get('classes/', None)
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
        slots = [1,2,3,4,5,6,7]
        return render(request, 'blog/sm_manage.html', {
            'title': 'Schedule Manager',
            'days': days,
            'classes': classes,
            'slots':slots,
        })
    else:
        return render(request, 'blog/sm_manage.html', SM.manage_schedule(request))
