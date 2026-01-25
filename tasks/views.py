from django.shortcuts import render,redirect,get_object_or_404
from .models import Task
from .forms import TaskForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import TaskSerializer
from rest_framework.permissions import AllowAny



# Create your views here.
@login_required(login_url="/accounts/login/")
@never_cache
def home(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect("home")

    form = TaskForm()
    tasks = Task.objects.filter(user=request.user)
    return render(request, "home.html", {"tasks": tasks, "form": form})


from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token

@api_view(["POST"])
@permission_classes([AllowAny])
def signup_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=400)

    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "message": "User created successfully",
        "token": token.key
    }, status=201)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})
        

@login_required
def toggle_task(request,task_id):
    task=get_object_or_404(Task,id=task_id,user=request.user)
    task.completed=not task.completed
    task.save()
    return redirect("home")

@login_required
def delete_task(request,task_id):
    task=get_object_or_404(Task,id=task_id,user=request.user)
    task.delete()
    return redirect("home")

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def task_list_api(request):

    if request.method == "GET":
        tasks = Task.objects.filter(user=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(user=request.user)
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def task_detail_api(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "GET":
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    if request.method == "PATCH":
        # toggle completed
        task.completed = not task.completed
        task.save()
        return Response(TaskSerializer(task).data)

    if request.method == "DELETE":
        task.delete()
        return Response({"message": "Task deleted"}, status=status.HTTP_204_NO_CONTENT)