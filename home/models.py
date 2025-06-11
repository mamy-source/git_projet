from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    CLIENT = 'CLIENT'
    EMPLOYEE = 'EMPLOYEE'
    MANAGER = 'MANAGER'
    
    ROLE_CHOICES = [
        (CLIENT, 'Client'),
        (EMPLOYEE, 'Employé'),
        (MANAGER, 'Manager'),
    ]
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=CLIENT)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Durée en minutes")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Pourcentage de commission pour l'employé"
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.price}€"

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    services = models.ManyToManyField(Service)
    image = models.ImageField(upload_to='employees/', blank=True, null=True)
    work_schedule = models.JSONField(default=dict)  # Ex: {'monday': ['09:00-12:00', '14:00-18:00'], ...}
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Profil employé de {self.user.get_full_name()}"

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    favorite_services = models.ManyToManyField(Service, blank=True)
    favorite_employee = models.ForeignKey(
        EmployeeProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    receive_promotions = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Profil client de {self.user.get_full_name()}"

class Appointment(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_appointments')
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='employee_appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('confirmed', 'Confirmé'),
            ('completed', 'Terminé'),
            ('pending', 'En attente'),
            ('cancelled', 'Annulé'),
            ('no_show', 'No Show'),
        ],
        default='En attente'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.client} avec {self.employee.user} pour {self.service} le {self.start_time}"

class Payment(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Paiement de {self.amount}€ pour le RDV {self.appointment.id}"

class DailyReport(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    date = models.DateField()
    total_earnings = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_commission = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    completed_appointments = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('employee', 'date')
    
    def __str__(self):
        return f"Rapport journalier de {self.employee.user} pour le {self.date}"

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('salary', 'Salaires'),
        ('product', 'Produits'),
        ('rent', 'Loyer'),
        ('utilities', 'Services publics'),
        ('other', 'Autres'),
    ]
    
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Dépense {self.get_category_display()} - {self.amount}€ le {self.date}"

class MonthlyFinancialReport(models.Model):
    month = models.DateField()  # Le premier du mois
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    appointments_count = models.PositiveIntegerField(default=0)
    most_popular_service = models.ForeignKey(
        Service, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        unique_together = ('month',)
    
    def __str__(self):
        return f"Rapport financier pour {self.month.strftime('%B %Y')}"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"