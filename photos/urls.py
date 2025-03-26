from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

# Setup the DRF router for API endpoints
router = DefaultRouter()
router.register(r'api/categories', views.CategoryViewSet)
router.register(r'api/photos', views.PhotoViewSet)
router.register(r'api/comments', views.CommentViewSet)

urlpatterns = [
    # Auth URLs
  
    
    # HTML URLs - using your existing view functions
    path('', views.view_gallery, name='gallery'),  
    path('photo/<str:pk>/', views.view_photo, name='photo'),
    path('add/', views.add_photo, name='add'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # API URLs
    path('api/', include(router.urls)),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Static and Media files configuration
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
