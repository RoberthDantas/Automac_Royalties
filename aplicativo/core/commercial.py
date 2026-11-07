"""Prospecção comercial (0.4.2): lista quente da Frente 1, metas do trimestre, relatório e cadência de follow-up.

Nada aqui envia mensagens. Os alvos vêm do Plano Comercial de 31/08/2026; números citados são os que constam do plano
(dados ANP processados por Uendry) até que a coleta de royalties do próprio aplicativo os substitua.
"""
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from .models import (Municipality, Organization, Contact, Opportunity, Activity, Signal, Royalty, CollectionJob, Well)

PLAN_SOURCE = 'Plano de Ação Comercial CartoGeo, 31/08/2026 — séries ANP 2021–2025 processadas por Uendry'

# (UF, município, círculo, excedentes 2021–2025 em R$ mi, % excedentes/total, costa em km, observação)
FRENTE1_TARGETS = [
    ('RN', 'Macau', 1, '26,2', '43', '41', ''),
    ('RN', 'Guamaré', 1, '14,9', '56', '12', 'Maior proporção de excedentes entre os litorâneos.'),
    ('RN', 'Areia Branca', 1, '19,1', '24', '40', ''),
    ('RN', 'Porto do Mangue', 1, '', '', '', ''),
    ('RN', 'Galinhos', 1, '', '', '', ''),
    ('RN', 'Grossos', 1, '', '', '', ''),
    ('RN', 'Tibau', 1, '', '', '', ''),
    ('SE', 'Barra dos Coqueiros', 2, '', '', '', ''),
    ('SE', 'Pirambu', 2, '', '', '', ''),
    ('SE', "Itaporanga d'Ajuda", 2, '', '', '', ''),
    ('SE', 'Brejo Grande', 2, '', '', '', ''),
    ('SE', 'Aracaju', 2, '', '', '', ''),
    ('SE', 'General Maynard', 2, '', '', '', 'R$ 104,3 mi de participação especial em 2021–2025, sendo um dos menores municípios do país em área. Entender a anomalia antes de abordar.'),
    ('CE', 'Fortaleza', 3, '4,1', '25', '49', ''),
    ('CE', 'Aquiraz', 3, '3,3', '26', '30', ''),
    ('CE', 'Caucaia', 3, '', '', '', ''),
    ('CE', 'Aracati', 3, '', '', '', ''),
    ('CE', 'Icapuí', 3, '', '', '', ''),
    ('AL', 'Coruripe', 3, '2,4', '15', '39', ''),
    ('AL', 'Marechal Deodoro', 3, '2,1', '3', '14', 'Excedentes baixos (3%): tese de confrontação fraca; manter como observação.'),
]
CIRCLE_LABEL = {1: '1º círculo — RN', 2: '2º círculo — SE', 3: '3º círculo — CE e AL'}
# Prazos propostos para a primeira ação de cada círculo; editáveis em cada oportunidade.
CIRCLE_DUE = {1: date(2026, 10, 2), 2: date(2026, 10, 9), 3: date(2026, 10, 16)}

# Metas do trimestre (seção 9 do Plano Comercial). O primeiro trimestre do plano foi 01/09 a 30/11/2026;
# os seguintes avançam de três em três meses (dez–fev, mar–mai, jun–ago, set–nov).
MONTHS_ABBR = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.']


def add_months(d, n):
    y, m = divmod(d.year * 12 + d.month - 1 + n, 12)
    return date(y, m + 1, 1)


def quarter_bounds(today=None):
    """Trimestre comercial que contém `today`, alinhado ao início do plano (01/09/2026)."""
    today = today or timezone.localdate()
    k = ((today.year - 2026) * 12 + today.month - 9) // 3
    start = add_months(date(2026, 9, 1), 3 * k)
    end = add_months(start, 3) - timedelta(days=1)
    return start, end


def quarter_label(start, end):
    if start.year == end.year:
        return f'{MONTHS_ABBR[start.month - 1]} a {MONTHS_ABBR[end.month - 1]} {end.year}'
    return f'{MONTHS_ABBR[start.month - 1]} {start.year} a {MONTHS_ABBR[end.month - 1]} {end.year}'


QUARTER_START, QUARTER_END = date(2026, 9, 1), date(2026, 11, 30)  # primeiro trimestre do plano (referência)
WEEKLY_APPROACHES = 10
ADVANCED_STAGES = ['proposta', 'negociacao', 'contratada', 'execucao', 'concluida']
SIGNED_STAGES = ['contratada', 'execucao', 'concluida']


def target_title(uf, name):
    return f'Royalties — {name}/{uf}'


def seed_frente1():
    """Cria prefeituras e oportunidades 'Identificada' para os alvos do plano. Idempotente; nunca sobrescreve edições."""
    created = 0
    with transaction.atomic():
        for uf, name, circle, excess, share, coast, note in FRENTE1_TARGETS:
            mun = Municipality.objects.filter(uf=uf, name=name).first()
            if mun is None:
                continue
            org, _ = Organization.objects.get_or_create(name=f'Prefeitura Municipal de {name}/{uf}', kind='prefeitura', defaults={
                'role': 'comprador', 'municipality': mun,
                'notes': 'Alvo da Frente 1 (Plano Comercial 31/08/2026). Procurador-geral, secretário de Fazenda e contato oficial a identificar e conferir.'})
            if Opportunity.objects.filter(front='royalties', title=target_title(uf, name)).exists():
                continue
            facts = []
            if excess:
                facts.append(f'Excedentes 2021–2025: R$ {excess} mi ({share}% do total de royalties recebidos).')
            if coast:
                facts.append(f'Extensão de costa: {coast} km.')
            if note:
                facts.append(note)
            if not facts:
                facts.append('Valores a confirmar pela coleta de royalties do aplicativo (Fontes e coletas → ANP, anos 2021 a 2026).')
            facts.append('Fonte: ' + PLAN_SOURCE + '.')
            action = ('Entender a anomalia de participação especial antes de qualquer abordagem' if name == 'General Maynard'
                      else 'Identificar procurador-geral e secretário de Fazenda; conferir telefone e e-mail oficiais')
            o = Opportunity.objects.create(
                title=target_title(uf, name), organization=org, front='royalties', stage='identificada', route='definir',
                priority=min(circle, 3), priority_reason=CIRCLE_LABEL[circle] + ' do Plano Comercial.',
                problem='\n'.join(facts),
                scope='Peça técnica de delimitação das águas territoriais municipais, com memorial descritivo e base geodésica. '
                      'Abordagem comercial usa apenas dado público da ANP; nenhum mapa indicativo, nenhum detalhe do método.',
                decision_maker='Procurador-Geral do Município; Secretário de Fazenda; prefeito',
                next_action=action, next_date=CIRCLE_DUE[circle],
                blockers='Contatos do comprador ainda não verificados. Rota (direta ou NUPEC) a definir.')
            Activity.objects.create(opportunity=o, kind='sistema', author='sistema',
                                    text='Alvo carregado a partir do Plano Comercial de 31/08/2026 (lista da Frente 1). Prazo proposto, editável.')
            created += 1
    return created


def apply_followup(activity):
    """Cadência D+4 / D+10 ao registrar um contato; proposta avança a etapa. Registra a alteração no histórico."""
    o = activity.opportunity
    today = timezone.localdate()
    changes = []
    if activity.kind == 'contato':
        if o.stage in ('identificada', 'qualificada'):
            o.stage = 'contato'; changes.append('etapa → Contato realizado')
        window_start = timezone.now() - timedelta(days=10)
        first = (o.activities.filter(kind='contato', created_at__gte=window_start).exclude(pk=activity.pk)
                 .order_by('created_at').first())
        if first:
            due = timezone.localtime(first.created_at).date() + timedelta(days=10)
            label = 'D+10'
            if due <= today:
                due = today + timedelta(days=4); label = 'D+4'
        else:
            due, label = today + timedelta(days=4), 'D+4'
        o.next_date = due
        o.next_action = f'Follow-up {label} do contato de {today:%d/%m} (sem resposta: novo contato e registro)'
        changes.append(f'próxima ação em {due:%d/%m} ({label})')
    elif activity.kind == 'proposta' and o.stage not in ADVANCED_STAGES:
        o.stage = 'proposta'; o.next_date = today + timedelta(days=4)
        o.next_action = 'Follow-up D+4 da proposta enviada'
        changes.append('etapa → Proposta enviada'); changes.append(f'próxima ação em {o.next_date:%d/%m}')
    elif activity.kind == 'reuniao' and o.stage in ('identificada', 'qualificada', 'contato'):
        o.stage = 'diagnostico'; changes.append('etapa → Diagnóstico')
    if changes:
        o.save()
        Activity.objects.create(opportunity=o, kind='sistema', author='sistema', text='Cadência automática: ' + '; '.join(changes) + '.')
    return changes


def royalty_summary(codes, years):
    rows = (Royalty.objects.filter(municipality_id__in=codes, year__in=years).values('municipality_id')
            .annotate(excess=Sum('excess'), total=Sum('total'), n=Count('pk')))
    return {r['municipality_id']: r for r in rows}


@login_required
def hot_list(request):
    targets = {(uf, name): (circle, excess, share, coast, note) for uf, name, circle, excess, share, coast, note in FRENTE1_TARGETS}
    opps = list(Opportunity.objects.filter(front='royalties', title__in=[target_title(u, n) for u, n in targets],
                                           organization__municipality__isnull=False)
                .select_related('organization__municipality').annotate(n_contacts=Count('organization__contacts', distinct=True),
                                                                        n_touch=Count('activities', filter=Q(activities__kind='contato'), distinct=True)))
    codes = [o.organization.municipality_id for o in opps if o.organization.municipality_id]
    years = list(Royalty.objects.values_list('year', flat=True).distinct().order_by('year'))
    series_years = [y for y in years if 2021 <= y <= 2025]
    summary = royalty_summary(codes, series_years)
    rows = []
    for o in opps:
        mun = o.organization.municipality
        circle, excess, share, coast, note = targets.get((mun.uf, mun.name), (3, '', '', '', ''))
        live = summary.get(mun.code)
        rows.append({'o': o, 'mun': mun, 'circle': circle, 'circle_label': CIRCLE_LABEL[circle], 'plan_excess': excess,
                     'plan_share': share, 'coast': coast, 'note': note,
                     'live_excess': live['excess'] if live else None,
                     'live_share': (live['excess'] / live['total'] * 100) if live and live['total'] else None})
    rows.sort(key=lambda r: (r['circle'], -(float(r['live_excess'] or 0)), -(float((r['plan_excess'] or '0').replace(',', '.'))), r['mun'].name))
    others = []
    if series_years:
        others = list(Royalty.objects.filter(year__in=series_years, municipality__uf__in=['RN', 'SE', 'CE', 'AL'])
                      .exclude(municipality_id__in=codes).values('municipality_id', 'municipality__name', 'municipality__uf')
                      .annotate(excess=Sum('excess'), total=Sum('total')).filter(excess__gt=0).order_by('-excess')[:25])
        for r in others:
            r['share'] = r['excess'] / r['total'] * 100 if r['total'] else None
    from .importer import royalty_ytd, offshore_production
    ytd_label, ytd = royalty_ytd(codes)
    for r in rows:
        r['ytd'] = ytd.get(r['mun'].code)
    production = offshore_production()
    offshore = (Well.objects.filter(environment='Mar', situation='PRODUZINDO', uf__in=['RN', 'SE', 'CE', 'AL'])
                .values('uf', 'field', 'operator').annotate(n=Count('pk')).order_by('-n'))
    return render(request, 'core/hot_list.html', {'title': 'Lista quente — Frente 1 (royalties)', 'rows': rows, 'others': others,
                  'series_years': series_years, 'offshore': offshore, 'ytd_label': ytd_label, 'production': production, 'plan_source': PLAN_SOURCE, 'today': timezone.localdate(),
                  'stage_counts': {s: sum(1 for r in rows if r['o'].stage == s) for s in ('identificada', 'contato', 'diagnostico', 'proposta')}})


def quarter_metrics(today=None):
    today = today or timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    q_start, q_end = quarter_bounds(today)
    acts = Activity.objects.filter(created_at__date__gte=q_start, created_at__date__lte=q_end)
    proposals = Opportunity.objects.filter(Q(stage__in=ADVANCED_STAGES) | Q(activities__kind='proposta',
                                           activities__created_at__date__gte=q_start)).distinct().count()
    qualified = Contact.objects.filter(verified_on__isnull=False, do_not_contact=False).exclude(organization__kind='cartorio').count()
    triaged = Signal.objects.filter(source_type='pncp', status__in=['descartado', 'convertido']).count()
    scanned = 0
    last_complete = CollectionJob.objects.filter(source='pncp_capacidades', status='ok').first()
    if last_complete:
        scanned = sum(int(v.get('scanned', 0)) for v in (last_complete.parameters.get('progress') or {}).values() if isinstance(v, dict))
    metrics = [
        ('Contratos assinados', Opportunity.objects.filter(stage__in=SIGNED_STAGES).count(), 3, 'Oportunidades em Contratada, Em execução ou Concluída.'),
        ('Propostas enviadas', proposals, 15, 'Oportunidades com proposta registrada ou etapa a partir de Proposta enviada.'),
        ('Contatos qualificados na base', qualified, 120, 'Contatos com data de conferência, exceto cartórios e bloqueados.'),
        ('Reuniões realizadas', acts.filter(kind='reuniao').count(), 20, 'Registros do tipo Reunião no histórico das oportunidades.'),
        ('Editais triados por você', triaged, 200, 'Sinais do PNCP revisados (descartados ou convertidos).'),
    ]
    rows = [{'label': l, 'value': v, 'goal': g, 'help': h, 'pct': min(100, round(v * 100 / g)) if g else 0} for l, v, g, h in metrics]
    week = acts.filter(kind='contato', created_at__date__gte=week_start).count()
    days_total = (q_end - q_start).days + 1
    elapsed = max(0, min(days_total, (today - q_start).days + 1))
    return {'quarter_start': q_start, 'quarter_end': q_end, 'quarter_label': quarter_label(q_start, q_end), 'rows': rows, 'week_approaches': week, 'week_goal': WEEKLY_APPROACHES, 'week_start': week_start,
            'approaches_total': acts.filter(kind='contato').count(), 'scanned_last_cycle': scanned,
            'elapsed_pct': round(elapsed * 100 / days_total), 'today': today,
            'manual': ['Cadastros de fornecedor ativos (meta 3)', 'Processos de inexigibilidade estruturados (meta 1)',
                       'Assinaturas recorrentes ativas (meta 1)']}


@login_required
def goals(request):
    ctx = quarter_metrics()
    month_start = ctx['today'].replace(day=1)
    prev_end = month_start - timedelta(days=1)
    ctx.update(month_start=month_start, prev_start=prev_end.replace(day=1), prev_end=prev_end,
               month_name=MONTH_NAMES[month_start.month - 1], prev_name=MONTH_NAMES[prev_end.month - 1])
    ctx.update(title=f"Metas do trimestre — {ctx['quarter_label']}",
               funnel=list(Opportunity.objects.values('front', 'stage').annotate(n=Count('pk')).order_by('front', 'stage')),
               overdue=Opportunity.objects.exclude(stage__in=['perdida', 'concluida', 'suspensa']).filter(next_date__lt=ctx['today']).select_related('organization')[:20],
               due_week=Opportunity.objects.exclude(stage__in=['perdida', 'concluida', 'suspensa']).filter(next_date__gte=ctx['today'], next_date__lte=ctx['today'] + timedelta(days=7)).select_related('organization').order_by('next_date')[:30])
    from .models import FRONTS, STAGES
    fl, sl = dict(FRONTS), dict(STAGES)
    for f in ctx['funnel']:
        f['front_label'] = fl.get(f['front'], f['front']); f['stage_label'] = sl.get(f['stage'], f['stage'])
    return render(request, 'core/goals.html', ctx)


MONTH_NAMES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']


def parse_day(value, default):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default


@login_required
def activity_report(request):
    """Relatório de prospecção em Markdown para o período (padrão: semana corrente). Base do E5 mensal."""
    from .identity import display_name
    today = timezone.localdate()
    start = parse_day(request.GET.get('de'), today - timedelta(days=today.weekday()))
    end = parse_day(request.GET.get('ate'), today)
    m = quarter_metrics(today)
    acts = (Activity.objects.filter(created_at__date__gte=start, created_at__date__lte=end).exclude(kind='sistema')
            .select_related('opportunity__organization').order_by('created_at'))
    kinds = dict(Activity._meta.get_field('kind').choices)
    active = Opportunity.objects.exclude(stage__in=['perdida', 'concluida', 'suspensa'])
    lines = [f'# Relatório de prospecção — CartoGeo', f'Período: {start:%d/%m/%Y} a {end:%d/%m/%Y} · gerado em {timezone.localtime():%d/%m/%Y %H:%M}',
             f'Gerado por: {display_name(request.user)}', '', f"## Indicadores do trimestre ({m['quarter_start']:%d/%m/%Y} a {m['quarter_end']:%d/%m/%Y})", '',
             '| Indicador | Realizado | Meta |', '|---|---|---|']
    for r in m['rows']:
        lines.append(f"| {r['label']} | {r['value']} | {r['goal']} |")
    lines += [f"| Abordagens nesta semana | {m['week_approaches']} | {m['week_goal']} |", '',
              f"Trimestre decorrido: {m['elapsed_pct']}%. Indicadores de acompanhamento manual: " + '; '.join(m['manual']) + '.', '',
              '## Atividades registradas no período', '']
    if acts:
        for a in acts:
            lines.append(f"- {timezone.localtime(a.created_at):%d/%m} · {kinds.get(a.kind, a.kind)} · {a.opportunity.title} ({a.opportunity.organization.name}): {a.text}")
    else:
        lines.append('- Nenhuma atividade comercial registrada no período.')
    lines += ['', '## Funil ativo por etapa', '']
    for s in active.values('stage').annotate(n=Count('pk')).order_by('stage'):
        lines.append(f"- {dict(Opportunity._meta.get_field('stage').choices).get(s['stage'])}: {s['n']}")
    lines += ['', '## Próximas ações (7 dias)', '']
    for o in active.filter(next_date__lte=end + timedelta(days=7)).select_related('organization').order_by('next_date')[:40]:
        flag = ' — ATRASADA' if o.next_date and o.next_date < today else ''
        lines.append(f"- {o.next_date:%d/%m} · {o.title}: {o.next_action}{flag}")
    new_signals = Signal.objects.filter(collected_at__date__gte=start, collected_at__date__lte=end)
    lines += ['', '## Radar no período', '',
              f"- Sinais novos: {new_signals.count()}; revisados (descartados ou convertidos): {Signal.objects.filter(updated_at__date__gte=start, updated_at__date__lte=end, status__in=['descartado','convertido']).count()}.",
              f"- Último ciclo completo do PNCP: {m['scanned_last_cycle']} licitações abertas examinadas em PB, RN, CE, SE e AL.",
              '', 'Documento interno. Números do funil refletem apenas o que foi registrado no aplicativo.']
    response = HttpResponse('\n'.join(lines), content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="relatorio-prospeccao-{start:%Y%m%d}-{end:%Y%m%d}.md"'
    return response
