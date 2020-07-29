import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  CORS(app)
  
  # CROS Headers
  # after_request decorator to set Access-Control-Allow Headers and Methods
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Autherization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE')
    return response

  # define variable with default value of 10 for number of Questions per page
  questions_within_page = 10

  # Define pagination function to handle display of Questions per page
  def paginate_questions(request, selection):
    # use request arguments to get the number of the page 
    page = request.args.get('page', 1, type=int) #ex: page number = 1
    start = (page - 1) * questions_within_page   #ex: start = (1-1) * 10 = 0
    end = start + questions_within_page          #ex: end = 0 + 10 = 10

    # loop throw the selection
    questions = [question.format() for question in selection]
    target_questions = questions[start:end]      #ex: target_questions = questions of [0:10]

    return target_questions


  # Done: Create an endpoint to handle GET requests for all available categories.

  @app.route('/categories')
  def get_categories():

    # Fetch all Categories order by id
    categories = Category.query.order_by(Category.id).all()

    # Check categories count (If > 0 will return json format categories data otherwise will abort with error 404) 
    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success':True,
      'categories': {category.id: category.type for category in categories},
    })
  

  # Done: Create an endpoint to handle GET requests for questions, including pagination (every 10 questions).
  # This endpoint should return a list of questions, number of total questions, current category, categories. 

  @app.route('/questions')
  def get_questions():
    # Fetch all questions from database
    selection = Question.query.order_by(Question.id).all()
    # Use pre defined function (paginate_questions) to paginate questions of 10 records per page
    target_questions = paginate_questions(request, selection)
    # Fetch all categories from database
    categories = Category.query.order_by(Category.id).all()

    if len(target_questions) == 0:
      abort(404)
    
    return jsonify({
      'success': True,
      'questions': target_questions,
      'total_questions': len(selection),
      'categories': {category.id: category.type for category in categories},
      'current_category': None
    })

  # TEST: At this point, when you start the application
  # you should see questions and categories generated,
  # ten questions per page and pagination at the bottom of the screen for three pages.
  # Clicking on the page numbers should update the questions. 
  

  
  # TODO: Create an endpoint to DELETE question using a question ID. 
  
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
      })

    except:
      abort(422)

  # TEST: When you click the trash icon next to a question, the question will be removed.
  # This removal will persist in the database and when you refresh the page. 
  

  
  # Done: Create an endpoint to POST a new question, 
  # which will require the question and answer text, category, and difficulty score.
  
  @app.route('/questions', methods=['POST'])
  def add_question():
    
    body = request.get_json()

    question = body.get('question')
    answer = body.get('answer')
    difficulty = body.get('difficulty')
    category = body.get('category')

    if (len(question) == 0 or len(answer) == 0):
      abort(422)

    try:
      new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      new_question.insert()

      return jsonify({
        'success': True,
        'created': new_question.id
      })

    except:
      abort(422)
    
  # TEST: When you submit a question on the "Add" tab, 
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.  
  

  
  # Done: Create a POST endpoint to get questions based on a search term.
  # It should return any questions for whom the search term is a substring of the question. 
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    
    try:
      body = request.get_json()
      search_term = body.get('searchTerm', None)
      search_result = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      return jsonify({
        'success':True,
        'questions': [question.format() for question in search_result],
        'total_questions': len(search_result),
        'current_category': None
      })

    except:
      abort(404)

  # TEST: Search by any phrase. The questions list will update to include 
  # only question that include that string within their question. 
  # Try using the word "title" to start. 
 

 
  # Done: Create a GET endpoint to get questions based on category.

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):

    try:
      questions = Question.query.filter(Question.category == str(category_id)).all()

      return jsonify({
        'success': True,
        'questions': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': category_id
      })

    except:
      abort(404)

  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 
  


 
  # Done: Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions.
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      body = request.get_json()
      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

      if category['type'] == 'click':
        show_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      else:
        show_questions = Question.query.filter_by(
          category=category['id']).filter(Question.id.notin_((previous_questions))).all()
      
      new_question = show_questions[random.randrange(
        0, len(show_questions))].format() if len(show_questions) > 0 else None 
      
      return jsonify({
        'success': True,
        'question': new_question
      })

    except:
      abort(422)
   

  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not. 
 

 
  # DONE: Create error handlers for all expected errors, including 404 and 422. 

  # Error Code 400 shows message (bad request) in json format
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    })

  # Error Code 404 shows message (page not found) in json format 
  @app.errorhandler(404)
  def page_not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Page Not Found'
    }), 404

  # Error Code 422 shows message (Unprocessable Entity) in json format 
  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success' : False,
      'error': 422,
      'message': 'Unprocessable Entity'
    }), 422


  return app

    