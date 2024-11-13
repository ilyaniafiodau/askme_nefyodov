import copy
from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator


# Create your views here.


questions = []
for i in range(0,30):
  questions.append({
    'title': 'Question#'  + str(i),
    'id': i,
    'text': 'Some lorem ipsum kinda text to provide content for question' + str(i)
  })


def index(request):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(questions, 5)
    page = paginator.page(page_num)
    return render(
       request, 'index.html', context = {'questions': page.object_list, 'page_obj': page }
       )

def hot(request):
   hot_questions = copy.deepcopy(questions)
   hot_questions.reverse()
   return render(
      request, 'hot.html', context = {'questions': hot_questions}
      )

def tag(request, question_tag):
   tagged_questions = copy.deepcopy(questions)
   tagged_questions.remove(question[0])
   return render(
      request, 'tag.html', context = {'questions': tagged_questions}
      )

def question(request, question_id):
   single_question = questions[question_id]
   return render(
      request, 'single_question.html', context = {'question': single_question}
      )

def login(request):
   login_error = {
        'error_message': None, 
    }
   return render(
      request, 'login.html', context = login_error
      )

def signup(request):
   signup_error = {
        'error_message': None, 
    }
   return render(
      request, 'login.html', context = signup_error
      )

def ask(request):
   ask_error = {
        'error_message': None, 
    }
   return render(
      request, 'login.html', context = ask_error
      )