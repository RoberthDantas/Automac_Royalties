"""0.6.0: exclusão de registros com confirmação e registro, e tela de usuários.

Toda exclusão mostra antes o que vai junto (histórico, anexos, lançamentos) e grava uma cópia em JSON em
dados/logs/exclusoes.jsonl, para que um registro apagado por engano possa ser recuperado pelo administrador.
"""
import json
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core import serializers
from django.db import router, transaction
from django.db.models import ProtectedError
from django.db.models.deletion import Collector
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import EDITORS
from .models import Attachment, InternalPlan

DELETABLE = {key: (model, label) for key, (model, _form, label) in EDITORS.items()}
DELETABLE['planejamento'] = (InternalPlan, 'Ação interna')
DELETABLE['documento'] = (Attachment, 'Documento')

AFTER_DELETE = {'planejamento': '/planejamento/'}


class _FullCollector(Collector):
    # Sem atalho de exclusão rápida: assim a lista mostra (e o registro guarda) também histórico e anexos ligados.
    def can_fast_delete(self, *args, **kwargs):
        return False


MODEL_LABELS = {'Opportunity': 'Oportunidade', 'Activity': 'Histórico', 'Attachment': 'Documentos anexados',
                'CashEntry': 'Lançamentos financeiros', 'Contact': 'Contatos', 'Organization': 'Organização',
                'DirectorPlan': 'Plano diretor', 'WatchedPage': 'Página monitorada', 'InternalPlan': 'Ação interna',
                'InternalPlanLog': 'Histórico da ação', 'Signal': 'Sinais'}


def _describe(obj):
    name = type(obj).__name__
    if name == 'Activity':
        return f"{obj.get_kind_display()} · {timezone.localtime(obj.created_at):%d/%m/%Y} · {obj.text[:60]}"
    if name == 'InternalPlanLog':
        return f"Alteração de {timezone.localtime(obj.created_at):%d/%m/%Y}"
    if name == 'DirectorPlan':
        return f'{obj.municipality} — {obj.law}'
    for attr in ('title', 'description', 'name'):
        value = getattr(obj, attr, None)
        if value:
            return str(value)
    return str(obj)


def _collect(obj):
    collector = _FullCollector(using=router.db_for_write(type(obj)))
    collector.collect([obj])
    groups = []
    for model, instances in collector.data.items():
        instances = list(instances)
        if not instances:
            continue
        groups.append({'label': MODEL_LABELS.get(model.__name__, str(model._meta.verbose_name_plural).capitalize()),
                       'count': len(instances), 'items': [_describe(i)[:120] for i in instances[:5]], 'model': model, 'objects': instances})
    return groups


def _log_deletion(user, entity, obj, groups):
    log_dir = settings.DATA_DIR / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    everything = [o for g in groups for o in g['objects']]
    entry = {'quando': datetime.now().isoformat(timespec='seconds'), 'usuario': user.get_username(),
             'tipo': entity, 'registro': str(obj), 'dados': json.loads(serializers.serialize('json', everything))}
    with (log_dir / 'exclusoes.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


@login_required
def delete_record(request, entity, pk):
    if entity not in DELETABLE:
        raise Http404
    model, label = DELETABLE[entity]
    obj = get_object_or_404(model, pk=pk)
    back = request.GET.get('voltar') or request.POST.get('voltar') or ''
    if not back.startswith('/') or back.startswith('//'):
        back = f'/oportunidade/{obj.opportunity_id}/' if entity == 'documento' else f'/{entity}/'
    try:
        groups = _collect(obj)
        blocked = None
    except ProtectedError as exc:
        groups = []
        blocked = sorted({f'{MODEL_LABELS.get(type(o).__name__, type(o).__name__)}: {_describe(o)}' for o in exc.protected_objects})[:10]
    if request.method == 'POST' and not blocked:
        if request.POST.get('confirmar') != 'sim':
            messages.error(request, 'Marque a confirmação para excluir.')
        else:
            files = [a.file for g in groups if g['model'] is Attachment for a in g['objects'] if a.file]
            name = _describe(obj)
            with transaction.atomic():
                _log_deletion(request.user, entity, obj, groups)
                obj.delete()
            for f in files:
                try:
                    f.storage.delete(f.name)
                except OSError:
                    pass
            messages.success(request, f'{label} excluído(a): {name}. Uma cópia ficou em dados\\logs\\exclusoes.jsonl.')
            # A ficha do próprio registro deixa de existir; volta para a lista.
            target = '/oportunidades/' if entity == 'oportunidades' else (AFTER_DELETE.get(entity) or back)
            return redirect(target)
    return render(request, 'core/delete_confirm.html', {
        'title': f'Excluir {label.lower()}', 'obj': _describe(obj), 'label': label, 'groups': groups,
        'blocked': blocked, 'back': back})


# ---------------------------------------------------------------- usuários

User = get_user_model()


class UserCreateForm(forms.Form):
    full_name = forms.CharField(label='Nome completo', max_length=150, help_text='Vai na assinatura das mensagens de abordagem.')
    username = forms.SlugField(label='Usuário para entrar', max_length=150)
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput, help_text='10 caracteres ou mais.')
    password2 = forms.CharField(label='Repita a senha', widget=forms.PasswordInput)

    def clean_username(self):
        value = self.cleaned_data['username'].lower()
        if User.objects.filter(username__iexact=value).exists():
            raise forms.ValidationError('Já existe uma conta com este usuário.')
        return value

    def clean(self):
        data = super().clean()
        if data.get('password1') and data.get('password1') != data.get('password2'):
            self.add_error('password2', 'As senhas não conferem.')
        elif data.get('password1'):
            try:
                validate_password(data['password1'], User(username=data.get('username', ''), first_name=data.get('full_name', '')))
            except forms.ValidationError as exc:
                self.add_error('password1', exc)
        return data


class UserEditForm(forms.Form):
    full_name = forms.CharField(label='Nome completo', max_length=150)
    is_active = forms.BooleanField(label='Conta ativa (pode entrar no app)', required=False)
    password1 = forms.CharField(label='Nova senha', widget=forms.PasswordInput, required=False, help_text='Deixe em branco para manter a senha atual.')
    password2 = forms.CharField(label='Repita a nova senha', widget=forms.PasswordInput, required=False)

    def __init__(self, *args, user=None, editing_self=False, **kwargs):
        self.user, self.editing_self = user, editing_self
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        if data.get('password1') or data.get('password2'):
            if data.get('password1') != data.get('password2'):
                self.add_error('password2', 'As senhas não conferem.')
            else:
                try:
                    validate_password(data['password1'], self.user)
                except forms.ValidationError as exc:
                    self.add_error('password1', exc)
        if not data.get('is_active'):
            if self.editing_self:
                self.add_error('is_active', 'Você não pode desativar a própria conta.')
            elif not User.objects.filter(is_active=True).exclude(pk=self.user.pk).exists():
                self.add_error('is_active', 'Precisa ficar pelo menos uma conta ativa.')
        return data


def _split(name):
    parts = name.strip().split(' ', 1)
    return parts[0], (parts[1] if len(parts) > 1 else '')


@login_required
def users(request):
    rows = User.objects.order_by('-is_active', 'first_name', 'username')
    return render(request, 'core/users.html', {'title': 'Usuários', 'rows': rows})


@login_required
def user_new(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        first, last = _split(form.cleaned_data['full_name'])
        # Como no 03_CRIAR_USUARIO.bat: o app não tem perfis, toda conta tem acesso completo.
        User.objects.create_superuser(username=form.cleaned_data['username'], email='', password=form.cleaned_data['password1'],
                                      first_name=first, last_name=last)
        messages.success(request, f'Conta "{form.cleaned_data["username"]}" criada.')
        return redirect('users')
    return render(request, 'core/form.html', {'title': 'Nova conta', 'form': form, 'back': '/usuarios/',
                  'intro': 'Toda conta tem acesso completo ao app. Crie uma conta por pessoa; não compartilhe senhas.'})


@login_required
def user_edit(request, pk):
    u = get_object_or_404(User, pk=pk)
    editing_self = u.pk == request.user.pk
    initial = {'full_name': u.get_full_name(), 'is_active': u.is_active}
    form = UserEditForm(request.POST or None, initial=initial, user=u, editing_self=editing_self)
    if request.method == 'POST' and form.is_valid():
        u.first_name, u.last_name = _split(form.cleaned_data['full_name'])
        u.is_active = form.cleaned_data['is_active']
        if form.cleaned_data.get('password1'):
            u.set_password(form.cleaned_data['password1'])
        u.save()
        if editing_self and form.cleaned_data.get('password1'):
            update_session_auth_hash(request, u)
        messages.success(request, f'Conta "{u.username}" atualizada.')
        return redirect('users')
    return render(request, 'core/form.html', {'title': f'Conta: {u.username}', 'form': form, 'back': '/usuarios/',
                  'intro': 'Para tirar o acesso de alguém, desmarque "Conta ativa". O histórico assinado por ela continua no app.'})
