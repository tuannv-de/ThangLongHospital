from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup, CustomLoginView, dashboard, logout_view, predict

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from .views import update_status

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard, name='dashboard'),  # Đường dẫn tới trang dashboard
    path('update_status/', update_status, name='update_status'),
    path('predict/', predict, name='predict'),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
