from django.urls import path
from . import views
from . import employers, client

urlpatterns = [
    path('', views.home , name='home'),
    path('dashboard/', views.view_dashboard, name='dashboard'),
    path('emplyee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('about/', views.about, name='about'),
    path('blog-sigle/', views.blog_single, name='blog_single'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    path('pricing/', views.pricing, name='pricing'),
    path('specialists/', views.specialists, name='specialists'),
    path('treatments/', views.treatements, name='treatments'),

    #authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # Gestion des services
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/update/<int:pk>/', views.service_update, name='service_update'),
    path('services/delete/<int:pk>/', views.service_delete, name='service_delete'),
    
    # Gestion des profils
    path('profile/', views.profile, name='profile'),

    #client profile
    path('client/profile/', client.client_profile_view, name='client_profile'),

    # Profile URLs
    path('mon-profil/', employers.employee_profile_view, name='employee_profile'),
    path('mon-profil/creer/', employers.create_employee_profile, name='create_employee_profile'),
    path('mon-profil/modifier/', employers.update_employee_profile, name='update_employee_profile'),
    
    # Employee list and detail
    path('employes/', employers.employee_list_view, name='employee_list'),
    path('employes/<int:user_id>/', employers.employee_detail_view, name='employee_detail'),
    
    # API AJAX
    path('api/toggle-favorite/', views.toggle_favorite_service, name='toggle_favorite_service'),


    #team
    #path('team/add/', views.team_create, name='team_create'),
    # path('team/<int:pk>/edit/', views.team_update, name='team_update'),
    # path('team/<int:pk>/delete/', views.team_delete, name='team_delete'),
    # path('team/', views.team_list, name='team_list'),

    # #service
    # path('service/', views.service_list, name='service_list'),
    # path('service/create/', views.service_create, name='service_create'),
    # path('service/update/<int:pk>/', views.service_update, name='service_update'),
    # path('service/delete/<int:pk>/', views.service_delete, name='service_delete'),


]