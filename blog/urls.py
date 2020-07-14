from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('about/',views.about,name='blog-about'),
    path('era/', views.era_view, name='blog-era'),
    path('saa/', views.saa_view, name='blog-saa'),
    path('sm/', views.sm_view, name='blog-sm'),
    path('sm/display/', views.sm_view_display, name='blog-sm-display'),
    path('sm/manage/', views.sm_view_manage, name='blog-sm-manage'),
    
    

    path('saa/se_a', views.saa_se_a_view, name='blog-saa-se-a'),
    
]
