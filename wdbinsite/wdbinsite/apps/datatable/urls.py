from django.urls import path

from . import views

urlpatterns = [
    path('', views.fetch_table, name='data'),
    path('<str:pk>', views.indv_summary, name='summary'),
    path('<str:pk>/status', views.indv_status, name='status'),
    path('<str:pk>/rvcurve', views.indv_rvcurve, name='rvcurve'),
    path('<str:pk>/sed', views.indv_sed, name='sed'),
    path('<str:pk>/lightcurve', views.indv_lightcurve, name='lightcurve')
]