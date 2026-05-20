from django.urls import path, include
from rest_framework.routers import DefaultRouter
from healthio import views

r = DefaultRouter()
r.register('users', views.UserView, basename='user')
r.register('customers', views.CustomerView, basename='customer')
r.register('experts', views.ExpertView, basename='expert')
r.register('health-records', views.HealthRecordView, basename='health-record')
r.register('reminders', views.ReminderView, basename='reminder')
r.register('schedules', views.ScheduleView, basename='schedule')
r.register('practices', views.PracticeView, basename='practice')
r.register('exercises', views.ExerciseView, basename='exercise')
r.register('meals', views.MealView, basename='meal')
r.register('contracts', views.ContractView, basename='contract')
r.register('list-experts', views.ListExpertView, basename='list-expert')
r.register('meal-details', views.MealDetailView, basename='meal-detail')
r.register('practice-details', views.PracticeDetailView, basename='practice-detail')
r.register('exercise-samples', views.ExerciseSampleView, basename='exercise-sample')
r.register('dish-samples', views.DishSampleView, basename='dish-sample')
r.register('health-goals', views.HealthGoalView, basename='health-goal')



urlpatterns = [
    path('', include(r.urls))
]