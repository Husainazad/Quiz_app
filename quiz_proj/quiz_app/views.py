from django.core.exceptions import ValidationError
from .serializers import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .helpers import get_tokens_for_user
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.contrib.auth import logout
from datetime import datetime, timedelta
from .models import UserGivenQuizes


# Create your views here.


class UserSignupView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data, 'msg': "User created successfully"},
                            status=status.HTTP_201_CREATED)
        return Response({
            "error": serializer.errors,
            "msg": "Something went wrong"
        }, status=status.HTTP_400_BAD_REQUEST)


# login views for all the users
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        is_user = authenticate(email=email, password=password)
        if is_user is not None:
            token = get_tokens_for_user(is_user)
            return Response({
                "email": is_user.email,
                "user_id": is_user.id,
                "access_token": token,
                "msg": "user login successfully"
            }, status=status.HTTP_200_OK)
        return Response({
            "msg": "Unfortunately the credentials you are entering is not matching our records."
                   "Please try again later or try resetting the credentials"
        }, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        is_user = authenticate(email=email, password=password)
        if is_user is not None and is_user.is_superuser:
            token = get_tokens_for_user(is_user)
            return Response({
                "email": is_user.email,
                "user_id": is_user.id,
                "access_token": token,
                "msg": "user login successfully"
            }, status=status.HTTP_200_OK)
        return Response({
            "msg": "Unfortunately the credentials you are entering is not matching our records."
                   "Please try again later or try resetting the credentials"
        }, status=status.HTTP_400_BAD_REQUEST)


class QuizFormView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        form_serializer = QuizFormSerializer(data=request.data)
        file_serializer = FileUploadSerializer(data=request.data)
        form_serializer.is_valid()
        file_serializer.is_valid()
        if form_serializer.is_valid() and file_serializer.is_valid():
            form_instance = form_serializer.save(user=request.user)
            file_serializer.save(quiz_form=form_instance)
            return Response({"msg": "Form Filled Successfully"}, status=status.HTTP_200_OK)

        return Response({"form_error": form_serializer.errors,
                         "file_error": file_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CreateQuizView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        quiz_data = request.data
        serializer = CreateQuizSerializer(data=quiz_data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({"msg": "Quiz Created Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class GetQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_timestamp = timezone.now()
        quizzes = Quiz.objects.filter(start_time__gte=current_timestamp)
        active_quizes = Quiz.objects.filter(start_time__lte=current_timestamp, end_time__gte=current_timestamp)
        if quizzes.exists():
            upcomingQuiz_Serializer = GetQuizSerializer(quizzes, many=True)
            activeQuiz_Serializer = GetQuizSerializer(active_quizes, many=True)
            return Response({"Upcoming_quiz": upcomingQuiz_Serializer.data, "active_quiz": activeQuiz_Serializer.data}, status=status.HTTP_200_OK)

        return Response({"msg": "There is no upcoming quiz!"}, status=status.HTTP_404_NOT_FOUND)


class GetQuestionsByQuizId(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            current_timestamp = timezone.now()
            quiz = Quiz.objects.get(id=quiz_id, start_time__lte=current_timestamp, end_time__gte=current_timestamp)
        except Quiz.DoesNotExist:
            return Response({"msg": "Quiz expired or haven't started yet, Please try again later!"}, status=status.HTTP_400_BAD_REQUEST)
        questions = QuizQuestion.objects.filter(quiz=quiz)
        questions = GetQuestionsSerializer(questions, many=True)
        if questions.data:
            for question in questions.data:
                try:
                    answer_instance = UserAnswer.objects.get(question=question["id"], user=request.user)
                    question.update(is_answered=answer_instance.is_answered)

                except UserAnswer.DoesNotExist:
                    question.update(is_answered=False)

            return Response({"data": questions.data}, status=status.HTTP_200_OK)

        return Response({"msg": "No questions added yet!"}, status=status.HTTP_404_NOT_FOUND)


class AddQuestionsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, quiz_id):
        questions = request.data
        try:
            quiz_instance = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"msg": f"No quiz found with the ID: '{quiz_id}'"})
        serializer = AddQuestionSerializer(data=questions)
        if serializer.is_valid():
            serializer.save(quiz=quiz_instance)
            return Response({"msg": "Question added successfully"}, status=status.HTTP_201_CREATED)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SubmitAnswersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id, question_id):
        data = request.data
        try:
            quiz_instance = Quiz.objects.get(id=quiz_id)
            question_instance = QuizQuestion.objects.get(id=question_id, quiz=quiz_instance)
            already_submitted = UserAnswer.objects.filter(user=request.user, question=question_instance,
                                                          quiz=quiz_instance).first()
            if already_submitted is not None:
                return Response({"msg": "Question already submitted by the user"}, status=status.HTTP_400_BAD_REQUEST)

        except Quiz.DoesNotExist:
            return Response({"msg": f"No quiz found with the ID: '{quiz_id}'"}, status=status.HTTP_404_NOT_FOUND)

        except QuizQuestion.DoesNotExist:
            return Response({"msg": f"No question found with the ID: '{question_id}' in quiz ID: {quiz_id}"},
                            status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            return Response({"msg": f"Invalid question ID"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubmitAnswerSerializer(data=data)
        if serializer.is_valid():
            if str(question_instance.correct_option) == str(serializer.validated_data["answer"]):
                serializer.save(user=request.user, quiz=quiz_instance, question=question_instance, is_correct=True,
                                is_answered=True)
            else:
                serializer.save(user=request.user, quiz=quiz_instance, question=question_instance, is_answered=True)

            return Response({"msg": "Answer Submitted", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UpdateQuestionView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, question_id):
        try:
            question = QuizQuestion.objects.get(id=question_id)

        except ValidationError as e:
            return Response({"msg": "Invalid question ID!"}, status=status.HTTP_400_BAD_REQUEST)

        except QuizQuestion.DoesNotExist:
            return Response({"msg": f"No question found with this ID: {question_id}"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GetQuestionsSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Quiz Updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"msg": "Something went wrong!", "error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class AdminPanelView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today_time - timedelta(days=7)
        users_joined_within_week = CustomUser.objects.filter(date_joined__gte=start_date)
        all_users = CustomUser.objects.all()
        todays_quiz = Quiz.objects.filter(start_time__gte=today_time, end_time__lte=today_time + timedelta(days=1))
        upcoming_quiz = Quiz.objects.filter(start_time__gte=timezone.now())

        return Response({"weekly_new_users": len(users_joined_within_week),
                         "all_users": len(all_users),
                         "today_quiz": len(todays_quiz),
                         "upcoming_quiz": len(upcoming_quiz)
                         }, status=status.HTTP_200_OK)


class GetUsersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        all_users = CustomUser.objects.filter(is_superuser=False)
        data = []
        for user in all_users:
            result_info = UserResult.objects.filter(user=user)
            passed_quiz = result_info.filter(result="PASS")

            combined_data = {
                # 'id': user_serializer.data["id"],
                # 'full_name': user_serializer.data["full_name"],
                # 'email': user_serializer.data["email"],
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                "number_of_quiz_attempt": len(result_info),
                "number_of_quiz_passed": len(passed_quiz),
                "number_of_quiz_failed": len(result_info) - len(passed_quiz)
            }
            data.append(combined_data)
        return Response({"data": data}, status=status.HTTP_200_OK)


class UpdateQuizView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, quiz_id):
        try:
            quiz_instance = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"msg": f"No quiz found with this ID: {quiz_id}"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GetQuizSerializer(quiz_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "msg": "Quiz Updated Successfully"}, status=status.HTTP_200_OK)

        return Response({"msg": "Something went wrong!", "error": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class ToggleCheckQuiz(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        try:
            quiz_instance = Quiz.objects.get(id=quiz_id)
            check_instance = UserGivenQuizes.objects.get(user=request.user, quiz=quiz_instance)

        except Quiz.DoesNotExist:
            return Response({"msg": f"No quiz found with this ID: {quiz_id}"}, status=status.HTTP_404_NOT_FOUND)

        except UserGivenQuizes.DoesNotExist:
            check_instance = UserGivenQuizes.objects.create(user=request.user, quiz=quiz_instance, has_given=True)
            return Response({"msg": "Toggled to True"},
                            status=status.HTTP_201_CREATED)

        if check_instance.has_given:
            return Response({"msg": "quiz already given"}, status=status.HTTP_200_OK)

        check_instance.has_given = True
        check_instance.save()
        return Response({"msg": "Toggled to True"},
                        status=status.HTTP_200_OK)


class CheckUserHasGivenQuiz(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz_instance = Quiz.objects.get(id=quiz_id)
            check_instance = UserGivenQuizes.objects.get(user=request.user, quiz=quiz_instance)
        except Quiz.DoesNotExist:
            return Response({"msg": f"No quiz found with this ID: {quiz_id}"}, status=status.HTTP_404_NOT_FOUND)

        except UserGivenQuizes.DoesNotExist:
            return Response({"msg": "quiz not given yet"}, status=status.HTTP_200_OK)

        if check_instance.has_given:
            return Response({"msg": "quiz already given"}, status=status.HTTP_200_OK)

        return Response({"msg": "quiz not given yet"}, status=status.HTTP_200_OK)


class GetAllQuiz(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        quizes = Quiz.objects.all()
        if quizes.exists():
            serializer = GetQuizSerializer(quizes, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"msg": "You haven't created any quiz!"}, status=status.HTTP_404_NOT_FOUND)


class DeleteQuizView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, quiz_id):
        try:
            quiz_instance = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"msg": f"No quiz found with this ID: {quiz_id}"}, status=status.HTTP_404_NOT_FOUND)
        quiz_instance.delete()
        return Response({"msg": "Quiz deleted successfully"}, status=status.HTTP_200_OK)


class DeleteQuestionView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, question_id):
        try:
            question_instance = QuizQuestion.objects.get(id=question_id)
        except ValidationError as e:
            return Response({"msg": f"Invalid question ID"}, status=status.HTTP_400_BAD_REQUEST)

        except QuizQuestion.DoesNotExist:
            return Response({"msg": f"No question found with this ID: {question_id}"}, status=status.HTTP_404_NOT_FOUND)

        question_instance.delete()
        return Response({"msg": "Question deleted successfully!"}, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'msg': 'User logged out Successfully.'}, status=status.HTTP_200_OK)
