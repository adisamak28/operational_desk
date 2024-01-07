from django.urls import path
# from . import views
from webbrowser import get
from django.conf import settings
from django.conf.urls.static import static
from old_data_reqapi.controller.old_data_controller import OperationalDataController
from old_data_reqapi.controller.authentication_controller import (
    AuthenticationController, 
    HomeView, 
    LogoutView,
    AuthenticationAPI,
)
app_name = 'data_req'

urlpatterns = [
    path('login/', AuthenticationController.as_view(),name = "login" ),
    path('home/', HomeView.as_view(), name='home'),
    path('CN/', OperationalDataController.as_view({'get':'operational_data_details'}), name = "operational_data_details" ),
    path('auth_status', AuthenticationAPI.as_view(), name='auth_status'),
    path('logout/', LogoutView.as_view(),name = "logout" ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


