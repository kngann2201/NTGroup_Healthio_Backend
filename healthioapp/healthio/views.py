from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, generics, parsers, status, request
from rest_framework.decorators import action
from rest_framework.response import Response
from healthio import models, serializers
from .paginators import ExercisePaginators, DishPaginators, PracticePaginators

# from django.http import HttpResponse
# def index(request):
#     return HttpResponse("Healthio App")

class ExerciseView(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = models.Exercise.objects.all()
    serializer_class = serializers.ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExercisePaginators

    def get_queryset(self):
        query = self.queryset
        q = self.request.GET.get('q')
        if q:
            query = query.filter(name__icontains=q)
        health_goal = self.request.GET.get('health_goal')
        if health_goal:
            query = query.filter(health_goal in health_goal)
        return query

class UserView(viewsets.ViewSet, generics.CreateAPIView):
    queryset = models.User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserRegisterSerializer
        return serializers.UserSerializer

    @action(methods=['get', 'patch'], url_path='current-user', detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        u = request.user
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                if k in ['first_name', 'last_name', 'email']:
                    setattr(u, k, v)
            u.save()
        return Response(serializers.UserSerializer(u).data, status=status.HTTP_200_OK)

class UserRegisterView(generics.CreateAPIView):
    serializer_class = serializers.UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class CustomerView(viewsets.ViewSet):
    queryset = models.Customer.objects.filter(user__is_active=True)
    serializer_class = serializers.CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get', 'patch'], url_path='profile', detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_profile(self, request):
        c = get_object_or_404(models.Customer, user=request.user)
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                if k in ['height', 'weight', 'health_goal', 'birth_year']:
                    setattr(c, k, v)
            c.save()
        return Response(serializers.CustomerSerializer(c).data, status=status.HTTP_200_OK)

    @action(methods=['get', 'post'], url_path="health-records", detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_health_records(self, request):
        c = get_object_or_404(models.Customer, user=request.user)
        if request.method.__eq__('GET'):
            records = models.HealthRecord.objects.select_related('customer').filter(customer=c).all()
            return Response(serializers.HealthRecordSerializer(records, many=True).data, status=status.HTTP_200_OK)
        serializer = serializers.HealthRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=c)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['get', 'post'], url_path="reminders", detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_reminders(self, request):
        c = get_object_or_404(models.Customer, user=request.user)
        if request.method.__eq__('GET'):
            reminders = models.Reminder.objects.select_related('customer').filter(customer=c).all()
            return Response(serializers.ReminderSerializer(reminders, many=True).data, status=status.HTTP_200_OK)
        serializer = serializers.ReminderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=c)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['get', 'post'], url_path="schedules", detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_schedules(self, request):
        c = get_object_or_404(models.Customer, user=request.user)
        if request.method.__eq__('GET'):
            schedules = models.Schedule.objects.select_related('customer').filter(customer=c).all()
            return Response(serializers.ScheduleSerializer(schedules, many=True).data, status=status.HTTP_200_OK)
        serializer = serializers.ScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=c)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExpertView(viewsets.ViewSet):
    queryset = models.Expert.objects.filter(user__is_active=True)
    serializer_class = serializers.ExpertSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get', 'patch'], url_path='profile', detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_profile(self, request):
        e = get_object_or_404(models.Expert, user=request.user)
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                if k in ['description']:
                    setattr(e, k, v)
            e.save()
        return Response(serializers.ExpertSerializer(e).data, status=status.HTTP_200_OK)

    @action(methods=['get', 'post'], url_path='exercise-samples', detail=False, permission_classes=[permissions.IsAuthenticated])
    def get_exercise_samples(self, request):
        e = get_object_or_404(models.Expert, user=request.user, role=models.ExpertRole.TRAINER)
        if request.method.__eq__('GET'):
            samples = models.ExerciseSample.objects.filter(expert=e).all()
            return Response(serializers.ExerciseSampleSerializer(samples, many=True).data, status=status.HTTP_200_OK)

        ex_id = request.query_params.get('exercise_id')
        if not ex_id:
            return Response({"message": "Chưa có mã bài tập!"}, status=400)
        exercise = models.Exercise.objects.filter(id=ex_id).first()
        serializer = serializers.ExerciseSampleSerializer(data=request.data, context={'exercise':exercise, 'expert':e})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['get', 'post'], url_path='dish-samples', detail=False,permission_classes=[permissions.IsAuthenticated])
    def get_dish_samples(self, request):
        e = get_object_or_404(models.Expert, user=request.user, role=models.ExpertRole.NUTRITIONIST)
        if request.method.__eq__('GET'):
            samples = models.DishSample.objects.filter(expert=e).all()
            return Response(serializers.DishSampleSerializer(samples, many=True).data, status=status.HTTP_200_OK)
        serializer = serializers.DishSampleSerializer(data=request.data, context={'expert': e})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class HealthRecordView(viewsets.ViewSet, generics.RetrieveUpdateAPIView):
    queryset = models.HealthRecord.objects.order_by('-created_at')
    serializer_class = serializers.HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExercisePaginators

    @action(methods=['get', 'post'], url_path='records', detail=True, permission_classes=[permissions.IsAuthenticated])
    def get_records(self, request, pk=None):
        h = get_object_or_404(models.HealthRecord, pk=pk)
        if h.customer.user != request.user:
            return Response({"message": "Khách mới có quyền xem các bản ghi sức khoẻ!"} ,status=status.HTTP_403_FORBIDDEN)

        if request.method.__eq__('GET'):
            records = models.Record.objects.select_related('health_record').filter(health_record=h).all()
            return Response(serializers.RecordSerializer(records, many=True).data, status=status.HTTP_200_OK)
        serializer = serializers.RecordSerializer(data=request.data, context={'health_record': h})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReminderView(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = models.Reminder.objects.all()
    serializer_class = serializers.ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

class ScheduleView(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = serializers.ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExercisePaginators

    def get_queryset(self):
        c_id = self.request.GET.get('customer_id')
        if c_id:
            c = get_object_or_404(models.Customer, id=c_id)
            return models.Schedule.objects.filter(customer=c).all()
        return models.Schedule.objects.all()

    @action(methods=['get', 'post'], url_path='practices', detail=True, permission_classes=[permissions.IsAuthenticated])
    def get_practices(self, request, pk):
        schedule = models.Schedule.objects.get(pk=pk)

        if request.method.__eq__('GET'):
            p = models.Practice.objects.select_related('schedule').filter(schedule=schedule).all()
            return Response(serializers.PracticeSerializer(p, many=True).data, status=status.HTTP_200_OK)
        serializer = serializers.PracticeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(schedule=schedule)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['get', 'post'], url_path='meals', detail=True, permission_classes=[permissions.IsAuthenticated])
    def get_meals(self, request, pk):
        schedule = models.Schedule.objects.get(pk=pk)

        if request.method.__eq__('GET'):
            m = models.Meal.objects.select_related('schedule').filter(schedule=schedule).all()
            return Response(serializers.MealSerializer(m, many=True).data, status=status.HTTP_200_OK)

        serializer = serializers.MealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(schedule=schedule)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PracticeView(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
    queryset = models.Practice.objects.select_related('schedule').order_by('-schedule__start_date', '-day_in_week')
    serializer_class = serializers.PracticeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PracticePaginators

    @action(methods=['get', 'post'], url_path='details', detail=True, permission_classes=[permissions.IsAuthenticated])
    def get_exercises(self, request, pk):
        p = models.Practice.objects.get(pk=pk)
        if request.method.__eq__('GET'):
            d = models.PracticeDetail.objects.filter(practice=p)
            return Response(serializers.PracticeDetailSerializer(d, many=True).data, status=status.HTTP_200_OK)
        ex_id = request.query_params.get('exercise_id')
        if not ex_id:
            return Response({"message": "Chưa có mã bài tập!"}, status=400)
        exercise = models.Exercise.objects.filter(id=ex_id).first()
        serializer = serializers.PracticeDetailSerializer(data=request.data, context={'practice': p, 'exercise': exercise})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PracticeDetailView(viewsets.ViewSet, generics.RetrieveUpdateAPIView):
    serializer_class = serializers.PracticeDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.PracticeDetail.objects.all()

    def perform_update(self, serializer):
        d = serializer.save()
        practice = d.practice
        practice.total_calories += d.calories_burned
        practice.save()

class MealView(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = models.Meal.objects.all()
    serializer_class = serializers.MealSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get', 'post'], url_path='details', detail=True, permission_classes=[permissions.IsAuthenticated])
    def get_dishes(self, request, pk):
        m = models.Meal.objects.get(pk=pk)
        if request.method.__eq__('GET'):
            d = models.MealDetail.objects.filter(meal=m)
            return Response(serializers.MealDetailSerializer(d, many=True).data, status=status.HTTP_200_OK)
        serializer = serializers.MealDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(meal=m)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MealDetailView(viewsets.ViewSet, generics.RetrieveUpdateAPIView):
    serializer_class = serializers.MealDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return models.MealDetail.objects.all()

class ContractView(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
    serializer_class = serializers.ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExercisePaginators

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'customer'):
            return models.Contract.objects.filter(customer=user.customer)
        elif hasattr(user, 'expert'):
            return models.Contract.objects.filter(expert=user.expert)
        return models.Contract.objects.none()

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'customer'):
            return Response({"message": "Chỉ khách mới có quyền gửi yêu cầu!"}, status=403)

        expert_id = request.query_params.get('expert_id')
        if not expert_id:
            return Response({"message": "Chưa có mã chuyên gia!"}, status=400)

        e = get_object_or_404(models.Expert, pk=expert_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=request.user.customer, expert=e)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    @action(methods=['get', 'post'], url_path='feedbacks', detail=True, permission_classes=[permissions.IsAuthenticated])
    def get_feedbacks(self, request, pk):
        contract = get_object_or_404(models.Contract, pk=pk)
        if request.method.__eq__('GET'):
            fbs = models.Feedback.objects.select_related('contract').filter(contract=contract).all()
            return Response(serializers.FeedbackSerializer(fbs, many=True).data, status=status.HTTP_200_OK)
        if not hasattr(request.user, 'customer'):
            return Response({"message": "Chỉ khách mới có quyền gửi yêu cầu!"}, status=403)
        serializer = serializers.FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(contract=contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['get', 'post'], url_path='requests', detail=True, permission_classes=[permissions.IsAuthenticated])
    def get_requests(self, request, pk):
        contract = get_object_or_404(models.Contract, pk=pk)
        if request.method.__eq__('GET'):
            rqs = models.Request.objects.select_related('contract').filter(contract=contract).all()
            return Response(serializers.RequestSerializer(rqs, many=True).data, status=status.HTTP_200_OK)
        if not hasattr(request.user, 'customer'):
            return Response({"message": "Chỉ khách mới có quyền gửi yêu cầu!"}, status=403)
        serializer = serializers.RequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(contract=contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ListExpertView(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = serializers.ExpertSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ExercisePaginators

    def get_queryset(self):
        sdt = self.request.query_params.get('phone_number')
        if not sdt:
            return models.Expert.objects.all().filter(processing_status=models.ProcessingStatus.PROCESSED)
        return models.Expert.objects.filter(user__phone_number=sdt, processing_status=models.ProcessingStatus.PROCESSED)


    @action(methods=['get'], url_path='feedbacks', detail=True, permission_classes=[permissions.AllowAny])
    def get_feedbacks(self, request, pk):
        e = get_object_or_404(models.Expert, pk=pk)
        contract = models.Contract.objects.filter(expert=e).all()
        fbs = models.Feedback.objects.filter(contract__in=contract)
        return Response(serializers.FeedbackSerializer(fbs, many=True).data, status=status.HTTP_200_OK)

class ExerciseSampleView(viewsets.ViewSet, generics.RetrieveUpdateAPIView):
    serializer_class = serializers.ExerciseSampleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExercisePaginators

    def get_queryset(self):
        return models.ExerciseSample.objects.filter(expert=self.request.user.expert)

class DishSampleView(viewsets.ViewSet, generics.RetrieveUpdateAPIView):
    serializer_class = serializers.DishSampleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DishPaginators

    def get_queryset(self):
        return models.DishSample.objects.filter(expert=self.request.user.expert)

class HealthGoalView(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = serializers.HealthGoalSerializer
    permission_classes = [permissions.AllowAny]
    queryset = models.HealthGoal.objects.all()

