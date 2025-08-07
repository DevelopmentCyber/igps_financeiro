from django.conf.urls import url, include
#from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    #Despesas
    url(r'ver_despesa/(?P<cod>[0-9]+)/', views.ver_despesa, name="ver_despesa"),
    url(r'deletar_despesa/(?P<cod>[0-9]+)/', views.deletar_despesa, name="deletar_despesa"),
    url(r'despesas/', views.despesas, name="despesas"),
    url(r'nova_despesa/(?P<cod>[0-9]+)/', views.nova_despesa, name="nova_despesa"),
    url(r'pre_nova_despesa/', views.pre_nova_despesa, name="pre_nova_despesa"),
    #geral
    url(r'painel/', views.painel, name="painel"),
    url(r'sair/', views.sair, name="sair"),
    url(r'tela_login/', views.tela_login, name="tela_login"),
    url(r'accounts/', views.tela_login, name="tela_login"),
    url(r'^$', views.tela_login, name='tela_login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)