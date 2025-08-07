from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
import xlsxwriter
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import *
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db.models import Q
from .ip_to_endereco import *

################################
##       CONTAS A PAGAR       ##
################################

@login_required
def ver_despesa(request, cod):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'ver_despesa.html', {'permissao': request.user.last_name,
    'cadastro': ContasPagar.objects.filter(id=cod)})


@login_required
def deletar_despesa(request, cod):
    ContasPagar.objects.filter(id=cod).update(status='Apagado em ' + str(datetime.now()) + ' pelo user: ' + str(request.user.username))
    return redirect(despesas)

@login_required
def despesas(request):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'despesas.html', {'permissao': request.user.last_name, 'despesas': ContasPagar.objects.filter(status='').order_by('-id')})

@login_required
def pre_nova_despesa(request):
    msg = ''
    if request.method == 'POST':
        usuario_pre_cadastro = request.user.username
        valor = request.POST.get('valor')
        vinculo = request.POST.get('vinculo')
        data = request.POST.get('data')
        obs = request.POST.get('obs')
        descricao = request.POST.get('descricao')
        long = request.POST.get('long')
        lat = request.POST.get('lat')
        entidade = request.POST.get('entidade')
        status = ''
        contas_pagar = PreCadastroContasPagar(usuario_pre_cadastro=usuario_pre_cadastro, valor=valor, vinculo=vinculo, data=data, obs=obs, descricao=descricao, status=status,
        lat=lat, long=long, entidade=entidade)
        contas_pagar.save()
        cod = contas_pagar.id
        msg = 'Salvo!'
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
        return redirect(nova_despesa, cod)
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'pre_nova_despesa.html', {'permissao': request.user.last_name, 'colaboradores': Colaboradores.objects.filter(status=''), 'msg': msg,
    'entidades': Entidade.objects.filter(status='')})

@login_required
def nova_despesa(request, cod):
    msg = 'Tela de cadastro. Tela de pre-cadastro encerrada.'
    if request.method == 'POST':
        usuario_cadastro = request.user.username
        valor = request.POST.get('valor')
        vinculo = request.POST.get('vinculo')
        data = request.POST.get('data')
        obs = request.POST.get('obs')
        descricao = request.POST.get('descricao')
        status = ''
        long = request.POST.get('long')
        lat = request.POST.get('lat')
        entidade = request.POST.get('entidade')
        #ARQUIVOS
        comprovante_pagamento = request.FILES.get('comprovante_pagamento')
        nota_fatura = request.FILES.get('comprovante_pagamento')
        ContasPagar(usuario_cadastro=usuario_cadastro, valor=valor, vinculo=vinculo, data=data, obs=obs, descricao=descricao, status=status,
        comprovante_pagamento=comprovante_pagamento, nota_fatura=nota_fatura, long=long, lat=lat, entidade=entidade).save()
        msg = 'Salvo!'
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'nova_despesa.html', {'permissao': request.user.last_name, 'colaboradores': Colaboradores.objects.filter(status=''), 'msg': msg, 
    'precadastro': PreCadastroContasPagar.objects.filter(id=cod), 'entidades': Entidade.objects.filter(status='')})

#######################
##       GERAL       ##
#######################

def sair(request):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post='Logout', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    logout(request)#informa ao sistema que o usuario esta fora dele
    return redirect(tela_login)#retorna a pagina de login

@login_required
def painel(request):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'painel.html', {'permissao': request.user.last_name})

def tela_login(request):
    if request.method == 'POST':
        name = request.POST['nome']
        senha = request.POST['senha']
        usu = authenticate(username=name, password=senha)
        if usu is not None:
            login(request, usu)
            localizar_ip = LocationService()
            resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
            Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post='login', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
            return redirect(painel)
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'tela_login.html')