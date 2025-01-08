import copy
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template import loader

# Create your views here.

pop_tags = ["Why", "How", "sigh", "duh", "WTF", "OK", "idk"]
question_tags = ["WTF", "idk"]

top_members = ["Mr Why", "Mr Who", "Mr When", "Dr Know-It-All", "Armchair Sportsman"]

questions = []
for i in range(0,30):
  questions.append({
    'title': 'Question #'  + str(i),
    'id': i,
    'text': 'Some lorem ipsum kinda text to provide content for what-is-supposed-to-be a complicated question ' + str(i)
  })

  hot_questions = copy.deepcopy(questions)
  hot_questions.reverse()

answers = []
for i in range(0,2):
  answers.append({
    'title': 'Answer #'  + str(i),
    'id': i,
    'text': 'Some lorem ipsum kinda text to provide content for answer ' + str(i)
  })


  from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate(objects_list, request, per_page = 4):
    page_number = request.GET.get('page', 1)  

    paginator = Paginator(objects_list, per_page)  
    
    try:
        page = paginator.get_page(page_number) 
    except PageNotAnInteger:
        page = paginator.get_page(1)
    except EmptyPage:
        page = paginator.get_page(paginator.num_pages)

    return page, page.number
    

def index(request):
    page, page_number = paginate(questions, request, per_page = 4)
    if (page is None):
        return redirect(f"/?page={page_number}")

    return render(
        request,
        template_name="index.html",
        context={
            'page_obj': page,
            'questions': page.object_list,
            'question_tags': question_tags,
            'pop_tags': pop_tags,
            'top_users': top_members
        }
    )

def hot(request):
    page, page_number = paginate(hot_questions, request, per_page = 4)
    if (page is None):
        return redirect(f"/?page={page_number}")

    return render(
        request,
        template_name="hot.html",
        context={
            'page_obj': page,
            'questions': page.object_list,
            'question_tags': question_tags,
            'pop_tags': pop_tags,
            'top_users': top_members
        }
    )

def question(request, question_id):
    if (question_id < 0) or (question_id >= len(questions)):
        return render(
                        request, 
                        'question_not_found.html',
                        status=404,
                        context={
                            'pop_tags': pop_tags,
                            'top_users': top_members
                        }
                    )
    
    return render(
        request,
        template_name="question.html",
        context={
            'question': questions[question_id],
            'pop_tags':pop_tags,
            'question_tags': question_tags,
            'top_users': top_members,
            'answers': answers
        }
    )

def tag(request, tag_name):
    page, page_number = paginate(questions, request, per_page=4)
    if (page is None):
        return redirect(f"/?page={page_number}")

    return render(
        request,
        template_name="tag.html",
        context={
            'page_obj': page,
            'questions': page.object_list,
            'question_tags': question_tags,
            'tag_name': tag_name,
            'pop_tags': pop_tags,
            'top_users': top_members
        }
    )

def signup(request):
   return render(
      request, 'signup.html',
      context={
            'pop_tags': pop_tags,
            'top_users': top_members,
            'question_tags': question_tags,
        }
      )

def ask(request):
   return render(
      request, 'ask.html',
      context={
            'pop_tags': pop_tags,
            'top_users': top_members,
            'question_tags': question_tags,
        }
      )

def settings(request):
   return render(
      request, 'settings.html',
      context={
            'pop_tags': pop_tags,
            'top_users': top_members,
            'question_tags': question_tags,
        }
      )

def login(request):
  #if request.method == 'POST':
      #username = request.POST.get('username')
     # password = request.POST.get('password')
      #confirm = request.POST.get('confirm')
      return render(
          request, 'login.html',
          context={
            'pop_tags': pop_tags,
            'top_users': top_members,
            'question_tags': question_tags,
            }
          )

#not yet implemented functions
def logout(request):
   return redirect(reverse('index') + "?after=logout")

def users(request):
   return render(request, 'users.html')

def profile_edit(request):
   return render(request, 'profile/edit.html')



