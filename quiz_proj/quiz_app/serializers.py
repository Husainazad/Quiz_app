from rest_framework import serializers
from .models import CustomUser, QuizForm, Quiz, QuizQuestion, UserAnswer, UserResult


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    # creating the user object with in the serializer
    def create(self, validated_data):
        user = CustomUser.objects.create_user(email=validated_data["email"],
                                              full_name=validated_data["full_name"],
                                              password=validated_data["password"])
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = CustomUser
        fields = ["email", "password"]


class QuizFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizForm
        fields = '__all__'


class FileUploadSerializer(serializers.Serializer):

    user_photo = serializers.FileField(required=False)
    aadhar_card = serializers.FileField(required=False)

    def save(self, **kwargs):
        user_photo = self.validated_data.get('user_photo')
        aadhar_card = self.validated_data.get('aadhar_card')
        quiz_form = kwargs.get('quiz_form')

        if user_photo:
            quiz_form.user_photo = user_photo
        if aadhar_card:
            quiz_form.aadhar_card = aadhar_card

        quiz_form.save()


class CreateQuizSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200, required=True)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)

    class Meta:
        model = Quiz
        fields = "__all__"


class GetQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = "__all__"


class AddQuestionSerializer(serializers.ModelSerializer):
    question = serializers.CharField(required=True)
    option_a = serializers.CharField(required=True)
    option_b = serializers.CharField(required=True)
    option_c = serializers.CharField(required=True)
    option_d = serializers.CharField(required=True)
    correct_option = serializers.CharField(required=True)

    class Meta:
        model = QuizQuestion
        fields = "__all__"


class GetQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = "__all__"


class SubmitAnswerSerializer(serializers.ModelSerializer):
    answer = serializers.CharField(required=True)
    class Meta:
        model = UserAnswer
        fields = "__all__"


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResult
        fields = "__all__"


# class UpdateQuestionSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = QuizQuestion
#         fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "date_joined"]


