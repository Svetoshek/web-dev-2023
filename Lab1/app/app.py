from flask import Flask, render_template, url_for
from faker import Faker
from random import randint


app = Flask(__name__)
application = app

fake = Faker()

images_ids = [
    '2d2ab7df-cdbc-48a8-a936-35bba702def5',
    '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
    '7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
    'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
    'cab5b7f2-774e-4884-a200-0c0180fa777f',
]


def generate_comments(reply=True):
    comments = []
    if not(reply): 
        max_quantity = randint(0, 3)
    else: 
        max_quantity = randint(1, 10)
    
    for i in range(max_quantity):
        comment = {
            'author': fake.name(),
            'text': fake.text(),
            'date': fake.date_time_between(
                start_date='-2y',
                end_date='now'
            )}
        if reply:
            comment['reply'] = generate_comments(reply=False)
        comments.append(comment)
    comments = sorted(comments, key=lambda comment: comment['date'], reverse=True)
    return comments


def generate_post(index):
    return {
        'index': index,
        'title': fake.text(max_nb_chars=15).rstrip('.'),
        'img_id': images_ids[index],
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'comments': generate_comments()
    }


posts_list = [generate_post(i) for i in range(5)]
posts_list = sorted(posts_list, key=lambda post: post['date'], reverse=True)


@ app.route('/')
def index():
    return render_template('index.html', msg='qq')


@ app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts_list=posts_list)


@ app.route('/post/<int:post_id>')
def post(post_id):
    for post_item in posts_list:
        if post_item['index'] == post_id:
            desired_post = post_item
            break
    return render_template('post.html', post=desired_post, title=desired_post['title'])


@ app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')



