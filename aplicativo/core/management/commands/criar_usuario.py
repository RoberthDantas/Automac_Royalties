"""Cria uma conta de acesso com perguntas em português (substitui o createsuperuser do Django)."""
import getpass
import unicodedata

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation


def sugestao_usuario(nome):
    primeiro = (nome.split() or [''])[0].lower()
    return ''.join(c for c in unicodedata.normalize('NFKD', primeiro) if c.isalnum() and ord(c) < 128)


def listar_contas(out):
    User = get_user_model()
    contas = list(User.objects.order_by('username'))
    if contas:
        out('Contas que já existem neste aplicativo:')
        for u in contas:
            nome = u.get_full_name()
            out(f'  - {u.username}' + (f' ({nome})' if nome else '') + ('' if u.is_active else ' [desativada]'))
    return contas


class Command(BaseCommand):
    help = 'Cria uma conta de acesso (administrador) com perguntas em português.'

    def add_arguments(self, parser):
        parser.add_argument('--nome')
        parser.add_argument('--usuario')
        parser.add_argument('--senha', help='Uso em testes. Sem esta opção, a senha é pedida sem aparecer na tela.')
        parser.add_argument('--opcional', action='store_true', help='Pergunta antes se deseja criar (obrigatório se não houver conta).')

    def handle(self, *args, **opts):
        translation.activate('pt-br')
        User = get_user_model()
        out = self.stdout.write
        contas = listar_contas(out)
        ativas = User.objects.filter(is_active=True, is_superuser=True).exists()
        if opts['opcional'] and ativas and opts['senha'] is None:
            resposta = input('\nCriar uma conta de acesso nova agora? [S/n] ').strip().lower()
            if resposta in ('n', 'nao', 'não'):
                out('Nenhuma conta criada.')
                return
        if not ativas:
            out('\nNenhuma conta administradora ativa: crie a sua agora para poder entrar no app.')
        out('\nCRIAR CONTA DE ACESSO')
        nome = opts['nome'] if opts['nome'] is not None else ''
        while not nome.strip():
            nome = input('Nome completo (vai na assinatura das mensagens): ').strip()
        nome = ' '.join(nome.split())
        usuario = opts['usuario'] or ''
        while True:
            if not usuario:
                sugestao = sugestao_usuario(nome)
                usuario = input(f'Nome de usuário para entrar no app [{sugestao}]: ').strip() or sugestao
            if not usuario or ' ' in usuario:
                if opts['usuario']:
                    raise CommandError('Usuário inválido: use uma palavra, sem espaços.')
                out('Use uma palavra, sem espaços.'); usuario = ''; continue
            if User.objects.filter(username__iexact=usuario).exists():
                if opts['usuario']:
                    raise CommandError(f'O usuário "{usuario}" já existe.')
                out(f'O usuário "{usuario}" já existe. Escolha outro.'); usuario = ''; continue
            break
        partes = nome.split()
        candidato = User(username=usuario, first_name=partes[0], last_name=' '.join(partes[1:]))
        for tentativa in range(5):
            if opts['senha'] is not None:
                senha = opts['senha']; repetida = senha
            else:
                out('A senha não aparece enquanto você digita. Use 10 caracteres ou mais.')
                senha = getpass.getpass('Senha: ')
                repetida = getpass.getpass('Repita a senha: ')
            if senha != repetida:
                out('As duas senhas não são iguais. Tente de novo.'); continue
            try:
                validate_password(senha, candidato)
            except ValidationError as e:
                if opts['senha'] is not None:
                    raise CommandError(' '.join(e.messages))
                out('Senha recusada: ' + ' '.join(e.messages)); continue
            break
        else:
            raise CommandError('Muitas tentativas. Rode o comando de novo.')
        User.objects.create_superuser(username=usuario, email='', password=senha,
                                      first_name=candidato.first_name, last_name=candidato.last_name)
        out(self.style.SUCCESS(f'\nConta criada: usuário "{usuario}" ({nome}). Use este usuário e a senha para entrar.'))
