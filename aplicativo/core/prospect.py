"""0.5.0 — carga de prospecção pesquisada, lista quente da Paraíba, gerador de mensagens, conferência de contatos,
série histórica de royalties e tarefas de cursos. Nada aqui envia mensagens: o texto é gerado para a pessoa logada revisar e enviar.
"""
import json
from datetime import date, timedelta
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import (Municipality, Organization, Contact, Opportunity, Activity, Signal, DirectorPlan, InternalPlan, Royalty)

SEED_FILE = 'referencias/prospeccao_20260929/prospeccao.json'
SEED_NOTE = 'Pesquisa pública de 29/09/2026 (site oficial ou dados abertos). Não conferido por telefone: confirme antes de usar e marque como conferido.'
PB_DUE = {1: date(2026, 10, 9), 2: date(2026, 10, 16), 3: date(2026, 10, 23)}

COURSE_TASKS = [
    ('curso:gnss', 'Curso GNSS e georreferenciamento (Altus APS-3) — primeira turma',
     'Fechar ementa, carga horária (sugestão: 16 h presenciais), instrutor e preço da primeira turma',
     'Preço e instrutor dependem de decisão do Dr. Gilberto. Público: topógrafos, técnicos de prefeitura, estudantes.'),
    ('curso:qgis-municipal', 'Curso QGIS para gestão municipal (online) — primeira turma',
     'Montar ementa (sugestão: 20 h, 5 encontros), formato de turma fechada para prefeitura e preço',
     'Porta de entrada para REURB, cadastro e plano diretor. Prefeitura pode contratar turma fechada por dispensa.'),
]


def _municipality(uf, name):
    return Municipality.objects.filter(uf=uf, name=name).first()


def _prefeitura(mun):
    org, _ = Organization.objects.get_or_create(name=f'Prefeitura Municipal de {mun.name}/{mun.uf}', kind='prefeitura', defaults={
        'role': 'comprador', 'municipality': mun, 'notes': 'Criada pela carga de prospecção 0.5.0.'})
    return org


def seed_prospect():
    """Idempotente: cria o que falta e nunca sobrescreve campos editados no app."""
    path = settings.BASE_DIR / SEED_FILE
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    out = {'contatos': 0, 'planos': 0, 'sinais': 0, 'oportunidades': 0, 'cursos': 0}
    with transaction.atomic():
        for c in data.get('contatos', []):
            mun = _municipality(c['uf'], c['municipio'])
            if not mun:
                continue
            org = _prefeitura(mun)
            _, created = Contact.objects.get_or_create(organization=org, name=c['nome'], email=c['email'], phone=c['telefone'], defaults={
                'position': c['cargo'] + (' — ' + c['orgao'] if c['orgao'] and c['orgao'] not in c['cargo'] else ''),
                'source_url': c['fonte'], 'notes': SEED_NOTE})
            out['contatos'] += created
        for p in data.get('planos_diretores', []):
            mun = _municipality(p['uf'], p['municipio'])
            if not mun or DirectorPlan.objects.filter(municipality=mun).exists():
                continue
            DirectorPlan.objects.create(municipality=mun, law=p['lei'][:240], base_date=date.fromisoformat(p['data_base']),
                                        source_url=p['fonte'], confirmed=p['confirmado'],
                                        checked_on=date(2026, 9, 29) if p['confirmado'] else None, notes=p['notas'])
            out['planos'] += 1
        signals = {}
        for s in data.get('sinais', []):
            mun = _municipality('PB', s['municipio'])
            obj, created = Signal.objects.get_or_create(external_key='pesquisa:' + s['chave'], defaults={
                'title': s['titulo'][:500], 'kind': s['tipo'], 'municipality': mun, 'source_url': s['fonte'],
                'reason': s['motivo'], 'publication_date': date.fromisoformat(s['data']), 'source_type': 'pesquisa',
                'relevance': 70, 'payload': {'origem': 'Pesquisa assistida 29/09/2026', 'temas': ['planos']}})
            signals[s['municipio']] = obj
            out['sinais'] += created
        for o in data.get('oportunidades_pb', []):
            if Opportunity.objects.filter(title=o['titulo']).exists():
                continue
            mun = _municipality('PB', o['municipio'])
            if not mun:
                continue
            if o['frente'] == 'apoio':
                org, _ = Organization.objects.get_or_create(name='Construtoras e incorporadoras de João Pessoa (via Sinduscon-JP)', kind='outro', defaults={
                    'role': 'comprador', 'municipality': mun, 'notes': 'Setor afetado pela anulação da LUOS (TJPB, 10/12/2025). Identificar empresas e interlocutor no Sinduscon-JP.'})
            else:
                org = _prefeitura(mun)
            sig = signals.get(o['municipio'])
            if sig and (sig.status == 'convertido' or Opportunity.objects.filter(signal=sig).exists()):
                sig = None
            opp = Opportunity.objects.create(title=o['titulo'], organization=org, front=o['frente'], stage='identificada',
                priority=o['prioridade'], priority_reason='Lista quente Paraíba (pesquisa de 29/09/2026).', problem=o['problema'],
                scope=o['escopo'], decision_maker=o['decisor'], next_action=o['acao'], next_date=PB_DUE[o['prioridade']],
                blockers='Interlocutor e andamento atual a confirmar.', signal=sig)
            if sig:
                sig.status = 'convertido'; sig.save(update_fields=['status'])
            Activity.objects.create(opportunity=opp, kind='sistema', author='sistema', text='Oportunidade carregada da pesquisa de 29/09/2026. Prazo proposto, editável.')
            out['oportunidades'] += 1
        # Onde a pesquisa já trouxe contatos, a próxima ação padrão (ainda não editada) passa a ser conferir e enviar.
        default_action = 'Identificar procurador-geral e secretário de Fazenda; conferir telefone e e-mail oficiais'
        for opp in Opportunity.objects.filter(front='royalties', next_action=default_action, organization__contacts__isnull=False).distinct():
            opp.next_action = 'Conferir por telefone os contatos pesquisados e enviar a primeira mensagem (botão Gerar mensagem)'
            opp.save(update_fields=['next_action', 'updated_at'])
        for key, title, action, blockers in COURSE_TASKS:
            _, created = InternalPlan.objects.get_or_create(seed_key=key, defaults={
                'title': title, 'category': 'operacao', 'status': 'escopo', 'owner': 'A definir', 'next_action': action, 'blockers': blockers})
            out['cursos'] += created
    return out


# ---------- Série histórica de royalties (uma coleta para vários anos) ----------

def collect_anp_series(job):
    from .collectors import collect_anp
    first = int(job.parameters.get('first_year', 2021))
    last = int(job.parameters.get('last_year', timezone.localdate().year))
    lines, failed = [], 0
    for year in range(first, last + 1):
        job.parameters = {**job.parameters, 'year': year}
        job.summary = f'Série ANP: coletando {year} ({year - first + 1} de {last - first + 1}).'
        job.save(update_fields=['parameters', 'summary'])
        try:
            summary, partial = collect_anp(job)
            lines.append(summary.split(' 13 denominações')[0][:300])
            failed += bool(partial)
        except Exception as exc:
            failed += 1
            lines.append(f'{year}: FALHOU — {type(exc).__name__}: {str(exc)[:200]}')
    return 'Série de royalties ' + f'{first}–{last}. ' + ' | '.join(lines), bool(failed)


# ---------- Lista quente Paraíba ----------

@login_required
def hot_list_pb(request):
    plans = list(DirectorPlan.objects.filter(municipality__uf='PB').select_related('municipality').order_by('base_date'))
    opps = (Opportunity.objects.filter(organization__municipality__uf='PB').exclude(front='royalties')
            .exclude(stage__in=['perdida', 'concluida', 'suspensa']).select_related('organization__municipality', 'signal')
            .order_by('priority', 'next_date'))
    signals = Signal.objects.filter(municipality__uf='PB', kind__in=['plano', 'outro', 'fundiaria', 'cadastral']).exclude(status='descartado').select_related('municipality').order_by('-publication_date')[:20]
    today = timezone.localdate()
    for p in plans:
        p.age = (today - p.base_date).days // 365
    return render(request, 'core/hot_list_pb.html', {'title': 'Lista quente — Paraíba', 'plans': plans, 'opps': opps, 'signals': signals, 'today': today})


# ---------- Contatos: conferência ----------

@login_required
@require_POST
def verify_contact(request, pk):
    c = get_object_or_404(Contact, pk=pk)
    c.verified_on = timezone.localdate()
    note = request.POST.get('note', '').strip()
    if note:
        c.notes = (c.notes + '\n' if c.notes else '') + f'{c.verified_on:%d/%m/%Y}: {note}'
    c.save(update_fields=['verified_on', 'notes'])
    messages.success(request, f'Contato conferido em {c.verified_on:%d/%m/%Y}. Agora conta como contato qualificado.')
    # 0.5.3: só volta para endereços do próprio app (evita redirecionamento para site externo).
    from django.utils.http import url_has_allowed_host_and_scheme
    target = request.POST.get('next') or ''
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=False):
        target = '/contatos/'
    return redirect(target)


# ---------- Gerador de mensagens ----------

def brl_mi(value):
    mi = Decimal(value) / Decimal(1_000_000)
    return 'R$ ' + f'{mi:,.1f}'.replace(',', 'X').replace('.', ',').replace('X', '.') + (' milhão' if round(mi, 1) < 2 else ' milhões')


def royalty_facts(mun):
    rows = Royalty.objects.filter(municipality=mun, year__gte=2021, year__lte=2025).aggregate(total=Sum('total'), excess=Sum('excess'), minimum=Sum('minimum'))
    if not rows['total']:
        return None
    return {'total': brl_mi(rows['total']), 'excess': brl_mi(rows['excess'] or 0),
            'pct': f"{(rows['excess'] or 0) / rows['total'] * 100:.0f}".replace('.', ','), 'zero': (rows['excess'] or 0) < rows['total'] / 100}


def build_messages(o, user=None):
    from .identity import full_name, PLACEHOLDER
    mun = o.organization.municipality
    name = full_name(user) or PLACEHOLDER
    first = name.split()[0] if name != PLACEHOLDER else PLACEHOLDER
    contacts = list(o.organization.contacts.filter(do_not_contact=False))
    lead = next((c for c in contacts if 'procurador' in (c.position or '').lower()), contacts[0] if contacts else None)
    greeting = f'Prezado(a) {lead.name},' if lead and lead.name and not lead.name.lower().startswith(('atendimento', 'gabinete', 'administra')) else 'Prezados,'
    from django.conf import settings as cfg
    org = cfg.ORG_NAME
    where = f', de {cfg.ORG_PLACE}' if cfg.ORG_PLACE else ''
    extra = ' · '.join(x for x in (cfg.ORG_PLACE, cfg.ORG_SITE) if x)
    sign = f'\n\nAtenciosamente,\n{name}\n{org} | {cfg.ORG_TAGLINE}' + (f'\n{extra}' if extra else '')
    warnings = []
    if name == PLACEHOLDER:
        warnings.append('Sua conta não tem nome completo cadastrado: o texto sai com [seu nome]. '
                        'Feche o app e use 04_ALTERAR_USUARIO.bat, na pasta principal, para cadastrar seu nome.')
    if o.front == 'royalties' and mun:
        f = royalty_facts(mun)
        if not f:
            warnings.append('Sem royalties 2021–2025 carregados para este município: rode a série de royalties antes de enviar.')
            f = {'total': '[valor]', 'excess': '[valor]', 'pct': '[x]', 'zero': False}
        if f['zero']:
            warnings.append('Excedentes abaixo de 1% do total em 2021–2025. Pelo critério do plano, a tese de confrontação é fraca: decida antes de abordar.')
        from .importer import royalty_ytd
        ytd_label, ytd = royalty_ytd([mun.code])
        y = ytd.get(mun.code)
        recent = ''
        if ytd_label and y and y['prev'] and y['pct'] is not None:
            last = max(Royalty.objects.values_list('year', flat=True))
            months = sorted(set(Royalty.objects.filter(year=last).values_list('month', flat=True)))
            names = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            direction = 'acima' if y['pct'] >= 0 else 'abaixo'
            recent = (f' De {names[months[0] - 1]} a {names[months[-1] - 1]} de {last}, a parcela acima de 5% somou {brl_mi(y["cur"])}, '
                      f'{abs(y["pct"]):.0f}% {direction} do mesmo período de {last - 1}.')
        subject = f'Royalties de petróleo de {mun.name}: leitura dos dados públicos da ANP (2021–2025)'
        body = (f'{greeting}\n\nSou {name}, da {org}{where}, e acompanho a distribuição de royalties de petróleo aos municípios.\n\n'
                f'Analisamos os dados públicos da ANP sobre a distribuição de royalties aos municípios do Nordeste. Entre 2021 e 2025, '
                f'{mun.name} recebeu {f["total"]} em royalties; desse total, {f["excess"]} ({f["pct"]}%) vieram da parcela acima de 5%, '
                f'que depende do enquadramento do município em relação à produção marítima.{recent}\n\n'
                f'Esse enquadramento tem base cartográfica e geodésica, e a leitura técnica dos dados ajuda a Procuradoria a decidir se vale aprofundar o caso.\n\n'
                f'Gostaria de apresentar à Procuradoria, em uma conversa de 20 minutos, o panorama dos números de {mun.name}. '
                f'Há disponibilidade na próxima semana?' + sign)
        call = (f'1. Apresentação: "Sou {first}, da {org}{where}. Acompanhamos os royalties de petróleo dos municípios."\n'
                f'2. Motivo: "Analisamos os royalties que {mun.name} recebeu da ANP de 2021 a 2025: {f["total"]}, sendo {f["excess"]} na parcela acima de 5%."\n'
                f'3. Pergunta: "Quem na Procuradoria acompanha os royalties do município?"\n'
                f'4. Pedido: "Posso enviar um resumo por e-mail e marcar 20 minutos para apresentar os números?"\n'
                f'5. Registro: anotar no app como "Contato realizado" (o follow-up de 4 dias é criado sozinho).\n'
                f'Não falar de método, mapas ou traçados. Não prometer receita.')
    else:
        plan = DirectorPlan.objects.filter(municipality=mun).first() if mun else None
        if plan:
            age = (timezone.localdate() - plan.base_date).days // 365
            context = f'O Plano Diretor de {mun.name} ({plan.law.split(" — ")[0]}) tem cerca de {age} anos; o Estatuto da Cidade prevê revisão ao menos a cada dez anos.'
        else:
            context = (o.problem or '').split('\n')[0]
        subject = f'{mun.name if mun else o.organization.name}: base cartográfica e apoio técnico ao planejamento territorial'
        body = (f'{greeting}\n\nSou {name}, da {org}{where}.\n\n{context}\n\n'
                f'Trabalhamos com base cartográfica atualizada e diagnóstico territorial para apoiar o planejamento das prefeituras.\n\n'
                f'Gostaria de apresentar, em uma conversa de 20 minutos, como esse trabalho apoia {("a revisão do plano e " if plan else "")}as decisões da secretaria. '
                f'Há disponibilidade na próxima semana?' + sign)
        call = (f'1. Apresentação: "Sou {first}, da {org}{where}. Trabalhamos com dados territoriais para municípios."\n'
                f'2. Motivo: {context}\n'
                '3. Pergunta: "Quem na prefeitura conduz o planejamento urbano e a base cartográfica?"\n'
                '4. Pedido: "Posso enviar um resumo e marcar 20 minutos?"\n'
                '5. Registro: anotar no app como "Contato realizado".')
    keys = ('procurador', 'tributa', 'finan', 'fazenda') if o.front == 'royalties' else ('planejamento', 'urbanismo', 'meio ambiente', 'procurador')
    chosen = [c for c in contacts if c.email and any(k in (c.position or '').lower() for k in keys)]
    if not chosen:
        chosen = [c for c in contacts if c.email][:2]
    to = ', '.join(dict.fromkeys(c.email for c in chosen[:3]))
    return {'subject': subject, 'body': body, 'call': call, 'to': to, 'warnings': warnings, 'lead': lead}


@login_required
def opportunity_message(request, pk):
    o = get_object_or_404(Opportunity.objects.select_related('organization__municipality'), pk=pk)
    return render(request, 'core/message.html', {'title': 'Mensagem de abordagem — ' + o.title, 'o': o, **build_messages(o, request.user)})


@login_required
@require_POST
def start_royalty_series(request):
    from .collectors import start_job
    try:
        job = start_job('anp_serie', {'first_year': 2021, 'last_year': timezone.localdate().year})
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect('/royalties/')
    return redirect('job_detail', pk=job.pk)
