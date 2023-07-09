from django.shortcuts import render, redirect
from django.http import HttpResponse
from . models import Conta, Categoria
from django.contrib import messages
from django.contrib.messages import constants 
from .utils import calcula_total, calula_equilibrio_financeiro
from extrato.models import Valores
from datetime import datetime

def home(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')

    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')

    contas = Conta.objects.all()
    total_contas = calcula_total(contas, 'valor')

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calula_equilibrio_financeiro()
   
    return render(request, 'home.html', {'contas': contas, 
                                         'total_contas': total_contas,
                                         'total_entradas': total_entradas,
                                         'total_saidas': total_saidas,
                                         'percentual_gastos_essenciais': int(percentual_gastos_essenciais),
                                         'percentual_gastos_nao_essenciais': int(percentual_gastos_nao_essenciais)})


def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_conta = calcula_total(contas, 'valor')
    return render(request, 'gerenciar.html', {'contas': contas, 'total_conta': total_conta, 'categorias': categorias})


def cadastrar_banco(resquest):
    apelido = resquest.POST.get('apelido').upper()
    banco = resquest.POST.get('banco')
    tipo = resquest.POST.get('tipo')
    valor = resquest.POST.get('valor')
    icone = resquest.FILES.get('icone')

    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(resquest, constants.ERROR, 'Preencha Todos os Campos')
        return redirect('/perfil/gerenciar/')
        #colocar mensagem de erro

    conta = Conta(
        apelido=apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save()
    messages.add_message(resquest, constants.SUCCESS, 'Conta Cadastrada com Sucesso!!')

    return redirect('/perfil/gerenciar/')


def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()
    messages.add_message(request, constants.SUCCESS, 'Conta Deletada com Sucesso!!')
    return redirect('/perfil/gerenciar/')


def cadastrar_categoria(request):
    nome = request.POST.get('categoria').upper()
    essencial = bool(request.POST.get('essencial'))

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria Cadastrada com Sucesso!!')
    return redirect('/perfil/gerenciar/')


def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.essencial = not categoria.essencial
    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria Atualizada com Sucesso!!')
    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}

    categorias = Categoria.objects.all()

    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria=categoria)
        for v in valores:
            total = total + v.valor
        dados[categoria.categoria] = total
    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 
                                              'values': list(dados.values())})

