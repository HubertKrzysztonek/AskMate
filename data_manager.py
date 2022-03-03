import database_common
import bcrypt
import psycopg2
import database_common


@database_common.connection_handler
def read_question(cursor, question_id):
    query = f"""
    SELECT * FROM question
    WHERE id = (%s);
    """
    cursor.execute(query, (question_id,))
    question = cursor.fetchone()
    return question


@database_common.connection_handler
def read_all_question(cursor, question_id):
    query = f"""
        SELECT * FROM question
        WHERE id = (%s);
        """
    cursor.execute(query, (question_id,))
    question = cursor.fetchall()
    return question


@database_common.connection_handler
def read_one_answer(cursor, answer_id):
    query = """
    SELECT * FROM answer
    WHERE id = %s
    """
    cursor.execute(query, [answer_id])
    answer = cursor.fetchone()
    return answer


@database_common.connection_handler
def read_question_id(cursor, answer_id):
    query = f"""
      SELECT question_id FROM answer
      WHERE id = %s;
      """
    cursor.execute(query, (answer_id,))
    question_id = cursor.fetchone()
    for row in question_id:
        if row != None:
            question_id = question_id[row]
    return question_id


@database_common.connection_handler
def read_answer(cursor, question_id):
    query = """
    SELECT * 
    FROM answer
    WHERE question_id = %s;
    """
    cursor.execute(query, [question_id])
    return cursor.fetchall()


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    query = """
        DELETE FROM answer
        WHERE id = %s;"""

    cursor.execute(query, [answer_id])


@database_common.connection_handler
def delete_question(cursor, question_id):
    query = """
        DELETE FROM question
        WHERE id = %s;"""

    cursor.execute(query, [question_id])


@database_common.connection_handler
def save_new_answer(cursor, question_id, message, image, userid):
    query = """
    INSERT INTO answer (submission_time, vote_number, message, question_id, image, user_id, accepted)
    VALUES (current_timestamp, 0, %s, %s, %s, %s, False);"""

    cursor.execute(query, (message, question_id, image, userid))


@database_common.connection_handler
def edit_answer(cursor, answer_id, message, image):
    query = f"""
    UPDATE answer 
    SET message = %s, image = %s 
    WHERE id = %s"""
    cursor.execute(query, (message, image, answer_id))


@database_common.connection_handler
def search_results_questions(cursor, text):
    query = """
    SELECT * FROM question
    WHERE title LIKE %s or message LIKE %s;
    """
    cursor.execute(query, ((f'%{text}%'), (f'%{text}%')))
    questions_search = cursor.fetchall()
    return questions_search


@database_common.connection_handler
def search_results_answers(cursor, text):
    results = []
    query = """
    SELECT question_id FROM answer
    WHERE message LIKE %s;
    """
    cursor.execute(query, ((f'%{text}%'),))
    answer_search = cursor.fetchall()

    for row in answer_search:
        for every_row in row:
            question_id = row[every_row]
            new_result = read_all_question(question_id)
            if new_result not in results:
                results.append(new_result)
    return results


print(search_results_answers('abc'))


@database_common.connection_handler
def vote_up(cursor, question_id):
    query = """
            UPDATE question SET vote_number = vote_number +1 WHERE id = %s;
    """
    cursor.execute(query, [question_id])


@database_common.connection_handler
def vote_down(cursor, question_id):
    query = """
            UPDATE question SET vote_number = vote_number -1 WHERE id = %s;
    """
    cursor.execute(query, [question_id])


@database_common.connection_handler
def vote_up_answer(cursor, answer_id):
    # print(answer_id)
    query = """
            UPDATE answer SET vote_number = vote_number +1 WHERE id = %s;
    """
    cursor.execute(query, [answer_id])


@database_common.connection_handler
def vote_down_answer(cursor, answer_id):
    query = """
            UPDATE answer SET vote_number = vote_number -1 WHERE id = %s;
    """
    cursor.execute(query, [answer_id])


@database_common.connection_handler
def sorting(cursor, sort_by, sort):
    query = f"""
            SELECT * FROM question ORDER BY {sort_by} {sort};
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def sorting_main_page(cursor, sort_by, sort):
    query = f"""
            SELECT * FROM question ORDER BY {sort_by} {sort}
            LIMIT 5;
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def add_new_question(cursor, sub_time, title, message, image, user_id):
    query = """
            INSERT INTO question
            (submission_time, view_number, vote_number, title, message, image, user_id)
            VALUES (%s,0,0,%s,%s,%s,%s)
            returning id
    """
    cursor.execute(query, (sub_time, title, message, image, user_id))
    return cursor.fetchone()['id']


@database_common.connection_handler
def edit_question_get(cursor, quest_id):
    query = """
            SELECT id,title, message
            FROM question
            WHERE id = %s
    """
    cursor.execute(query, [quest_id])
    return cursor.fetchone()


@database_common.connection_handler
def edit_question_post(cursor, id, title, message, imi):
    query = """
        UPDATE question
        SET title = %s , message = %s,image = %s
        WHERE id = %s
    """
    cursor.execute(query, (title, message, imi, id))


@database_common.connection_handler
def read_comment_question(cursor, question_id):
    query = """
        SELECT *
        FROM comment
        WHERE question_id = %s
    """
    cursor.execute(query, [question_id])
    return cursor.fetchall()


@database_common.connection_handler
def add_comment_to_question(cursor, question_id, message, userid):
    query = """
        INSERT INTO comment
        (question_id, message, submission_time, edited_count, user_id) 
        VALUES (%s,%s,current_timestamp,0,%s)
    """
    cursor.execute(query, [question_id, message, userid])


@database_common.connection_handler
def pull_commnet(cursor, comment_id):
    query = """
        SELECT *
        FROM comment
        WHERE id = %s
    """
    cursor.execute(query, [comment_id])
    return cursor.fetchone()


@database_common.connection_handler
def update_comment(cursor, comment_id, message):
    query = """
        UPDATE comment
        SET message = %s , edited_count = edited_count + 1
        WHERE id = %s
    """
    cursor.execute(query, (message, comment_id))


@database_common.connection_handler
def read_answer_answer_id(cursor, answer_id):
    query = """
        SELECT *
        FROM answer
        WHERE id = %s
    """
    cursor.execute(query, [answer_id])
    return cursor.fetchone()


@database_common.connection_handler
def add_comment_to_answer(cursor, question_id, answer_id, message):
    query = """
        INSERT INTO comment
        (question_id,answer_id, message, submission_time, edited_count) 
        VALUES (%s,%s,%s,current_timestamp,0)
    """
    cursor.execute(query, [question_id, answer_id, message])


@database_common.connection_handler
def get_tag_name_by_id(cursor, tag_id):
    query = """
           SELECT name
            FROM tag
            WHERE id = %s
       """
    cursor.execute(query, [tag_id])
    return cursor.fetchone()


@database_common.connection_handler
def get_id_by_tag_name(cursor, tagname):
    query = """
               SELECT id
                FROM tag
                WHERE name = %s
           """
    cursor.execute(query, [tagname])
    return cursor.fetchone()


@database_common.connection_handler
def save_tag_id_to_question(cursor, question_id, tagid):
    query = """
            INSERT INTO question_tag
            (question_id, tag_id)
            VALUES (%s,%s)
        """
    cursor.execute(query, (question_id, tagid))


@database_common.connection_handler
def get_all_tags_id_from_question(cursor, question_id):
    query = """
               SELECT tag_id
                FROM question_tag
                WHERE question_id = %s
           """
    cursor.execute(query, [question_id])
    return cursor.fetchall()

@database_common.connection_handler
def get_all_questions_id_by_tag_id(cursor, tag_id):
    query = """
                   SELECT question_id
                    FROM question_tag
                    WHERE tag_id = %s
               """
    cursor.execute(query, [tag_id])
    return cursor.fetchall()

@database_common.connection_handler
def save_new_tag(cursor, newtag):
    query = """
        INSERT INTO tag
        (name)
        VALUES (%s)
    """
    cursor.execute(query, [newtag])

@database_common.connection_handler
def del_tag_from_question(cursor, questid, tagid):
    query = """
            DELETE FROM question_tag WHERE question_id = %s AND tag_id = %s;
             """
    cursor.execute(query, [questid, tagid])

@database_common.connection_handler
def get_user_data(cursor, user_id):
    query = """
        SELECT *
        FROM users
        WHERE id = %s
    """
    cursor.execute(query, [user_id])
    return cursor.fetchone()

@database_common.connection_handler
def check_new_user(cursor, user, password):
    salt = bcrypt.gensalt()
    hashed_psw = bcrypt.hashpw(b'password', salt)
    query = """
    SELECT * 
    FROM users
    WHERE username = %s;
    """
    cursor.execute(query, [user])
    users = cursor.fetchall()
    if users == []:
            query = """
                INSERT INTO users
                (username, password, registration, asked_questions, answers, comments, reputation, image) 
                VALUES (%s,%s,current_timestamp,0,0,0,0, 'null')
            """
            cursor.execute(query, [user, hashed_psw])
            return True
    else:
        return False

check_new_user ('dragonpl','123456')

@database_common.connection_handler
def get_user_question(cursor, user_id):
    query = """
        SELECT *
        FROM question
        WHERE user_id= %s
    """
    cursor.execute(query, [user_id])
    return cursor.fetchall()


@database_common.connection_handler
def get_user_answer(cursor, user_id):
    query = """
        SELECT *
        FROM answer
        WHERE user_id= %s
    """
    cursor.execute(query, [user_id])
    return cursor.fetchall()

@database_common.connection_handler
def users(cursor):
    query = """
        SELECT *
        FROM users
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_user_comment(cursor, user_id):
    query = """
        SELECT *
        FROM comment
        WHERE user_id= %s
    """
    cursor.execute(query, [user_id])
    return cursor.fetchall()


@database_common.connection_handler
def get_all_tags(cursor):
    query = """
               SELECT * 
                FROM tag
           """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def is_tag_alredy_in_question(cursor, questid):
    query = """
                SELECT tag_id 
                FROM question_tag
                WHERE  %s = question_id
              """
    cursor.execute(query, [questid])
    return cursor.fetchall()


def code(password):
    password = password.encode('utf-8')
    hashed_psw = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed_psw.decode('utf-8')

@database_common.connection_handler
def check_new_user(cursor, user, password):
    password = code(password)
    print (password)
    query = """
    SELECT * 
    FROM users
    WHERE username = %s;
    """
    cursor.execute(query, [user])
    users = cursor.fetchall()
    if users == []:
            query = """
                INSERT INTO users
                (username, password, registration, asked_questions, answers, comments, reputation, image) 
                VALUES (%s,%s,current_timestamp,0,0,0,0, 'null')
            """
            cursor.execute(query, (user, password))
            return True
    else:
        return False

def check_password (password, repeat_password):
    if password != repeat_password:
        return False
    else:
        return True


class BCryptHelper:
    pass


@database_common.connection_handler
def check_login (cursor, username, password):
    query = """
        SELECT password
        FROM users
        WHERE username = %s
    """
    cursor.execute(query, [username])
    database_user = cursor.fetchone()
    if database_user != None:
        if bcrypt.checkpw(password.encode('utf-8'), database_user['password'].encode('utf-8')):
            return True
        else:
            return False
    else:
        return False


@database_common.connection_handler
def update_user_reputation(cursor, user_id, value):
    query = """
    UPDATE users 
    SET reputation = reputation + %s
    WHERE id = %s
    """
    cursor.execute(query, (value, user_id))

@database_common.connection_handler
def lost_user_reputation(cursor, user_id):
    query = """
    UPDATE users 
    SET reputation = reputation - 2
    WHERE id = %s
    """
    cursor.execute(query, [user_id])

@database_common.connection_handler
def get_user(cursor, user_id):
    query = """
    SELECT *
    FROM users
    where id = %s
    """
    cursor.execute(query, [user_id])
    return cursor.fetchone()

@database_common.connection_handler
def get_user_id(cursor, user_id):
    query = """
    SELECT ID
    FROM users
    where id = %s
    """
    cursor.execute(query, [user_id])
    return cursor.fetchone()

@database_common.connection_handler
def get_user_username(cursor, username):
    query = """
    SELECT *
    FROM users
    where username = %s
    """
    cursor.execute(query, [username])
    return cursor.fetchone()

@database_common.connection_handler
def update_user_question(cursor, user_id, value):
    query = """
    UPDATE users 
    SET asked_questions = asked_questions + %s
    WHERE id = %s
    """
    cursor.execute(query, (value, user_id))

@database_common.connection_handler
def get_user_id_by_username(cursor, username):
    query = """
        SELECT id
        FROM users
        where username = %s
        """
    cursor.execute(query, [username])
    return cursor.fetchone()
@database_common.connection_handler
def update_answer_accept(cursor,answer_id):
    query = """
    UPDATE answer
    SET accepted=True
    where id=%s
    """
    cursor.execute(query, [answer_id])