from django.urls import path
from .views import homePageView, nepseData,trading_simulation

urlpatterns = [
    # path("",homePageView,name="home"),
    path("",nepseData,name="nepse_data"),
    path("simulation/",trading_simulation,name="simulation"),
]