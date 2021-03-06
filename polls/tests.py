import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from .models import Question


# Create your tests here.

class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose pub_date is in the future.
        :return:
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEquals(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose pub_date is older than 1 day.
        :return:
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEquals(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose pub_date is within the last day.
        :return:
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEquals(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Creates a question with the given 'question_text' published the given number of 'days' offset to now
    (negative for questions published in the past, positive for questions that have yet to be published).
    :param question_text:
    :param days:
    :return:
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed
        :return:
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the index page
        :return:
        """
        create_question(question_text="Past Question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question.>'])

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on the index page
        :return:
        """

        create_question(question_text="Future Question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_future_question_and_a_past_question(self):
        """
        Even if both past and future questions exist, only past questions will be displayed
        :return:
        """
        create_question(question_text="Past Question.", days=-30)
        create_question(question_text="Future Question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past Question.>'])

    def test_index_view_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        :return:
        """
        create_question(question_text="Past Question 1.", days=-30)
        create_question(question_text="Past Question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past Question 2.>', '<Question: Past Question 1.>'])


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The details view of a question with a pub_date in the future should return a 404 not found.
        :return:
        """
        future_question = create_question(question_text="Future Question.", days=5)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The details view of a question with a pub_date in the past should display the question's text
        :return:
        """
        past_question=create_question(question_text="Past Question.",days=-5)
        response=self.client.get(reverse('polls:detail',args=(past_question.id,)))
        self.assertContains(response,past_question.question_text,status_code=200)
