from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('prevention/', views.prevention, name='prevention'),
    path('risk-factors/', views.risk, name='risk'), 
    path('assessment/', views.assessment, name='assessment'), 
    path('articles/', views.articles_public_list, name='articles_public_list'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),

    # --- Authentication --- 
    path('login/', views.loginview, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # --- Doctor Specific Views ---
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/articles/', views.article_list, name='doctor_article_list'), # List view
    # URL for handling the modal POST submission for articles
    path('doctor/articles/create/', views.article_create, name='article_create'), # <--- URL used in modal form action
    path('doctor/articles/<int:pk>/update/', views.article_update, name='doctor_article_update'),
    path('doctor/articles/<int:pk>/delete/', views.article_delete, name='doctor_article_delete'),

    path('doctor/tips/', views.tip_list, name='doctor_tip_list'), # List view
    # URL for handling the modal POST submission for tips
    path('doctor/tips/create/', views.tip_create, name='doctor_tip_create'), # <--- URL used in modal form action
    path('doctor/tips/<int:pk>/update/', views.tip_update, name='doctor_tip_update'),
    path('doctor/tips/<int:pk>/delete/', views.tip_delete, name='doctor_tip_delete'),

    path('doctor/model-info/', views.model_info, name='doctor_model_info'), # TODO: Link this in na


    path('usercontrol/dashboard/', views.is_doctor_check, name='admin_dashboard'), 

     path('doctor/download-json/', views.download_doctor_profile_json, name='download_your_data'),


    # path('admin/', views.admindashboard, name='admin_dashboard_view'), 



]

