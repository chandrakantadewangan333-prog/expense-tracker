
from django.urls import path
from ExpenseTracker import views
from django.conf.urls.static import static
from tracker import settings

urlpatterns = [
    path('', views.home, name='home'),  # root of society/ prefix
    path('registered/',views.registered,name="registered"),
    path('logins/',views.logins,name='logins'),
    path('login/',views.login,name="login"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('expenses/',views.expenses,name="expenses"),
    path('add/',views.add,name="add"),
    path('filter-month/', views.filter_month, name='filter_month'),
    path('jan/',views.jan,name="jan"),
    path('update/<int:id>/',views.update,name="update"),
    path('update_submit/<int:id>/', views.update_submit, name='update_submit'),
    path('delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('set_limit/', views.set_limit, name='set_limit'),
    path('logout/', views.logout_view, name='logout'),
]+ static(settings.STATIC_URL,document_root=settings.STATICFILES_DIRS)
