import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:devel@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_not_found_questions(self):
        # unreachable question id 5000
        res = self.client().get('/questions?page=5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Page Not Found')
    
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_not_found_categories(self):
        # unreachable category id 5000
        res = self.client().get('/categories/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Page Not Found')
    
    def test_add_new_question(self):
        new_question = {
            'question': 'How Are You ?',
            'answer': 'Fine, Thank You!',
            'difficulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        
    
    def test_unprocessable_add_new_question(self):
        # question body missing gategory and difficulty
        new_question = {
            'question': 'How Are You ?',
            'answer': 'Fine, Thank You!',
        }
        
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")

    def test_delete_question(self):
        # create new question record 
        question = Question(question='How Are You ?', answer='Fine, Thank You!',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        # delete the record we have just created
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_unprocessable_delete_question(self):
        # unreachable question id 5000
        res = self.client().delete('/questions/5000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_search_questions(self):
        # this question mark "?" will be found in most of the question
        search_term = {'searchTerm': '?'}
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_not_found_search_question(self):
        # empty search value
        search_term = {'searchTerm': ''}
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page Not Found")
    
    def test_get_questions_by_category(self):
        # get the questions of category id = 1
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_not_found_get_questions_by_category(self):
        # unreachable category id value "xzy"
        res = self.client().get('/categories/xzy/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page Not Found")

    def test_play_quiz(self):
        new_quiz = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1}
        }
                            
        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_unprocessable_play_quiz(self):
        # new quiz body missing quiz_category
        new_quiz = {
            'previous_questions': []
        }
        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable Entity")
    
# All Tests running Correctly
# Ran 14 tests with result Ok

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()