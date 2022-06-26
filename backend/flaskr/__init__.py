import os
from tracemalloc import start
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # 
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """ 
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
     response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
     response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
     return response
    """
    @TODO:
     Create an endpoint to handle GET requests
     for all available categories.
    """
    @app.route('/categories')
    def get_all_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        
        return jsonify({
           'categories': formatted_categories,
            'success':True
            })


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int )
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        
        questions = Question.query.all()
        formatted_questions = [question.format() for question in questions]
        
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        
        if len(formatted_questions[start:end]) == 0:
            abort(404)

        return jsonify({
            'questions': formatted_questions[start:end],
            'total_questions': len(questions),
            'categories': formatted_categories,
            'current_category': None,
            'success':True
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:quest_id>', methods=['DELETE'])
    def delete_question(quest_id):      
        try:
            question = Question.query.get(quest_id)
            question.delete()
            return jsonify({
                'deleted': quest_id,
                'success':True
                })
        except:
             abort(422)        

   
                

       
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
            question = request.get_json()['question']
            answer = request.get_json()['answer']
            category = request.get_json()['category']
            difficulty = request.get_json()['difficulty']
            new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            new_question.insert()

            return jsonify({
            'success':True,
            'created':'question'
            })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_question():
            searchTerm = request.get_json()['searchTerm']
            query_data = Question.query.filter( Question.question.ilike('%{}%'.format(searchTerm))).all()
            
            formatted_questions = [question.format() for question in query_data]

            return jsonify({
                'total_questions':len(formatted_questions),
                'questions': formatted_questions,
                'currentCategory': [question.category for question in query_data ],
                'success':True
            })


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_cat(category_id):
        try:
            questions = Question.query.filter(
                Question.category == str(category_id + 1)).all()
            formatted_questions = [question.format() for question in questions]


            return jsonify({ 
                'questions': formatted_questions,
                'total_questions': len(questions),
                'current_category': category_id,
                'success':True,
            })
        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play():

        try:
            category = request.get_json()['quiz_category']
            previous_questions = request.get_json()['previous_questions']

            if category['type'] == 'click':
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                available_questions = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((previous_questions))).all()

            rand_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success':True,
                'question': rand_question
            })
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "page not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed "
        }), 400

    return app

