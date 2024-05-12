import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone


# Create your models here.

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True, blank=False)
    full_name = models.CharField(max_length=120)
    # phone = models.CharField(max_length=20, blank=True, null=True)
    # otp = models.CharField(max_length=6, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{str(self.email)}"


def validate_file_extension(value):
    allowed_extensions = ['jpg', 'jpeg', 'pdf']
    extension = str(value).lower().split('.')[-1]
    if extension not in allowed_extensions:
        raise ValidationError("Only JPG, JPEG, and PDF files are allowed.")


class QuizForm(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    user_photo = models.FileField(upload_to='user_photos/', validators=[validate_file_extension], null=True, blank=True)
    full_name = models.CharField(max_length=120)
    dob = models.DateField()
    age = models.IntegerField()
    father_name = models.CharField(max_length=120)
    phone_number = models.IntegerField()
    alter_phone_number = models.IntegerField()
    email = models.EmailField()
    qualifications = models.CharField(max_length=200)
    occupation_or_profession = models.CharField(max_length=200)
    address = models.CharField(max_length=550)
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120)
    pincode = models.IntegerField()
    state = models.CharField(max_length=120)
    aadhar_card = models.FileField(upload_to='aadhar/', validators=[validate_file_extension], null=True, blank=True)
    payment_done = models.BooleanField(default=False)

    def __str__(self):
        return f"{str(self.user)}"


class Quiz(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    # start_date = models.DateField(blank=True, null=True)
    # start_time = models.TimeField(blank=True, null=True)
    # end_date = models.DateField(blank=True, null=True)
    # end_time = models.TimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    # created_at = models.DateTimeField(default=timezone.now(), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"


class QuizQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    question = models.CharField(max_length=3000, null=True, blank=True)
    option_a = models.CharField(max_length=250, null=True, blank=True)
    option_b = models.CharField(max_length=250, null=True, blank=True)
    option_c = models.CharField(max_length=250, null=True, blank=True)
    option_d = models.CharField(max_length=250, null=True, blank=True)
    correct_option = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f"{self.quiz}/ {self.question}"


class UserAnswer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, blank=True, null=True)
    answer = models.CharField(max_length=120, null=False, blank=False, verbose_name="User Answer")
    is_correct = models.BooleanField(default=False, help_text="user answer is correct or not")
    is_answered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}/{self.question}/{self.answer}/{self.is_correct}"


class UserResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True, verbose_name="quiz attempt")
    total_questions = models.IntegerField(blank=True, null=True, verbose_name="Total questions attempts")
    right_answers = models.IntegerField(blank=True, null=True)
    wrong_answers = models.IntegerField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    result = models.CharField(default='FAIL', max_length=120, blank=True, null=True)


    def __str__(self):
        return f"{self.user}/{self.quiz}/{self.result}"


class UserGivenQuizes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, blank=True, null=True)
    has_given = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}/{self.quiz}/{self.has_given}"

