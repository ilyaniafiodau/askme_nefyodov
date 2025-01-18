import copy
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from . import models


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
    questions = models.Question.objects.annotate(
        votes_count=models.Sum('votes__vote_type'),
    ).order_by('-created_at')

    pop_tags = models.Tag.objects.get_popular_n_tags()
    top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)

    page, page_number = paginate(questions, request, per_page = 4)
    if (page is None):
        return redirect(f"/?page={page_number}")

    return render(
        request,
        "index.html",
        context={
            'page_obj': page,
            'questions': page.object_list,
            #'question_tags': question_tags,
            'pop_tags': pop_tags,
            'top_users': top_members
        }
    )

def hot(request):
    hot_questions = models.Question.objects.get_hot_questions()
    pop_tags = models.Tag.objects.get_popular_n_tags()
    top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)

    page, page_number = paginate(hot_questions, request, per_page = 4)
    if (page is None):
        return redirect(f"/?page={page_number}")

    return render(
        request,
        "hot.html",
        context={
            'page_obj': page,
            'questions': page.object_list,
            #'question_tags': question_tags,
            'pop_tags': pop_tags,
            'top_users': top_members
        }
    )

def question(request, question_id):
    if (question_id <= 0) or (question_id >= models.Question.objects.count()):
        return page_404(request)

    pop_tags = models.Tag.objects.get_popular_n_tags()
    top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)

    answers = models.Answer.objects.get_answers_by_question_id(question_id)
    page, page_number = paginate(answers, request, per_page=3)
    
    if (page is None):
        return redirect(f"/?page={page_number}")  
    
    return render(
        request,
        "question.html",
        context={
            'question': models.Question.objects.get_question_by_id(question_id),
            'page_obj': page,
            'answers': page.object_list,
            'pop_tags': pop_tags,
            'top_users': top_members,
            #'question_tags': question_tags
        }
    )

def page_404(request):
    pop_tags = models.Tag.objects.get_popular_n_tags()
    top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)

    return render(
            request,
            'page_404.html',
            status=404,
            context={
                'pop_tags': pop_tags,
                'top_users': top_members
            }
        )

def tag(request, tag_name):
    questions = models.Question.objects.get_questions_by_tag_name(tag_name)
    pop_tags = models.Tag.objects.get_popular_n_tags()
    top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)

    page, page_number = paginate(questions, request, per_page=4)
    if (page is None):
        return redirect(f"/?page={page_number}")

    return render(
        request,
        "tag.html",
        context={
            'page_obj': page,
            'questions': page.object_list,
            #'question_tags': question_tags,
            'tag_name': tag_name,
            'pop_tags': pop_tags,
            'top_users': top_members
        }
    )

def signup(request):
    pop_tags = models.Tag.objects.get_popular_n_tags()
    top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)

    return render(
        request, 
        'signup.html',
        context={
                'pop_tags': pop_tags,
                'top_users': top_members,
                #'question_tags': question_tags,
            }
        )

def ask(request):
   pop_tags = models.Tag.objects.get_popular_n_tags()
   top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)
   
   return render(
      request, 
      'ask.html',
      context={
            'pop_tags': pop_tags,
            'top_users': top_members,
            #'question_tags': question_tags,
        }
      )

def settings(request):
   pop_tags = models.Tag.objects.get_popular_n_tags()
   top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)

   return render(
      request, 
      'settings.html',
      context={
            'pop_tags': pop_tags,
            'top_users': top_members,
            #'question_tags': question_tags,
        }
      )

def login(request):
  #if request.method == 'POST':
      #username = request.POST.get('username')
     # password = request.POST.get('password')
      #confirm = request.POST.get('confirm')
      pop_tags = models.Tag.objects.get_popular_n_tags()
      top_members = models.Profile.objects.get_top_n_users_by_number_of_answers(5)

      return render(
          request, 
          'login.html',
          context={
            'pop_tags': pop_tags,
            'top_users': top_members,
            #'question_tags': question_tags,
            }
          )

#not yet implemented functions
def logout(request):
   return redirect(reverse('index') + "?after=logout")

def users(request):
   return render(request, 'users.html')

def profile_edit(request):
   return render(request, 'profile/edit.html')



