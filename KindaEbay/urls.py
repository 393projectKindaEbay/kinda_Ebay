"""KindaEbay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from signup import views as v
from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.views.generic import TemplateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.contrib.auth.models import AbstractBaseUser
#123
from pages.views import home_view
from products.views import product_detail_view, product_create_view, product_list_view

from typing import List

UserModel = get_user_model()


class UsersListView(LoginRequiredMixin, ListView):
    http_method_names = ['get', ]

    def get_queryset(self):
        return UserModel.objects.all().exclude(id=self.request.user.id)

    def render_to_response(self, context, **response_kwargs):
        users: List[AbstractBaseUser] = context['object_list']

        data = [{
            "username": user.get_username(),
            "pk": str(user.pk)
        } for user in users]
        return JsonResponse(data, safe=False, **response_kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("signup/", v.register_request, name="signup_page"),
    path("login/", v.login_request, name="login"),
    path("logout/", v.logout_request, name='logout'),
    url(r'', include('django_private_chat2.urls', namespace='django_private_chat2')),
    path('users/', UsersListView.as_view(), name='users_list'),
    path('chat/', login_required(TemplateView.as_view(template_name='chat.html')), name='home'),
    #123
    path('', product_list_view, name = 'home'),
    path('create/', product_create_view),
    path('home/', product_list_view),
    path('product/<int:productid>/', product_detail_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)