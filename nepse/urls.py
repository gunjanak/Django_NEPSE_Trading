from django.urls import path
from .views import homePageView, nepseData

urlpatterns = [
    # path("",homePageView,name="home"),
    path("",nepseData,name="nepse_data"),
]