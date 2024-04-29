from django.urls import path, include
from .views import *

urlpatterns = [
    path("signup", UserSignupView.as_view(), name="User-signup"),
    path("login", UserLoginView.as_view(), name="User-login"),
    path("admin/login", AdminLoginView.as_view(), name="Admin-login"),
    path("fill-form", QuizFormView.as_view(), name="Fill-Quiz-Form"),
    path("admin/create-quiz", CreateQuizView.as_view(), name="Create-Quiz"),
    path("get-quiz", GetQuizView.as_view(), name="Get-all-quizzes"),
    path("admin/add-question/<str:quiz_id>", AddQuestionsView.as_view(), name="add-question"),
    path("quiz/<str:quiz_id>", GetQuestionsByQuizId.as_view(), name="get-questions"),
    path("admin/update-quiz/<str:quiz_id>", UpdateQuizView.as_view(), name="get-questions"),
    path("submit/<str:quiz_id>/<str:question_id>", SubmitAnswersView.as_view(), name="Submit-answer"),
    path("admin/update-question/<str:question_id>", UpdateQuestionView.as_view(), name="update-question"),
    path("admin/dashboard", AdminPanelView.as_view(), name="admin-dashboard"),
    path("admin/get-users", GetUsersView.as_view(), name="get-users"),
    path("admin/get-all-quiz", GetAllQuiz.as_view(), name="get-all-quizes"),
    path("admin/delete-quiz/<str:quiz_id>", DeleteQuizView.as_view(), name="Delete-quiz"),
    path("admin/delete-question/<str:question_id>", DeleteQuestionView.as_view(), name="Delete-question"),
    path("logout", UserLogoutView.as_view(), name="user-logout"),

]