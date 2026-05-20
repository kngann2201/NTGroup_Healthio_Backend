from django.db.models import Avg
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from healthio import models


class HealthRecordSerializer(ModelSerializer):
    class Meta:
        model = models.HealthRecord
        fields = ['id', 'height', 'weight', 'drink_total', 'record_date']

    def validate_height(self, value):
        if value <= 0:
            raise serializers.ValidationError("Chiều cao không hợp lệ!")
        return value

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cân nặng không hợp lệ!")
        return value

class RecordSerializer(ModelSerializer):
    class Meta:
        model = models.Record
        fields = ['drink_amount', 'steps', 'heart_rate', 'created_at']

    def validate_drink_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Lượng nước không hợp lệ!")
        return value

    def create(self, validated_data):
        health_record = self.context['health_record']
        drink_amount = validated_data['drink_amount']
        record = models.Record.objects.create(
            health_record=health_record,
            **validated_data
        )
        health_record.drink_total += drink_amount
        health_record.save(update_fields=['drink_total'])
        return record

class UserSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            'id', 'first_name', 'last_name', 'username', 'password',
            'role', 'email', 'gender', 'phone_number', 'avatar'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if instance.avatar:
            data['avatar'] = request.build_absolute_uri(instance.avatar.url)
        else:
            data['avatar'] = None
        return data

class CustomerRegisterSerializer(ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['health_goal', 'birth_year']

class ExpertRegisterSerializer(ModelSerializer):
    class Meta:
        model = models.Expert
        fields = ['role', 'description', 'certificate', 'cv']

class UserRegisterSerializer(serializers.ModelSerializer):
    customer = CustomerRegisterSerializer(required=False)
    expert = ExpertRegisterSerializer(required=False)
    class Meta:
        model = models.User
        fields = ['id', 'username', 'password',
            'first_name', 'last_name',
            'role', 'customer', 'expert'
        ]

    def create(self, validated_data):
        customer_data = validated_data.pop('customer', None)
        expert_data = validated_data.pop('expert', None)
        user = models.User(**validated_data)
        user.set_password(user.password)
        user.save()
        if user.role == 1:
            health_goal_id = customer_data.pop('health_goal', None)
            if health_goal_id:
                customer_data['health_goal'] = models.HealthGoal.objects.get(id=health_goal_id)
            models.Customer.objects.create(user=user, **customer_data)
        elif user.role == 2:
            models.Expert.objects.create(user=user, **expert_data)
        return user

class CustomerSerializer(ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['id', 'health_goal', 'birth_year', 'updated_at']

class ExpertSerializer(ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = models.Expert
        fields = ['id', 'role', 'description', 'certificate', 'cv', 'updated_at', 'avg_star', 'user', 'processing_status']

class ReminderSerializer(ModelSerializer):
    class Meta:
        model = models.Reminder
        fields = ['id', 'reminder_time', 'reminder_type', 'active', 'content']

class ScheduleSerializer(ModelSerializer):
    customer = CustomerSerializer(required=False)
    class Meta:
        model = models.Schedule
        fields = ['id', 'start_date', 'num_of_weeks', 'active',
                  'schedule_name', 'meals', 'practices', 'customer']

class PracticeSerializer(ModelSerializer):
    class Meta:
        model = models.Practice
        fields = ['id', 'day_in_week', 'total_calories']

class ExerciseSerializer(ModelSerializer):
    class Meta:
        model = models.Exercise
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.url if instance.image else None
        return data

class PracticeDetailSerializer(ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    class Meta:
        model = models.PracticeDetail
        fields = ['id', 'exercise', 'duration', 'calories_burned', 'calories_target', 'actual_duration', 'is_complete']

    def create(self, validated_data):
        practice = self.context['practice']
        exercise = self.context['exercise']
        duration = validated_data['duration']
        calories_target = validated_data['calories_target']

        d = models.PracticeDetail.objects.create(
            practice=practice, exercise=exercise,
            duration=duration, calories_target=calories_target
        )
        return d

class MealSerializer(ModelSerializer):
    class Meta:
        model = models.Meal
        fields = ['id', 'day_in_week']

class MealDetailSerializer(ModelSerializer):
    class Meta:
        model = models.MealDetail
        fields = ['meal_type', 'name', 'calories', 'how_to_make',
                  'icon', 'quantity', 'unit']

class ContractSerializer(ModelSerializer):
    expert = ExpertSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = models.Contract
        fields = '__all__'

class FeedbackSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = models.Feedback
        fields = ['content', 'star', 'created_at', 'user']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            expert = self.contract.expert
            avg = models.Feedback.objects.filter(contract__expert=expert).aggregate(avg_star=Avg('star'))['avg_star'] or 0
            expert.avg_star = round(avg, 1)
            expert.save(update_fields=['avg_star'])

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.contract.customer.user).data if instance.contract.customer.user else None
        return data

class RequestSerializer(ModelSerializer):
    class Meta:
        model = models.Request
        fields = ['content', 'created_at']

class ExerciseSampleSerializer(ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)
    expert = ExpertSerializer(read_only=True)
    class Meta:
        model = models.ExerciseSample
        fields = '__all__'

    def create(self, validated_data):
        exercise = self.context['exercise']
        expert = self.context['expert']
        duration = validated_data['duration']
        s=models.ExerciseSample.objects.create(
            exercise=exercise, expert=expert, duration=duration
        )
        return s

class DishSampleSerializer(ModelSerializer):
    expert = ExpertSerializer(read_only=True)
    class Meta:
        model = models.DishSample
        fields = '__all__'

    def create(self, validated_data):
        expert = self.context['expert']
        d=models.DishSample.objects.create(
            expert=expert, **validated_data
        )
        return d


class HealthGoalSerializer(ModelSerializer):
    class Meta:
        model = models.HealthGoal
        fields = '__all__'
