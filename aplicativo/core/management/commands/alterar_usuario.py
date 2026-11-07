"""Troca senha, nome ou desativa uma conta, com perguntas em português."""
import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

from .criar_usuario import listar_contas


def sim(pergunta):
    return input(pergunta + ' [s/N] ').strip().lower() in ('s', 'sim')


class Command(BaseCommand):
    help = 'Troca a senha, o nome ou desativa uma conta de acesso.'

    def add_arguments(self, parser):
        parser.add_argument('--usuario')
        parser.add_argument('--nome')
        parser.add_argument('--senha')
        parser.add_argument('--desativar', action='store_true')
        parser.add_argument('--reativar', action='store_true')

    def handle(self, *args, **opts):
        translation.activate('pt-br')
        User = get_user_model()
        out = self.stdout.write
        automatico = any(opts[k] for k in ('nome', 'senha')) or opts['desativar'] or opts['reativar']
        listar_contas(out)
        usuario = opts['usuario'] or input('\nQual usuário deseja alterar? ').strip()
        try:
            u = User.objects.get(username__iexact=usuario)
        except User.DoesNotExist:
            raise CommandError(f'Usuário "{usuario}" não encontrado.')
        # Nome
        nome = opts['nome']
        if nome is None and not automatico:
            nome = input(f'Nome completo [Enter mantém "{u.get_full_name() or "sem nome"}"]: ').strip()
        if nome:
            partes = nome.split(); u.first_name, u.last_name = partes[0], ' '.join(partes[1:])
            out(f'Nome atualizado: {u.get_full_name()}')
        # Senha
        senha = opts['senha']
        if senha is None and not automatico and sim('Trocar a senha desta conta?'):
            for _ in range(5):
                out('A senha não aparece enquanto você digita. Use 10 caracteres ou mais.')
                a = getpass.getpass('Nova senha: '); b = getpass.getpass('Repita a nova senha: ')
                if a != b:
                    out('As duas senhas não são iguais.'); continue
                try:
                    validate_password(a, u)
                except ValidationError as e:
                    out('Senha recusada: ' + ' '.join(e.messages)); continue
                senha = a; break
        if senha:
            try:
                validate_password(senha, u)
            except ValidationError as e:
                raise CommandError(' '.join(e.messages))
            u.set_password(senha); out('Senha trocada.')
        # Ativação
        desativar = opts['desativar'] or (not automatico and u.is_active and sim('Desativar esta conta (ela deixa de entrar no app)?'))
        if desativar:
            outros = User.objects.filter(is_active=True, is_superuser=True).exclude(pk=u.pk).exists()
            if not outros:
                raise CommandError('Não é possível desativar a única conta administradora ativa. Crie outra antes (03_CRIAR_USUARIO.bat).')
            u.is_active = False; out('Conta desativada. O histórico registrado por ela continua no app.')
        elif opts['reativar'] or (not automatico and not u.is_active and sim('Reativar esta conta?')):
            u.is_active = True; out('Conta reativada.')
        u.save()
        out(self.style.SUCCESS('Alterações salvas.'))
