from django.contrib.auth.models import AbstractUser
from django.db import models
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class UserRole(models.IntegerChoices):
    CUSTOMER = 1, 'Khách hàng'
    EXPERT = 2, 'Chuyên gia'

class ExpertRole(models.IntegerChoices):
    TRAINER = 1, 'Huấn luyện viên'
    NUTRITIONIST = 2, 'Chuyên gia dinh dưỡng'

class ContractStatus(models.IntegerChoices):
    WAIT = 1, 'Chờ kết nối'
    APPLY = 2, 'Đang kết nối'
    ADJUST = 3, 'Chờ điều chỉnh'

class ProcessingStatus(models.IntegerChoices):
    PENDING = 1, 'Đang chờ xử lí'
    PROCESSED = 2, 'Đã được duyệt'
    REFUSE = 3, 'Bị từ chối'

class HealthGoal(Base):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class ScheduleName(models.IntegerChoices):
    PRACTICE = 1, 'Luyện tập'
    MEAL = 2, 'Bữa ăn'

class ScheduleStatus(models.IntegerChoices):
    PREVIEW = 1, 'Xem trước',
    USING = 2, 'Đang áp dụng',
    FINISHED = 3, 'Đã hoàn thành',
    CANCEL = 4, 'Đã huỷ'

class MealType(models.IntegerChoices):
    BREAKFAST = 1, 'Bữa sáng'
    LUNCH = 2, 'Bữa trưa'
    DINNER = 3, 'Bữa tối'

class ReminderType(models.IntegerChoices):
    DRINK = 1, 'Nhắc uống nước'
    PRACTICE = 2, 'Nhắc tập luyện'
    REST = 3, 'Nhắc nghỉ ngơi'

class Exercise(Base):
    name = models.CharField(max_length=100)
    description = models.TextField()
    MET = models.FloatField(default=0.0)
    image = CloudinaryField(null=True)
    health_goal = models.ManyToManyField(HealthGoal)
    def __str__(self):
        return self.name

class Gender(models.IntegerChoices):
    MALE = 1, 'Nam'
    FEMALE = 2, 'Nữ'

class Schedule(Base):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    expert = models.ForeignKey('Expert', on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    num_of_weeks = models.IntegerField()
    active = models.BooleanField(default=True)
    schedule_name = models.IntegerField(choices=ScheduleName.choices)
    def __str__(self):
        return self.customer.user.first_name + ' ' + self.customer.user.last_name + ', '\
                + self.get_schedule_name_display() + ' mã: ' +  str(self.id)

class Practice(Base):
    day_in_week = models.IntegerField()
    total_calories = models.FloatField()
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='practices', null=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schedule', 'day_in_week'],
                name='unique_practice_per_schedule'
            )
        ]

class PracticeDetail(Base):
    duration = models.IntegerField()
    calories_burned = models.FloatField(default=0)
    calories_target = models.FloatField()
    actual_duration = models.IntegerField(default=0)
    is_complete = models.BooleanField(default=False)
    practice = models.ForeignKey('Practice', on_delete=models.CASCADE, related_name='practice_details')
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE, related_name='practice_details')

class HealthDiary(Base):
    content = RichTextField(null=False)
    practice = models.OneToOneField('Practice', on_delete=models.PROTECT, null=False)

class Meal(Base):
    day_in_week = models.IntegerField()
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='meals', null=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schedule', 'day_in_week'],
                name='unique_meal_per_day_per_schedule'
            )
        ]
    def __str__(self):
        return 'Ngày' + ' ' + str(self.day_in_week)

class MealDetail(Base):
    meal_type = models.IntegerField(choices=MealType.choices)
    name = models.CharField(max_length=100)
    calories = models.IntegerField(default=0)
    how_to_make = RichTextField(null=True, blank=True)
    icon = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=100, null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    meal = models.ForeignKey('Meal', on_delete=models.CASCADE, related_name='meal_details')

class User(AbstractUser):
    avatar = CloudinaryField(default="https://res.cloudinary.com/dkzxdp1gi/image/upload/v1767843265/avatar-trang-nu-001_dym4n0.webp")
    gender = models.IntegerField(choices=Gender.choices, default=Gender.MALE)
    phone_number = models.CharField(max_length=10, null=True, blank=True, unique=True)
    role = models.IntegerField(choices=UserRole.choices, default=UserRole.CUSTOMER)
    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Expert(Base):
    role = models.IntegerField(choices=ExpertRole.choices, default=ExpertRole.TRAINER)
    certificate = CloudinaryField(null=True, blank=True)
    cv = models.FileField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    processing_status = models.IntegerField(choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING)
    avg_star = models.FloatField(default=0)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

class Customer(Base):
    birth_year = models.IntegerField(null=True)
    health_goal = models.ForeignKey('HealthGoal', on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

class HealthRecord(Base):
    height = models.IntegerField(null=True)
    weight = models.FloatField(null=True)
    drink_total = models.IntegerField(default=0)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='health_records')
    record_date = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'record_date'],
                name='unique_daily_record'
            )
        ]

    def __str__(self):
        return self.customer.user.first_name + ' ' + self.customer.user.last_name + ', '\
            + self.created_at.strftime("%Y-%m-%d %H:%M:%S")

class Record(Base):
    drink_amount = models.IntegerField(default=0)
    steps = models.IntegerField(default=0)
    heart_rate = models.IntegerField(default=0)
    health_record = models.ForeignKey('HealthRecord', on_delete=models.CASCADE)

class Reminder(Base):
    reminder_time = models.TimeField()
    reminder_type = models.IntegerField(choices=ReminderType.choices)
    active = models.BooleanField(default=True)
    content = models.TextField(null=True, blank=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

class DishSample(Base):
    name = models.CharField(max_length=100)
    calories = models.IntegerField()
    image = CloudinaryField(null=True, blank=True)
    how_to_make = RichTextField()
    expert = models.ForeignKey('Expert', on_delete=models.CASCADE, related_name='dish_samples')
    def __str__(self):
        return self.name

class ExerciseSample(Base):
    duration = models.IntegerField()
    expert = models.ForeignKey('Expert', on_delete=models.CASCADE, related_name='exercise_samples')
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE, related_name='exercise_samples')

class Contract(Base):
    start_date = models.DateField()
    end_date = models.DateField()
    contract_status = models.IntegerField(choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING)
    active = models.BooleanField(default=False)
    expert = models.ForeignKey('Expert', on_delete=models.PROTECT, related_name='contracts')
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT, related_name='contracts')

class Feedback(Base):
    content = models.TextField(null=False)
    star = models.IntegerField(default=0)
    contract = models.OneToOneField('Contract', on_delete=models.CASCADE)

class Request(Base):
    content = models.TextField(null=False)
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)

class Conversation(Base):
    last_message = models.TextField(null=True)
    contract = models.OneToOneField('Contract', on_delete=models.PROTECT)

class Message(Base):
    content = models.TextField(null=False)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE)
    sender = models.ForeignKey('User', on_delete=models.CASCADE, null=True)

