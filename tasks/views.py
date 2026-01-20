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
from .serializers import TaskSerializer




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
@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def task_detail_api(request,task_id):
    
    task= get_object_or_404(Task,id=task_id, user=request.user)

    if request.method=="GET":
        serializer=TaskSerializer(task)
        return Response(serializer.data)
    
    if request.method=="PUT":
        serializer=TaskSerializer(task,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method=="DELETE":
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)