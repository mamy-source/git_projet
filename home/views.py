from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.core.exceptions import PermissionDenied
from .models import User, Service, EmployeeProfile, ClientProfile
import json

# Fonctions utilitaires pour vérifier les rôles
def is_manager(user):
    return user.role == User.MANAGER

def is_employee(user):
    return user.role == User.EMPLOYEE

def is_client(user):
    return user.role == User.CLIENT

# Vues d'authentification
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue, {user.get_full_name()}!")
            
            # Redirection selon le rôle
            if user.role == User.MANAGER:
                return redirect('dashboard')
            elif user.role == User.EMPLOYEE:
                return redirect('employee_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Identifiants invalides.")
    
    # Design élégant avec Bootstrap
    return render(request, 'auth/login.html', {
        'title': 'Connexion',
        'hide_nav': True,
        'hide_footer': True,
        'body_class': 'bg-light'
    })

def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')

def register(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', User.CLIENT)
        phone_number = request.POST.get('phone_number', '')
        address = request.POST.get('address', '')
        
        # Validation
        errors = {}
        if password != password2:
            errors['password'] = "Les mots de passe ne correspondent pas."
        if User.objects.filter(username=username).exists():
            errors['username'] = "Ce nom d'utilisateur est déjà pris."
        if User.objects.filter(email=email).exists():
            errors['email'] = "Cet email est déjà utilisé."
        
        if not errors:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    phone_number=phone_number,
                    address=address
                )
                
                # Création du profil selon le rôle
                if role == User.CLIENT:
                    ClientProfile.objects.create(user=user)
                elif role == User.EMPLOYEE:
                    EmployeeProfile.objects.create(user=user)
                
                login(request, user)
                messages.success(request, "Compte créé avec succès!")
                return redirect('home')
            except Exception as e:
                errors['general'] = f"Une erreur est survenue: {str(e)}"
        
        # S'il y a des erreurs, on les affiche
        for field, error in errors.items():
            messages.error(request, error)
    
    return render(request, 'auth/register.html', {
        'title': 'Créer un compte',
        'role_choices': User.ROLE_CHOICES,
        'hide_nav': True,
        'hide_footer': True,
        'body_class': 'bg-light'
    })

# Vues pour les services (CRUD)
@login_required
def service_list(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'services/list.html', {
        'title': 'Nos services',
        'services': services,
        'is_manager': is_manager(request.user)
    })

@login_required
@user_passes_test(is_manager)
def service_create(request):
    if request.method == 'POST':
        try:
            # Récupération des données
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            duration = request.POST.get('duration')
            price = request.POST.get('price')
            commission_rate = request.POST.get('commission_rate')
            
            # Validation simple
            if not all([name, duration, price, commission_rate]):
                raise ValueError("Tous les champs obligatoires doivent être remplis.")
            
            # Création du service
            service = Service.objects.create(
                name=name,
                description=description,
                duration=duration,
                price=price,
                commission_rate=commission_rate
            )
            
            # Gestion de l'image
            if 'image' in request.FILES:
                image = request.FILES['image']
                image_name = f"services/{service.id}/{image.name}"
                service.image = default_storage.save(image_name, image)
                service.save()
            
            messages.success(request, "Service créé avec succès!")
            return redirect('service_list')
        except Exception as e:
            messages.error(request, f"Erreur lors de la création: {str(e)}")
    
    return render(request, 'services/create.html', {
        'title': 'Ajouter un service'
    })

@login_required
@user_passes_test(is_manager)
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        try:
            # Mise à jour des champs
            service.name = request.POST.get('name', service.name)
            service.description = request.POST.get('description', service.description)
            service.duration = request.POST.get('duration', service.duration)
            service.price = request.POST.get('price', service.price)
            service.commission_rate = request.POST.get('commission_rate', service.commission_rate)
            
            # Gestion de l'image
            if 'image' in request.FILES:
                # Suppression de l'ancienne image si elle existe
                if service.image:
                    default_storage.delete(service.image.path)
                
                image = request.FILES['image']
                image_name = f"services/{service.id}/{image.name}"
                service.image = default_storage.save(image_name, image)
            
            service.save()
            messages.success(request, "Service mis à jour avec succès!")
            return redirect('service_list')
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    
    return render(request, 'services/update.html', {
        'title': 'Modifier le service',
        'service': service
    })

@login_required
@user_passes_test(is_manager)
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        try:
            # Soft delete (désactivation)
            service.is_active = False
            service.save()
            messages.success(request, "Service désactivé avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
    
    return redirect('service_list')

# Vues pour le dashboard
@login_required
def dashboard(request):
    if is_manager(request.user):
        return manager_dashboard(request)
    elif is_employee(request.user):
        return employee_dashboard(request)
    else:
        return client_dashboard(request)

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    services = Service.objects.filter(is_active=True)
    employees = User.objects.filter(role=User.EMPLOYEE)
    clients = User.objects.filter(role=User.CLIENT)
    
    return render(request, 'admin/dashboard.html', {
        'title': 'Tableau de bord Manager',
        'services_count': services.count(),
        'employees_count': employees.count(),
        'clients_count': clients.count(),
        'recent_services': services.order_by('-id')[:5]
    })

@login_required
@user_passes_test(is_employee)
def employee_dashboard(request):
    employee_profile = request.user.employee_profile
    services = employee_profile.services.filter(is_active=True)
    appointments = []  # À remplacer par vos rendez-vous
    
    return render(request, 'dashboard/employee.html', {
        'title': 'Tableau de bord Employé',
        'services': services,
        'appointments': appointments,
        'work_schedule': json.loads(employee_profile.work_schedule) if employee_profile.work_schedule else {}
    })

@login_required
@user_passes_test(is_client)
def client_dashboard(request):
    client_profile = request.user.client_profile
    favorite_services = client_profile.favorite_services.all()
    appointments = []  # À remplacer par vos rendez-vous
    
    return render(request, 'dashboard/client.html', {
        'title': 'Tableau de bord Client',
        'favorite_services': favorite_services,
        'appointments': appointments,
        'receive_promotions': client_profile.receive_promotions
    })

# Vues pour la gestion des profils
@login_required
def profile(request):
    user = request.user
    profile = None
    
    if is_employee(user):
        profile = user.employee_profile
    elif is_client(user):
        profile = user.client_profile
    
    if request.method == 'POST':
        try:
            # Mise à jour des informations de base
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.phone_number = request.POST.get('phone_number', user.phone_number)
            user.address = request.POST.get('address', user.address)
            
            # Mise à jour du profil spécifique
            if is_employee(user) and profile:
                if 'image' in request.FILES:
                    if profile.image:
                        default_storage.delete(profile.image.path)
                    image = request.FILES['image']
                    image_name = f"employees/{user.id}/{image.name}"
                    profile.image = default_storage.save(image_name, image)
                
                profile.hourly_rate = request.POST.get('hourly_rate', profile.hourly_rate)
                profile.save()
            elif is_client(user) and profile:
                profile.receive_promotions = 'receive_promotions' in request.POST
                profile.save()
            
            user.save()
            messages.success(request, "Profil mis à jour avec succès!")
            return redirect('profile')
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    
    return render(request, 'profile/view.html', {
        'title': 'Mon profil',
        'profile': profile
    })

# API pour la gestion des services favoris (AJAX)
@require_POST
@login_required
@user_passes_test(is_client)
def toggle_favorite_service(request):
    service_id = request.POST.get('service_id')
    if not service_id:
        return JsonResponse({'status': 'error', 'message': 'ID de service manquant'}, status=400)
    
    service = get_object_or_404(Service, pk=service_id)
    client_profile = request.user.client_profile
    
    if service in client_profile.favorite_services.all():
        client_profile.favorite_services.remove(service)
        is_favorite = False
    else:
        client_profile.favorite_services.add(service)
        is_favorite = True
    
    return JsonResponse({
        'status': 'success',
        'is_favorite': is_favorite,
        'service_id': service_id
    })


def home(request):
    return render(request,'home/index.html')

def view_dashboard(request):
    return render(request, 'admin/dashboard.html')

def about(request):
    return render(request, 'home/about.html')

def blog_single(request):
    return render(request, 'home/blog-single.htm')

def blog(request):
    return render(request, 'home/blog.html')
def contact(request):
    return render(request, 'home/contact.html')

def pricing(request):
    return render (request, 'home/pricing.html')

def specialists(request):
    return render(request, 'home/specialists.html')

def treatements(request):
    return render(request, 'home/treatments.html')

def register_page(request):
    
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
