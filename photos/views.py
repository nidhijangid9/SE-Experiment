from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from .models import Category, Photo, Comment
from .forms import CommentForm
from rest_framework import permissions
from django.contrib import messages 
from .forms import LoginForm, SignUpForm
from .serializers import (
    CategorySerializer, 
    PhotoSerializer, 
    CommentSerializer,
    UserSerializer
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def list(self, request, *args, **kwargs):
        if request.accepted_renderer.format == 'html':
            # Redirect to gallery if accessed via browser
            return redirect('gallery')
        return super().list(request, *args, **kwargs)
        
    def retrieve(self, request, *args, **kwargs):
        if request.accepted_renderer.format == 'html':
            # Redirect to photo detail if accessed via browser
            comment = self.get_object()
            return redirect('photo', pk=comment.photo.id)
        return super().retrieve(request, *args, **kwargs)

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        queryset = Photo.objects.all()
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category__name=category)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        categories = Category.objects.all()
        
        if request.accepted_renderer.format == 'html':
            return render(request, 'photos/gallery.html', {
                'photos': queryset,
                'categories': categories
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.accepted_renderer.format == 'html':
            comments = instance.comments.all()
            form = CommentForm()
            return render(request, 'photos/photo.html', {
                'photo': instance,
                'comments': comments,
                'form': form
            })
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if request.accepted_renderer.format == 'html':
            data = request.POST
            image = request.FILES.get('image')

            # Determine Category
            category = None
            if data.get('category') and data['category'] != '':
                try:
                    category = Category.objects.get(id=data['category'])
                except Category.DoesNotExist:
                    category = None
            elif data.get('category_new') and data['category_new'] != '':
                category, created = Category.objects.get_or_create(name=data['category_new'])

            # Create Photo
            if image and data.get('name'):
                Photo.objects.create(
                    name=data['name'],
                    category=category,
                    description=data.get('description', ''),
                    image=image,
                    user=request.user
                )
                return redirect('gallery')
                
            categories = Category.objects.all()
            return render(request, 'photos/add.html', {
                'categories': categories,
                'current_user': request.user
            })
        
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        photo = self.get_object()
        
        if request.accepted_renderer.format == 'html':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.photo = photo
                comment.user = request.user
                comment.save()
                return redirect('photo', pk=pk)
            return redirect('photo', pk=pk)
            
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                photo=photo
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer

def login_view(request):
    if request.user.is_authenticated:
        return redirect('gallery')
        
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('gallery')
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'photos/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('gallery')
        
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('gallery')
    
    return render(request, 'photos/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')

@login_required(login_url='login')
def view_gallery(request):
    category = request.GET.get('category')
    categories = Category.objects.all()

    if category is None:
        photos = Photo.objects.all()
    else:
        photos = Photo.objects.filter(category__name=category)

    context = {'categories': categories, 'photos': photos}
    return render(request, 'photos/gallery.html', context)

@login_required(login_url='login')
def view_photo(request, pk):
    photo = get_object_or_404(Photo, id=pk)
    comments = photo.comments.all()

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.photo = photo
            comment.user = request.user
            comment.save()
            return redirect('photo', pk=pk)
    else:
        form = CommentForm()

    context = {
        'photo': photo,
        'comments': comments,
        'form': form,
    }
    return render(request, 'photos/photo.html', context)

@login_required(login_url='login')
def add_photo(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        data = request.POST
        image = request.FILES.get('image')

        # Determine Category
        category = None
        if data.get('category') and data['category'] != '':
            try:
                category = Category.objects.get(id=data['category'])
            except Category.DoesNotExist:
                category = None
        elif data.get('category_new') and data['category_new'] != '':
            category, created = Category.objects.get_or_create(name=data['category_new'])

        # Create Photo
        if image and data.get('name'):
            Photo.objects.create(
                name=data['name'],
                category=category,
                description=data.get('description', ''),
                image=image,
                user=request.user
            )
            return redirect('gallery')

    context = {'categories': categories, 'current_user': request.user}
    return render(request, 'photos/add.html', context)