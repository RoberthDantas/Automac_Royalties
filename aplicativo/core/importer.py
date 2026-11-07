"""0.5.1 — importação de arquivos oficiais colocados em dados/importar (royalties ANP .xlsx e produção por poço do CDP .csv).

Cada arquivo é importado uma única vez (identificado pelo SHA-256). O original fica preservado em dados/fontes/<coleta>.
Nada é baixado da internet aqui: são arquivos baixados à mão das fontes oficiais.
"""
import hashlib
import re
from collections import defaultdict
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import CollectionJob, Snapshot, Royalty, Municipality, WellProduction

ANP_FILE_URL = 'https://www.gov.br/anp/pt-br/assuntos/royalties-e-outras-participacoes/royalties'


def import_royalty_file(raw, filename, year):
    from .collectors import parse_anp_xlsx, normalize
    job = CollectionJob.objects.create(source='anp', status='running', parameters={'year': year, 'arquivo': filename, 'origem': 'pasta importar'})
    digest = hashlib.sha256(raw).hexdigest()
    folder = settings.DATA_DIR / 'fontes' / str(job.pk); folder.mkdir(parents=True, exist_ok=True)
    stored = digest + '.http-body'; (folder / stored).write_bytes(raw)
    snap = Snapshot.objects.create(job=job, url=ANP_FILE_URL, filename=stored, sha256=digest, size=len(raw), provenance={
        'requested_url': ANP_FILE_URL, 'received_body_file': stored, 'received_body_sha256': digest, 'received_body_size': len(raw),
        'origem': f'Arquivo {filename} baixado da ANP e importado da pasta dados/importar', 'collector_version': settings.VERSION})
    try:
        mapping = {(m.uf, normalize(m.name)): m.pk for m in Municipality.objects.all()}
        audit = []
        records, months, unmatched = parse_anp_xlsx(raw, year, mapping, alias_audit=audit)
        added = changed = 0
        with transaction.atomic():
            for r in records:
                key = {k: r[k] for k in ('municipality_id', 'year', 'month')}
                _, created = Royalty.objects.update_or_create(**key, defaults={'minimum': r['minimum'], 'excess': r['excess'], 'total': r['total'], 'source_url': ANP_FILE_URL, 'snapshot': snap})
                added += created; changed += not created
        job.status = 'partial' if unmatched else 'ok'
        job.summary = f'{year} (arquivo {filename}): {len(records)} valores mensais; {added} novos e {changed} atualizados. Meses publicados: {", ".join(map(str, months))}. {len(unmatched)} nomes não conciliados.'
    except Exception as exc:
        job.status = 'error'; job.summary = f'{exc} Arquivo original preservado; valores anteriores mantidos.'
    finally:
        job.finished_at = timezone.now(); job.save()
    return job


def import_folder():
    from .wells import import_production
    folder = settings.DATA_DIR / 'importar'
    folder.mkdir(parents=True, exist_ok=True)
    done = set(Snapshot.objects.values_list('sha256', flat=True))
    results = []
    for f in sorted(folder.iterdir(), key=lambda p: p.name):
        if not f.is_file():
            continue
        raw = f.read_bytes(); digest = hashlib.sha256(raw).hexdigest()
        if digest in done:
            continue
        name = f.name.lower()
        if name.endswith('.csv') and 'producao' in name:
            env = 'Mar' if '_mar' in name else 'Terra' if '_terra' in name else None
            if not env:
                results.append(f'{f.name}: informe _Mar ou _Terra no nome do arquivo'); continue
            job = import_production(raw, f.name, env)
        elif name.endswith('.xlsx') and 'royalties' in name:
            m = re.search(r'(20\d\d)', name)
            if not m:
                results.append(f'{f.name}: ano não encontrado no nome'); continue
            job = import_royalty_file(raw, f.name, int(m.group(1)))
        else:
            continue
        done.add(digest)
        results.append(f'{f.name}: {job.get_status_display()}')
    return results


# ---------- Análises usadas nas telas ----------

def royalty_ytd(codes):
    """Excedentes do ano mais recente (meses publicados) contra os mesmos meses do ano anterior, por município."""
    years = sorted(set(Royalty.objects.values_list('year', flat=True)))
    if len(years) < 2:
        return None, {}
    last = years[-1]
    months = sorted(set(Royalty.objects.filter(year=last).values_list('month', flat=True)))
    out = defaultdict(lambda: {'cur': 0, 'prev': 0})
    for r in Royalty.objects.filter(municipality_id__in=codes, year__in=[last, last - 1], month__in=months).values('municipality_id', 'year', 'excess'):
        out[r['municipality_id']]['cur' if r['year'] == last else 'prev'] += r['excess']
    for v in out.values():
        v['pct'] = (float(v['cur']) / float(v['prev']) - 1) * 100 if v['prev'] else None
    abbr = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
    label = f'{last} ({abbr[months[0] - 1]}–{abbr[months[-1] - 1]}) vs {last - 1}'
    return label, dict(out)


def offshore_production():
    """Produção marítima importada, por campo: último mês e primeiro mês do mesmo ano."""
    rows = defaultdict(lambda: defaultdict(lambda: {'wells': 0, 'oil': 0.0, 'gas': 0.0}))
    meta = {}
    for p in WellProduction.objects.filter(environment='Mar').only('uf', 'period', 'petroleum', 'gas', 'raw'):
        field = (p.raw or {}).get('Campo') or '—'
        key = (p.uf, field)
        meta[key] = (p.raw or {}).get('Operador', '')
        cell = rows[key][p.period]
        cell['wells'] += 1; cell['oil'] += float(p.petroleum or 0); cell['gas'] += float(p.gas or 0)
    table = []
    for key, periods in rows.items():
        last = max(periods); first = min(x for x in periods if x.year == last.year)
        a, b = periods[first], periods[last]
        table.append({'uf': key[0], 'field': key[1], 'operator': meta[key], 'last': last, 'first': first, 'wells': b['wells'],
                      'oil': b['oil'], 'gas': b['gas'], 'oil_first': a['oil'], 'gas_first': a['gas'],
                      'oil_pct': (b['oil'] / a['oil'] - 1) * 100 if a['oil'] else None})
    latest = max((r['last'] for r in table), default=None)
    for r in table:
        r['stale'] = latest and r['last'] < latest
    return sorted(table, key=lambda r: -r['oil'])
