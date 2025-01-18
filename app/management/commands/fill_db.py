from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from app.models import Question, Answer, QuestionVote, AnswerVote, Tag, QuestionTag, Profile, Profile

from faker import Faker
import random
from tqdm import tqdm
import os


fake = Faker()

DEFAULT_POPULATION_VALUE = 10

PROFILE_IMG_PATH = os.path.join(settings.MEDIA_ROOT, 'images')


class Command(BaseCommand):
    help = 'Populates the database with sample data.'
    population_value_arg_name = 'ratio'

    tags_limit_per_question_number = 4

    question_number_factor = 10
    answer_number_factor = 100
    like_number_factor = 200

    batch_size = 1000

    description_width = 27

    def format_description(self, description):
        return description.ljust(self.description_width)

    def add_arguments(self, parser):
        parser.add_argument(self.population_value_arg_name, nargs='?', type=int,
                            default=DEFAULT_POPULATION_VALUE, help='Number of users to create')

    def init_values(self, population_value):
        self.population_value = population_value
        self.user_number = population_value
        self.question_number = population_value * self.question_number_factor
        self.answer_number = population_value * self.answer_number_factor
        self.tag_number = population_value
        self.like_number = population_value * self.like_number_factor

        self.average_answers_per_question = self.answer_number_factor / self.question_number_factor

    def is_population_value_valid(self, population_value):
        # return population_value * population_value * self.question_number_factor >= population_value * self.like_number_factor
        return population_value * self.question_number_factor >= self.like_number_factor

    def handle(self, *args, **options):
        population_value = options[self.population_value_arg_name]
        if (not self.is_population_value_valid(population_value)):
            print("Population value should be greater than 20. Stopping...")
            return

        self.init_values(population_value)
        
        self.generate_users()
        self.generate_questions()
        self.generate_answers()
        self.tick_correct_answers()
        self.generate_tags()
        self.generate_question_likes()
        self.generate_answer_likes()

 
 
    def tick_correct_answers(self):
        questions = Question.objects.all()
        for question in tqdm(questions, desc=self.format_description("Ticking Correct Answers")):
            answers = Answer.objects.filter(question=question)
            if len(answers) > 0:
                correct_answer = random.choice(answers)
                correct_answer.is_accepted = True
                correct_answer.save()

    def generate_users(self):
        images = os.listdir(PROFILE_IMG_PATH)

        # Get a set of existing usernames to avoid duplicates
        existing_usernames = set(User.objects.values_list('username', flat=True))
        generated_usernames = set()

        user_batch = []
        profile_batch = []

        # Generate unique usernames
        while len(generated_usernames) < self.user_number:
            user_name = fake.unique.user_name()
            if user_name not in existing_usernames:
                generated_usernames.add(user_name)

        for user_name in tqdm(generated_usernames, desc=self.format_description("Creating Users and Profiles")):
            user = User(username=user_name)
            user.set_password('1')  # Set hashed password
            user_batch.append(user)

        # Bulk create users
        users = User.objects.bulk_create(user_batch)

        # Create profiles for the users
        for user in tqdm(users, desc=self.format_description("Creating Profiles")):
            img_filename = random.choice(images)

            profile = Profile(user=user)
            with open(os.path.join(PROFILE_IMG_PATH, img_filename), 'rb') as img_file:
                profile.profile_image.save(img_filename, File(img_file), save=False)

            profile_batch.append(profile)

        # Bulk create profiles
        Profile.objects.bulk_create(profile_batch) 


    def generate_questions(self):
        existing_question_titles = set(Question.objects.values_list('title', flat=True))

        question_batch = []
        profile_ids = Profile.objects.values_list('id', flat=True)

        for _ in tqdm(range(self.question_number), desc=self.format_description("Creating Questions")):
            title = fake.sentence()
            if title in existing_question_titles:
                continue  # Skip duplicate question titles
            question = Question(
                user_id=random.choice(profile_ids),
                title=title,
                body=fake.text(random.randint(30, 400)),
                created_at=timezone.make_aware(fake.date_time_this_decade()),
            )
            question_batch.append(question)

            if len(question_batch) % self.batch_size == 0:
                Question.objects.bulk_create(question_batch)
                question_batch = []

        if question_batch:
            Question.objects.bulk_create(question_batch)


    def generate_answers(self):
        answer_batch = []

        profile_ids = Profile.objects.values_list('id', flat=True)
        question_ids = Question.objects.values_list('id', flat=True)

        for i in tqdm(range(self.answer_number), desc=self.format_description("Creating Answers")):
            answer = Answer(
                user_id=random.choice(profile_ids),
                question_id=random.choice(question_ids),
                body=fake.paragraph(random.randint(2, 30), variable_nb_sentences=True),
                created_at=timezone.make_aware(fake.date_time_this_decade()),
            )
            answer_batch.append(answer)

            if (i + 1) % self.batch_size == 0:
                Answer.objects.bulk_create(answer_batch)
                answer_batch = []

        if len(answer_batch):
            Answer.objects.bulk_create(answer_batch)


    def generate_question_likes(self):
        question_like_batch = []

        used_questions = {}
        question_ids = Question.objects.values_list('id', flat=True)
        profile_ids = Profile.objects.values_list('id', flat=True)

        for _ in tqdm(range(self.like_number), desc=self.format_description("Creating Votes to Questions")):
            question_like = QuestionVote(
                question_id=random.choice(question_ids),
                user_id=random.choice(profile_ids),
                vote_type=random.choice([1, -1]),
                created_at=timezone.make_aware(fake.date_time_this_decade()),
            )
            if (question_like.user_id not in used_questions):
                used_questions[question_like.user_id] = {question_like.question_id}
            else:
                while question_like.question_id in used_questions[question_like.user_id]:
                    question_like.question_id = random.choice(question_ids)
                used_questions[question_like.user_id].add(question_like.question_id)
            question_like_batch.append(question_like)

        QuestionVote.objects.bulk_create(question_like_batch) 

       
    def generate_answer_likes(self):
        answer_like_batch = []

        used_answers = {}
        answers_ids = Answer.objects.values_list('id', flat=True)
        profile_ids = Profile.objects.values_list('id', flat=True)

        for i in tqdm(range(self.like_number), desc=self.format_description("Creating Votes to Answers")):
            answer_like = AnswerVote(
                answer_id=random.choice(answers_ids),
                user_id=random.choice(profile_ids),
                vote_type=random.choice([1, -1]),
                created_at=timezone.make_aware(fake.date_time_this_decade()),
            )
            if (answer_like.user_id not in used_answers):
                used_answers[answer_like.user_id] = {answer_like.answer_id}
            else:
                while answer_like.answer_id in used_answers[answer_like.user_id]:
                    answer_like.answer_id = random.choice(answers_ids)
                used_answers[answer_like.user_id].add(answer_like.answer_id)
            answer_like_batch.append(answer_like)

        AnswerVote.objects.bulk_create(answer_like_batch) 


    def generate_tags(self):
        num_tags = self.tag_number  
        tags_pool = {fake.word() for _ in range(num_tags)}

        tags = []
        for tag_name in tqdm(tags_pool, desc=self.format_description("Creating Tags")):
            tags.append(Tag(name=tag_name))

        Tag.objects.bulk_create(tags)

        question_tags = []
        for question in tqdm(Question.objects.all(), desc=self.format_description("Assigning Tags to Questions")):
            num_tags = random.randint(2, self.tags_limit_per_question_number)
            question_tags.extend([QuestionTag(question=question, tag=tag) for tag in random.sample(tags, num_tags)])
 
        QuestionTag.objects.bulk_create(question_tags)   
        
        