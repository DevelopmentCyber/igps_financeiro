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

###########################
##       CONTRATOS       ##
###########################

@login_required
def despesas_contrato(request, cod):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'despesas.html', {'permissao': request.user.last_name, 'despesas': ContasPagar.objects.filter(contrato=cod).order_by('-id')})

@login_required
def editar_contrato(request, cod):
    msg = ''
    if request.method == 'POST':
        vinculo = request.POST.get('vinculo').split('=')[0]
        nome_vinculo = request.POST.get('vinculo').split('=')[1]
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        valor = request.POST.get('valor')
        contrato = request.FILES.get('contrato')

        if contrato != None and contrato != '':
            ContratoReceita.objects.filter(id=cod).update(vinculo=vinculo, nome_vinculo=nome_vinculo, data_inicio=data_inicio, data_fim=data_fim, valor=valor, contrato=contrato)
        else:
            ContratoReceita.objects.filter(id=cod).update(vinculo=vinculo, nome_vinculo=nome_vinculo, data_inicio=data_inicio, data_fim=data_fim, valor=valor)

        msg = 'Salvo!'

        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'editar_contrato.html', {'permissao': request.user.last_name, 'msg': msg, 'entidades': Entidade.objects.filter(status=''), 'contrato': ContratoReceita.objects.filter(id=cod)})

@login_required
def deletar_contrato(request, cod):
    ContratoReceita.objects.filter(id=cod).update(status='Apagado em ' + str(datetime.now()) + ' pelo user: ' + str(request.user.username))
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return redirect(contratos)

@login_required
def contratos(request):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'contratos.html', {'permissao': request.user.last_name, 'contratos': ContratoReceita.objects.filter(status='').order_by('-id')})

@login_required
def novo_contrato(request):
    msg = ''
    if request.method == 'POST':
        vinculo = request.POST.get('vinculo').split('=')[0]
        nome_vinculo = request.POST.get('vinculo').split('=')[1]
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        valor = request.POST.get('valor')
        valor_atual_gasto = 0
        status = ''

        contrato = request.FILES.get('contrato')

        ContratoReceita(vinculo=vinculo, nome_vinculo=nome_vinculo, data_inicio=data_inicio, data_fim=data_fim, valor_atual_gasto=valor_atual_gasto, valor=valor, status=status, contrato=contrato).save()

        msg = 'Salvo!'

        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'novo_contrato.html', {'permissao': request.user.last_name, 'entidades': Entidade.objects.filter(status=''), 'msg': msg})

#################################
##       CENTRO DE CUSTO       ##
#################################

@login_required
def relatorio_despesas_centro_custo(request, cod):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    log = Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado)
    log.save()
    return render(request, 'relatorio_despesas.html', {'permissao': request.user.last_name, 'despesas': ContasPagar.objects.filter(status='', centrodecusto=cod),
    'usuario': request.user.username, 'cod': log.id})

@login_required
def despesas_centrocusto(request, cod):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'despesas.html', {'permissao': request.user.last_name, 'despesas': ContasPagar.objects.filter(status='', centrodecusto=cod).order_by('-id')})

@login_required
def editar_centrocusto(request, cod):
    msg = ''
    if request.method == 'POST':
        nome = request.POST.get('nome')

        CentroCusto.objects.filter(id=cod).update(nome=nome)

        msg = 'Salvo!'

        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'editar_centrocusto.html', {'permissao': request.user.last_name, 'msg': msg, 'centrodecusto': CentroCusto.objects.filter(id=cod)})

@login_required
def deletar_centrodecusto(request, cod):
    CentroCusto.objects.filter(id=cod).update(status='Apagado em ' + str(datetime.now()) + ' pelo user: ' + str(request.user.username))
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return redirect(centrosdecusto)

@login_required
def centrosdecusto(request):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'centrosdecusto.html', {'permissao': request.user.last_name, 'centrosdecusto': CentroCusto.objects.filter(status='').order_by('-id')})

@login_required
def novo_centrocusto(request):
    msg = ''
    if request.method == 'POST':
        nome = request.POST.get('nome')
        status = ''

        CentroCusto(nome=nome, status=status).save()

        msg = 'Salvo!'

        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'novo_centrocusto.html', {'permissao': request.user.last_name, 'msg': msg})

############################
##       FORNECEDOR       ##
############################

@login_required
def editar_fornecedor(request, cod):
    msg = ''
    if request.method == 'POST':
        razao_social = request.POST.get('razao_social')
        cnpj = request.POST.get('cnpj')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        n = request.POST.get('n')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        uf = request.POST.get('uf')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        contrato_social = request.FILES['contrato_social']
        cartao_cnpj = request.FILES['cartao_cnpj']
        data_abertura = request.POST.get('data_abertura')
        atuacao = request.POST.get('atuacao')
        status = ''

        Fornecedor.objects.filter(id=cod).update(razao_social=razao_social, cnpj=cnpj, cep=cep, rua=rua, n=n, bairro=bairro, cidade=cidade, uf=uf, telefone=telefone, email=email,
        data_abertura=data_abertura, atuacao=atuacao, status=status)

        if contrato_social != None and contrato_social != '':
            for f in Fornecedor.objects.filter(id=cod):
                f.contrato_social = contrato_social
                f.save()

        if cartao_cnpj != None and cartao_cnpj != '':
            for f in Fornecedor.objects.filter(id=cod):
                f.cartao_cnpj = cartao_cnpj
                f.save()

        msg = 'Salvo!'

        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'editar_fornecedor.html', {'permissao': request.user.last_name, 'msg': msg, 'fornecedor': Fornecedor.objects.filter(id=cod)})

@login_required
def deletar_fornecedor(request, cod):
    Fornecedor.objects.filter(id=cod).update(status='Apagado em ' + str(datetime.now()) + ' pelo user: ' + str(request.user.username))
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return redirect(fornecedores)

@login_required
def fornecedores(request):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'fornecedores.html', {'permissao': request.user.last_name, 'fornecedores': Fornecedor.objects.filter(status='').order_by('-id')})

@csrf_exempt
def consulta_cnpj(request):
    cnpj = json.loads(request.body)['cnpj']
    response  = requests.get('http://receitaws.com.br/v1/cnpj/' + str(cnpj))
    #print(dict(response.text))
    return JsonResponse(data=json.loads(response.text))

@login_required
def novo_fornecedor(request):
    msg = ''
    if request.method == 'POST':
        razao_social = request.POST.get('razao_social')
        cnpj = request.POST.get('cnpj')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        n = request.POST.get('n')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        uf = request.POST.get('uf')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        contrato_social = request.FILES['contrato_social']
        cartao_cnpj = request.FILES['cartao_cnpj']
        data_abertura = request.POST.get('data_abertura')
        atuacao = request.POST.get('atuacao')
        status = ''

        Fornecedor(razao_social=razao_social, cnpj=cnpj, cep=cep, rua=rua, n=n, bairro=bairro, cidade=cidade, uf=uf, telefone=telefone, email=email, contrato_social=contrato_social,
        cartao_cnpj=cartao_cnpj, data_abertura=data_abertura, atuacao=atuacao, status=status).save()

        msg = 'Salvo!'

        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'novo_fornecedor.html', {'permissao': request.user.last_name, 'msg': msg})

################################
##       CONTAS A PAGAR       ##
################################

@login_required
def relatorio_despesas(request):
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    log = Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado)
    log.save()
    return render(request, 'relatorio_despesas.html', {'permissao': request.user.last_name, 'despesas': ContasPagar.objects.filter(status=''),
    'usuario': request.user.username, 'cod': log.id, 'x': 1})

@login_required
def ver_despesa(request, cod):
    msg = ''
    if request.method == 'POST':
        comprovante_pagamento = request.FILES['comprovante_pagamento']
        nota_fatura = request.FILES['nota_fatura']

        if comprovante_pagamento != None and comprovante_pagamento != '':
            for c in ContasPagar.objects.filter(id=cod):
                c.comprovante_pagamento = comprovante_pagamento
                c.save()

        if nota_fatura != None and nota_fatura != '':
            for c in ContasPagar.objects.filter(id=cod):
                c.nota_fatura = nota_fatura
                c.save()

        msg = 'Salvo!'

        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'ver_despesa.html', {'permissao': request.user.last_name,
    'cadastro': ContasPagar.objects.filter(id=cod), 'msg': msg})

@login_required
def deletar_despesa(request, cod):
    ContasPagar.objects.filter(id=cod).update(status='Apagado em ' + str(datetime.now()) + ' pelo user: ' + str(request.user.username))
    localizar_ip = LocationService()
    resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
    Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
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
        centrodecusto = request.POST.get('centrodecusto')
        contrato = request.POST.get('contrato')
        status = ''
        contas_pagar = PreCadastroContasPagar(usuario_pre_cadastro=usuario_pre_cadastro, valor=valor, vinculo=vinculo, data=data, obs=obs, descricao=descricao, status=status,
        lat=lat, long=long, entidade=entidade, centrodecusto=centrodecusto, contrato=contrato)
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
    'entidades': Entidade.objects.filter(status=''), 'fornecedores': Fornecedor.objects.filter(status=''), 'centrosdecusto': CentroCusto.objects.filter(status=''),
    'contratos': ContratoReceita.objects.filter(status='')})

@login_required
def nova_despesa(request, cod):
    msg = 'Tela de cadastro. Tela de pre-cadastro encerrada.'
    if request.method == 'POST':
        usuario_cadastro = request.user.username
        valor = request.POST.get('valor')
        vinculo = request.POST.get('vinculo').split('-')[0] + '-' + request.POST.get('vinculo').split('-')[1]
        nome_vinculo = request.POST.get('vinculo').split('-')[1]
        data = request.POST.get('data')
        obs = request.POST.get('obs')
        descricao = request.POST.get('descricao')
        status = ''
        long = request.POST.get('long')
        lat = request.POST.get('lat')
        entidade = request.POST.get('entidade')
        centrodecusto = request.POST.get('centrodecusto')
        contrato = request.POST.get('contrato')
        #ARQUIVOS
        comprovante_pagamento = request.FILES.get('comprovante_pagamento')
        nota_fatura = request.FILES.get('comprovante_pagamento')
        ContasPagar(usuario_cadastro=usuario_cadastro, valor=valor, nome_vinculo=nome_vinculo, vinculo=vinculo, data=data, obs=obs, descricao=descricao, status=status,
        comprovante_pagamento=comprovante_pagamento, nota_fatura=nota_fatura, long=long, lat=lat, entidade=entidade, centrodecusto=centrodecusto, contrato=contrato).save()
        for c in ContratoReceita.objects.filter(id=contrato):
            valor_atual = c.valor_atual_gasto
            valor_novo = float(valor.replace('.', '').replace('.', '').replace('.', '').replace('.', '').replace('.', '').replace('.', '').replace(',', '.')) - float(valor_atual)
            c.valor_atual_gasto = valor_novo
            c.save()
            #ContratoReceita.objects.filter(id=contrato).update(valor_atual_gasto=valor_novo)
        msg = 'Salvo!'
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user.username, data_hora=datetime.now(), dados_post=request.POST.items(), dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    else:
        localizar_ip = LocationService()
        resultado = localizar_ip.get_location(str(request.META.get('REMOTE_ADDR')))
        Logs(usuario=request.user, data_hora=datetime.now(), dados_post='', dados_pc_acesso=request.META.get('HTTP_USER_AGENT', ''), ip=request.META.get('REMOTE_ADDR'), tipo_acesso=request.method, pagina=request.path, endereco=resultado).save()
    return render(request, 'nova_despesa.html', {'permissao': request.user.last_name, 'colaboradores': Colaboradores.objects.filter(status=''), 'msg': msg, 
    'precadastro': PreCadastroContasPagar.objects.filter(id=cod), 'entidades': Entidade.objects.filter(status=''), 'fornecedores': Fornecedor.objects.filter(status=''),
    'centrosdecusto': CentroCusto.objects.filter(status=''), 'contratos': ContratoReceita.objects.filter(status='')})

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