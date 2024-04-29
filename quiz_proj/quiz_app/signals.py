from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserAnswer, UserResult


@receiver(post_save, sender=UserAnswer)
def calculate_result(sender, instance, created, **kwargs):

    if created:
        try:
            user_result = UserResult.objects.get(user=instance.user, quiz=instance.quiz)
            if instance.is_correct:
                user_result.total_questions += 1
                user_result.right_answers += 1
                user_result.score += 4
                user_result.save()
                if user_result.score >= 40:
                    user_result.result = "PASS"
                    user_result.save()
            else:
                user_result.total_questions += 1
                user_result.wrong_answers += 1
                user_result.save()
                if user_result.score >= 40:
                    user_result.result = "PASS"
                    user_result.save()

        except UserResult.DoesNotExist:
            if instance.is_correct:
                user_result = UserResult.objects.create(
                    user=instance.user,
                    quiz=instance.quiz,
                    total_questions=1,
                    right_answers=1,
                    wrong_answers=0,
                    score=4,
                )
            else:
                user_result = UserResult.objects.create(
                    user=instance.user,
                    quiz=instance.quiz,
                    total_questions=1,
                    right_answers=0,
                    wrong_answers=1,
                    score=0
                )
