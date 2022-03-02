from flask import Flask, make_response, render_template, redirect, request, url_for, sessions, session
import data_manager, os, datetime
from os import urandom


SESSION_USERNAME = 'username'
app = Flask(__name__)
app.secret_key = urandom(15)
app.config["IMAGE_UPLOADS"] = 'static/images'


@app.route("/", methods=['GET', 'POST'])
def hello():
    sort = 'DESC'
    sort_by = 'submission_time'
    all_list_sorted = data_manager.sorting_main_page(sort_by, sort)
    response = make_response(render_template("index.html", last_questions=all_list_sorted, username = SESSION_USERNAME))
    return response

@app.route("/logout", methods=['GET'])
def logout ():
    session.pop (SESSION_USERNAME)
    return redirect(url_for('hello'))


@app.route(f"/search", methods=['GET', 'POST'])
def searching():
    search = request.args.get('q')
    question_results = data_manager.search_results_questions(search)
    answer_results = data_manager.search_results_answers(search)
    return render_template("search.html", question_results=question_results, answer_results=answer_results)


@app.route('/list', methods=['GET'])
def list_of_questions():
    return render_template('list.html', lista=data_manager.sorting(sort_by='submission_time', sort='DESC'))


@app.route('/list', methods=['POST'])
def sorted_list_of_questions():
    sort = request.form['order']
    sort_by = request.form['type']
    all_list_sorted = data_manager.sorting(sort_by, sort)
    return render_template('list.html', lista=all_list_sorted)


@app.route("/question/<question_id>", methods=['POST', 'GET'])
def display_question(question_id):
    question = data_manager.read_question(question_id)
    answer = data_manager.read_answer(question_id)
    comment = data_manager.read_comment_question(question_id)
    tags = id_to_tags(question_id)
    print(tags)
    return render_template('display_question.html', question=question, answer=answer, comment=comment, tags=tags)


@app.route("/answer/<answer_id>/edit", methods=['POST', 'GET'])
def edit_answer(answer_id):
    answer = data_manager.read_one_answer(answer_id)
    question_id = data_manager.read_question_id(answer_id)
    question = data_manager.read_question(question_id)
    if request.method == 'POST':
        message = request.form['answer']
        image = None
        data_manager.edit_answer(answer_id, message, image)
        return redirect(f'/question/{question_id}')
    return render_template('edit_answer.html', answer=answer, question=question)


@app.route("/add-question", methods=['GET'])
def add_question_get():
    return render_template("addquestion.html")


@app.route("/add-question", methods=["POST"])
def add_question_post():
    sub_tim = str(datetime.datetime.now())
    image = request.files['file']
    print(f'to jest {image}')
    if image.filename != '':
        base_dir = os.path.abspath(os.path.dirname(__file__))
        image.save(os.path.join(base_dir, app.config['IMAGE_UPLOADS'], image.filename))
    else:
        image.filename = None
    sub_tim = str(datetime.datetime.now())
    new_id = data_manager.add_new_question(sub_time=sub_tim, title=request.form['title'],
                                           message=request.form['message'],
                                           image=image.filename)
    return redirect(f'/question/{new_id}')


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def question_new_answer(question_id):
    question = data_manager.read_question(question_id)
    answer = data_manager.read_answer(question_id)
    if request.method == 'POST':
        image = request.files['file']
        answer = request.form['answer']
        if image.filename == '':
            data_manager.save_new_answer(question_id, answer, None)
            return redirect(url_for('display_question', question_id=question_id))
        else:
            base_dir = os.path.abspath(os.path.dirname(__file__))
            image.save(os.path.join(base_dir, app.config['IMAGE_UPLOADS'], image.filename))
            data_manager.save_new_answer(question_id, answer, image.filename)
            return redirect(url_for('display_question', question_id=question_id))
    return render_template('post_answer.html', question=question, answer=answer)


@app.route("/question/<question_id>/delete")
def question_delete(question_id):
    data_manager.delete_question(question_id)
    return render_template("list.html")


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def question_edit(question_id):
    if request.method == "GET":
        question = data_manager.edit_question_get(question_id)
        return render_template("editquestion.html", question=question)
    elif request.method == "POST":
        image = request.files['file']
        base_dir = os.path.abspath(os.path.dirname(__file__))
        image.save(os.path.join(base_dir, app.config['IMAGE_UPLOADS'], image.filename))
        data_manager.edit_question_post(id=question_id, title=request.form['title'], message=request.form['message'],
                                        imi=image.filename)
        return redirect(url_for('list_of_questions'))


@app.route("/answer/<answer_id>/delete")
def answer_delete(answer_id):
    data_manager.delete_answer(answer_id)
    return render_template("list.html")


@app.route("/question/<question_id>/vote_up")
def question_vote_up(question_id):
    data_manager.vote_up(question_id)
    question = data_manager.read_question(question_id=question_id)
    data_manager.update_user_reputation(user_id=question['user_id'], value=5)
    return redirect("/list")


@app.route("/question/<question_id>/vote_down")
def question_vote_down(question_id):
    data_manager.vote_down(question_id)
    question = data_manager.read_question(question_id=question_id)
    data_manager.lost_user_reputation(user_id=question['user_id'])
    return redirect("/list")


@app.route("/answer/<answer_id>/vote_up")
def answer_vote_up(answer_id):
    data_manager.vote_up_answer(answer_id)
    answer = data_manager.read_answer_answer_id(answer_id=answer_id)
    data_manager.update_user_reputation(user_id=answer['user_id'], value=10)
    return redirect(request.referrer)


@app.route("/answer/<answer_id>/vote_down")
def answer_vote_down(answer_id):
    data_manager.vote_down_answer(answer_id)
    answer = data_manager.read_answer_answer_id(answer_id=answer_id)
    data_manager.lost_user_reputation(user_id=answer['user_id'])
    return redirect(request.referrer)


@app.route('/question/<question_id>/new-comment', methods=["GET", "POST"])
def new_commet(question_id):
    if request.method == "GET":
        return render_template('add_comment.html', question=data_manager.read_question(question_id), field='question')
    if request.method == "POST":
        data_manager.add_comment_to_question(question_id=question_id, message=request.form['message'])
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/comment/<comment_id>/edit', methods=["GET", "POST"])
def edit_commnet(comment_id):
    if request.method == "GET":
        comment = data_manager.pull_commnet(comment_id=comment_id)
        return render_template('comment_edit.html', comment=comment)
    if request.method == "POST":
        message = request.form['message']
        data_manager.update_comment(comment_id=comment_id, message=message)
        comment = data_manager.pull_commnet(comment_id=comment_id)
        return redirect(url_for('display_question', question_id=comment['question_id']))


@app.route('/answer/<answer_id>/new-comment', methods=["GET", "POST"])
def comment_answer(answer_id):
    answer = data_manager.read_answer_answer_id(answer_id=answer_id)
    if request.method == "GET":
        return render_template('add_comment_answer.html', answer=answer)
    if request.method == "POST":
        data_manager.add_comment_to_answer(question_id=answer['question_id'], answer_id=answer['id'],
                                           message=request.form['message'])
        return redirect(url_for('display_question', question_id=answer['question_id']))


@app.route('/question/<question_id>/new-tag', methods=['GET'])
def add_tag(question_id):
    print(question_id)
    tags = id_to_tags(question_id)
    return render_template('addtag.html', tags=tags, question_id=question_id)

@app.route('/del-tag/<question_id>/<tag>')
def del_tag_from_queestion(question_id, tag):
    tag_id = data_manager.get_id_by_tag_name(tag)
    data_manager.del_tag_from_question(question_id, tag_id["id"])
    return redirect(f'/question/{question_id}/new-tag')


@app.route('/question/<question_id>/new-tag', methods=['POST'])
def new_tag(question_id):
    all_tag = []
    question_id = int(question_id)
    newtag = request.form['newtag']
    tags = data_manager.get_all_tags()
    for tag in tags:
        all_tag.append(tag['name'])
    print(f'to jest all tag {all_tag}')
    print(f'New tag {newtag}')
    if newtag not in all_tag:
        data_manager.save_new_tag(newtag)
        new_id = data_manager.get_id_by_tag_name(newtag)
        data_manager.save_tag_id_to_question(question_id, new_id["id"])
    else:
        used_tags = []
        all_used_tags = data_manager.is_tag_alredy_in_question(question_id)
        for ele in all_used_tags:
            used_tags.append(ele['tag_id'])
        new_id = data_manager.get_id_by_tag_name(newtag)
        if new_id['id'] in used_tags:
            return redirect(url_for('display_question', question_id=question_id))
        else:
            data_manager.save_tag_id_to_question(question_id, new_id["id"])
    return redirect(url_for('display_question', question_id=question_id))


def id_to_tags(question_id):
    all_tags_id = []
    all_tags_name = []
    all_question_tag_id = data_manager.get_all_tags_id_from_question(question_id)
    if all_question_tag_id == []:
        tags = 'Notags'
        return tags
    else:
        for tag_name in all_question_tag_id:
            all_tags_id.append(tag_name['tag_id'])
        for ele in all_tags_id:
            tag = data_manager.get_tag_name_by_id(ele)
            all_tags_name.append(tag['name'])
            tags = all_tags_name
        return tags

@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        if data_manager.check_password (password = request.form['password'], repeat_password =request.form['repeat_password']) != True:
            wrong_passwords = True
            return (render_template('register.html', wrong_passwords=wrong_passwords ))

        if data_manager.check_new_user (user = request.form['username'] , password = request.form['password']):
            return redirect(url_for('hello'))
    return render_template('register.html', wrong_passwords=False)

@app.route('/login', methods=['GET', 'POST'])
def login ():
    if request.method == "POST":
        if data_manager.check_login (username = request.form['username'] , password = request.form['password']):
            user = request.form['username']
            session[SESSION_USERNAME] = user

            return redirect(url_for('hello'))
        else:
            wrong_login = True
            return (render_template('login.html', wrong_login=wrong_login))
    return render_template('login.html',wrong_login=False)

@app.route('/user/<user_id>')
def single_user_page(user_id):
    user = data_manager.get_user_data(user_id)
    answer = data_manager.get_user_answer(user_id)
    comment = data_manager.get_user_comment(user_id)
    question = data_manager.get_user_question(user_id)
    return render_template('user_page.html', user=user, answer=answer, comment=comment, question=question)


@app.route('/bonusquestions')
def bonus_question():
    return render_template('bonus_questions.html')


if __name__ == "__main__":
    app.run(debug=True)
