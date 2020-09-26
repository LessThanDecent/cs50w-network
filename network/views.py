import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post


def index(request):
    post_list = Post.objects.all()[::-1]
    page = request.GET.get('page', 1)

    paginator = Paginator(post_list, 10)
    try:
        posts = paginator.page(page)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/index.html", {
        "posts": posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def post(request):
    if request.method == "POST":
    
        if not request.POST["content"]:
            return HttpResponseRedirect(reverse('index'))
        
        if len(request.POST["content"]) > 255:
            return HttpResponseRedirect(reverse('index'))
        
        post = Post(user=request.user, content=request.POST["content"])
        post.save()

        return HttpResponseRedirect(reverse('index'))

def profile(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
    
    post_list = Post.objects.filter(user=user)[::-1]
    page = request.GET.get('page', 1)

    paginator = Paginator(post_list, 10)
    try:
        posts = paginator.page(page)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    return render(request, "network/profile.html", {
        "user_data": user,
        "posts": posts
    })

@login_required
def follow(request):
    if request.method == "POST":
        target = User.objects.get(id=request.POST["user_id"])
        user = request.user

        if target in user.following.all():
            user.following.remove(target)
        else:
            user.following.add(target)
        
        user.save()

        return HttpResponseRedirect(reverse("profile", args=[request.POST["user_id"]]))

@login_required
def following(request):
    post_list = Post.objects.filter(user__in=request.user.following.all())[::-1]
    page = request.GET.get('page', 1)

    paginator = Paginator(post_list, 10)

    try:
        posts = paginator.page(page)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/following.html", {
        "posts": posts
    })

@csrf_exempt
@login_required
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
        
        post.save()
        return HttpResponse(status=204)
