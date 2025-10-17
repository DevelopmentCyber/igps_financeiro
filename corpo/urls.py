from django.conf.urls import url, include
#from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    #Centro de custo
    url(r'relatorio_despesas_centro_custo/(?P<cod>[0-9]+)/', views.relatorio_despesas_centro_custo, name="relatorio_despesas_centro_custo"),
    url(r'despesas_centrocusto/(?P<cod>[0-9]+)/', views.despesas_centrocusto, name="despesas_centrocusto"),
    url(r'editar_centrocusto/(?P<cod>[0-9]+)/', views.editar_centrocusto, name="editar_centrocusto"),
    url(r'centrosdecusto/', views.centrosdecusto, name="centrosdecusto"),
    url(r'deletar_centrodecusto/(?P<cod>[0-9]+)/', views.deletar_centrodecusto, name="deletar_centrodecusto"),
    url(r'novo_centrocusto/', views.novo_centrocusto, name="novo_centrocusto"),
    #Fornecedor
    url(r'editar_fornecedor/(?P<cod>[0-9]+)/', views.editar_fornecedor, name="editar_fornecedor"),
    url(r'deletar_fornecedor/(?P<cod>[0-9]+)/', views.deletar_fornecedor, name="deletar_fornecedor"),
    url(r'fornecedores/', views.fornecedores, name="fornecedores"),
    url(r'consulta_cnpj/', csrf_exempt(views.consulta_cnpj), name="consulta_cnpj"),
    url(r'novo_fornecedor/', views.novo_fornecedor, name="novo_fornecedor"),
    #Despesas
    url(r'relatorio_despesas/', views.relatorio_despesas, name="relatorio_despesas"),
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