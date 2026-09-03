from django.shortcuts import render, get_object_or_404
from motorartigos.models import Responsavel, Comercio, EixoTecnologia
from django.db.models import Q

import os
import hmac
import hashlib
import subprocess

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def update_server(request):

    if request.method != 'POST':
        return HttpResponseForbidden('Method not allowed')

    # Secret configurado no GitHub e no PythonAnywhere
    secret = os.environ.get('GITHUB_WEBHOOK_SECRET')

    if not secret:
        return HttpResponseForbidden('Webhook secret not configured')

    # Assinatura enviada pelo GitHub
    signature = request.headers.get('X-Hub-Signature-256', '')

    if not signature.startswith('sha256='):
        return HttpResponseForbidden('Invalid signature')

    expected_signature = 'sha256=' + hmac.new(
        secret.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return HttpResponseForbidden('Invalid signature')

    # Caminho real do projeto
    project_dir = '/home/pythondavi/prova'

    try:

        subprocess.run(
            [
                'git',
                '-C',
                project_dir,
                'pull',
                'origin',
                'aula12_finalizando_artigo'
            ],
            check=True
        )

        # Recarrega o Django
        wsgi_file = '/var/www/pythondavi_pythonanywhere_com_wsgi.py'

        subprocess.run(
            ['touch', wsgi_file],
            check=True
        )

        return HttpResponse(
            'Server updated successfully',
            status=200
        )

    except subprocess.CalledProcessError as e:

        return HttpResponse(
            f'Git update failed: {e}',
            status=500
        )


def index(request):
    comercios_base = Comercio.objects.filter(publicada=True)
    
    eixos = EixoTecnologia.objects.all()

    termo_busca = request.GET.get('busca')
    eixo_id = request.GET.get('eixo')

    comercios_todos = comercios_base

    if eixo_id:
        comercios_todos = comercios_todos.filter(
            id_fk_eixo__id=eixo_id
        )

    if termo_busca:
        comercios_todos = comercios_todos.filter(
            Q(titulo__icontains=termo_busca) | 
            Q(texto__icontains=termo_busca) |
            Q(id_fk_responsavel__nome__icontains=termo_busca) |
            Q(id_fk_eixo__nome__icontains=termo_busca)
        )
    
    comercios_recentes = comercios_base.order_by(
        '-data_publicacao'
    )[:4]

    contexto = {
        'artigos': comercios_todos,
        'artigos_recentes': comercios_recentes,
        'eixos': eixos,
        'eixo_selecionado': eixo_id,
        'termo_busca': termo_busca
    }

    return render(
        request,
        'motorartigos/index.html',
        contexto
    )


def artigo(request):
    return render(
        request,
        'motorartigos/artigo.html'
    )


def detalhe_comercio(request, id):
    comercio = get_object_or_404(
        Comercio.objects.select_related(
            'id_fk_eixo',
            'id_fk_responsavel'
        ),
        id=id,
        publicada=True
    )

    return render(
        request,
        'motorartigos/banca.html',
        {'artigo': comercio}
    )


def mostrar_dashboard(request):
    return render(
        request,
        'motorartigos/dashboard.html'
    )


def criar_grafico_pizza():
    pass
