import io
import base64
import html
import numpy as np
import matplotlib.pyplot as plt

ACCENT = '#3B8F7B'
ACCENT_DARK = '#286F60'
ACCENT_PALE = '#EFF8F5'
PAGE = '#F2F7F5'
BORDER = '#DDEBE6'
TEXT = '#1F2B27'
MUTED = '#75817B'
GOOD = '#2E8B57'
WARN = '#B7791F'
BAD = '#B24D3B'
BAD_PALE = '#FFF0EC'
WARN_PALE = '#FFF7E7'
GOOD_PALE = '#EEF8F2'


def pct(x):
    return f'{x*100:.1f}%'


def num(x):
    return f'{x:,.0f}'


def delta(cur, prev, pp=False):
    if pp:
        return f"{(cur-prev)*100:+.1f}pp"
    return 'n/a' if prev == 0 else f"{(cur/prev-1)*100:+.1f}%"


def _delta_color(value):
    if value.startswith('+'):
        return GOOD
    if value.startswith('-'):
        return BAD
    return MUTED


def _fig_b64(fig):
    b = io.BytesIO()
    fig.savefig(b, format='png', dpi=170, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return base64.b64encode(b.getvalue()).decode()


def make_funnel(a):
    k = a['kpis']
    labels = ['Walk-ins', 'Relevant', 'Interacted', 'Buyers']
    vals = [k['walkins'], k['relevant'], k['interactions'], k['buyers']]
    convs = [
        1,
        k['relevant_rate'],
        k['interaction_rate'],
        k['conversion'],
    ]
    fig, ax = plt.subplots(figsize=(8.4, 2.45))
    y = np.arange(len(labels))
    bars = ax.barh(y, vals, color=ACCENT, alpha=.92, height=.55)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_title('Shopper funnel', loc='left', fontsize=11, fontweight='bold', color=TEXT, pad=10)
    ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    ax.tick_params(axis='x', labelsize=8, colors=MUTED, length=0)
    ax.tick_params(axis='y', labelsize=9, colors=TEXT, length=0)
    ax.grid(axis='x', alpha=.12)
    maxv = max(vals) if vals else 1
    for i, (bar, v) in enumerate(zip(bars, vals)):
        stage = '' if i == 0 else f'  ·  {convs[i]*100:.1f}%'
        ax.text(v + maxv*.012, bar.get_y()+bar.get_height()/2,
                f'{v:,.0f}{stage}', va='center', fontsize=8.5, color=TEXT)
    ax.set_xlim(0, maxv*1.25)
    fig.tight_layout()
    return _fig_b64(fig)


def make_matrix(a):
    d = a['outlets']
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    sizes = np.clip(d.offtake * 3, 35, 380)
    ax.scatter(d.relevant_per_manday, d.conversion * 100, s=sizes,
               alpha=.62, color=ACCENT, edgecolors='white', linewidths=.6)
    xm = d.relevant_per_manday.median()
    ym = d.conversion.median() * 100
    ax.axvline(xm, ls='--', lw=1, color='#9BAAA5')
    ax.axhline(ym, ls='--', lw=1, color='#9BAAA5')
    ax.set_xlabel('Relevant shoppers / manday', fontsize=9, color=MUTED)
    ax.set_ylabel('Conversion %', fontsize=9, color=MUTED)
    ax.set_title('Opportunity matrix', loc='left', fontsize=11, fontweight='bold', color=TEXT, pad=10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#D8E3DF')
    ax.tick_params(labelsize=8, colors=MUTED)
    ax.grid(alpha=.10)
    ax.text(.98, .97, 'SCALE', transform=ax.transAxes, ha='right', va='top', fontsize=8.5,
            color=ACCENT_DARK, fontweight='bold')
    ax.text(.02, .97, 'SMALL / EFFICIENT', transform=ax.transAxes, ha='left', va='top', fontsize=8.5,
            color=MUTED, fontweight='bold')
    ax.text(.98, .03, 'CONVERT', transform=ax.transAxes, ha='right', va='bottom', fontsize=8.5,
            color=BAD, fontweight='bold')
    ax.text(.02, .03, 'REASSESS', transform=ax.transAxes, ha='left', va='bottom', fontsize=8.5,
            color=BAD, fontweight='bold')
    fig.tight_layout()
    return _fig_b64(fig)


def _badge(text, kind='neutral'):
    palette = {
        'good': (GOOD_PALE, GOOD),
        'warn': (WARN_PALE, WARN),
        'bad': (BAD_PALE, BAD),
        'neutral': (ACCENT_PALE, ACCENT_DARK),
    }
    bg, fg = palette[kind]
    return (f'<span style="display:inline-block;background:{bg};color:{fg};'
            f'padding:4px 7px;border-radius:999px;font-size:10px;font-weight:700;">'
            f'{html.escape(str(text))}</span>')


def _section(title, subtitle, inner_html):
    return f'''
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
      style="background:#FFFFFF;border:1px solid {BORDER};border-radius:16px;box-shadow:0 6px 20px rgba(25,78,66,0.08);margin-bottom:14px;">
      <tr><td style="padding:16px 18px 8px 18px;">
        <div style="font-size:17px;line-height:22px;font-weight:700;color:{TEXT};">{title}</div>
        <div style="font-size:11px;line-height:16px;color:{MUTED};margin-top:3px;">{subtitle}</div>
      </td></tr>
      <tr><td style="padding:6px 10px 14px 10px;">{inner_html}</td></tr>
    </table>'''


def _table(df, columns, empty='No material exceptions in this period.'):
    if df is None or len(df) == 0:
        return f'<div style="padding:14px;color:{MUTED};font-size:12px;">{html.escape(empty)}</div>'
    th = (f'padding:10px 11px;text-align:left;font-size:10px;color:#68736E;'
          f'text-transform:uppercase;letter-spacing:.35px;background:{PAGE};'
          f'border-bottom:1px solid {BORDER};')
    td = (f'padding:11px;font-size:12px;color:#2E3833;border-bottom:1px solid {BORDER};'
          f'vertical-align:top;line-height:17px;')
    out = ['<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:separate;border-spacing:0;">', '<tr>']
    for label, _ in columns:
        out.append(f'<th style="{th}">{html.escape(label)}</th>')
    out.append('</tr>')
    for _, r in df.iterrows():
        out.append('<tr>')
        for _, fn in columns:
            out.append(f'<td style="{td}">{fn(r)}</td>')
        out.append('</tr>')
    out.append('</table>')
    return ''.join(out)


def render(a, cadence):
    k = a['kpis']
    p = a['prev_kpis']
    funnel = make_funnel(a)
    matrix = make_matrix(a)

    # Headline KPI cards
    cards = []
    kpi_defs = [
        ('Conversion', pct(k['conversion']), delta(k['conversion'], p.get('conversion', 0), True)),
        ('Relevant Shoppers', num(k['relevant']), delta(k['relevant'], p.get('relevant', 0))),
        ('Availability', pct(k['availability']), delta(k['availability'], p.get('availability', 0), True)),
        ('Offtake / Manday', f"{k['offtake_per_manday']:.1f}", delta(k['offtake_per_manday'], p.get('offtake_per_manday', 0))),
    ]
    for label, value, d in kpi_defs:
        cards.append(f'''
        <td width="25%" valign="top" style="padding:5px;">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
            style="background:#FFFFFF;border:1px solid {BORDER};border-radius:14px;box-shadow:0 6px 18px rgba(25,78,66,0.07);">
            <tr><td style="padding:16px 15px 14px 15px;">
              <div style="font-size:10px;color:{MUTED};font-weight:700;text-transform:uppercase;letter-spacing:.45px;">{label}</div>
              <div style="font-size:25px;line-height:31px;font-weight:700;color:{TEXT};margin-top:5px;">{value}</div>
              <div style="font-size:11px;color:{_delta_color(d)};font-weight:700;margin-top:4px;">{d}</div>
              <div style="font-size:9px;color:#9AA59F;margin-top:2px;">vs previous period</div>
            </td></tr>
          </table>
        </td>''')
    kpi_html = '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:14px;"><tr>' + ''.join(cards) + '</tr></table>'

    actions = a['actions'].copy()
    if len(actions):
        def evidence(r):
            if r.diagnosis == 'Promoter engagement issue':
                return f'{r.relevant_per_manday:.1f} relevant/manday · interaction {pct(r.interaction_rate)} vs peer {pct(r.peer_inter)}'
            if r.diagnosis == 'Availability constrained':
                return f'Conversion {pct(r.conversion)} · availability {pct(r.availability)}'
            return f'Interaction {pct(r.interaction_rate)} · conversion {pct(r.conversion)} vs peer {pct(r.peer_conv)}'

        def rec(r):
            if r.diagnosis == 'Promoter engagement issue':
                missed = max(0, r.relevant * (r.peer_inter - r.interaction_rate) / max(r.active_days, 1))
                return f'Engage ~{missed:.1f} more relevant shoppers/day.'
            if r.diagnosis == 'Availability constrained':
                return 'Replenish constrained SKUs; use the reorder table below.'
            return 'Review pitch, sampling quality and objection handling.'

        actions['Evidence'] = actions.apply(evidence, axis=1)
        actions['Action'] = actions.apply(rec, axis=1)

    issue_kind = {
        'Promoter engagement issue': 'warn',
        'Availability constrained': 'bad',
        'Conversion quality issue': 'warn',
    }
    action_table = _table(actions, [
        ('Outlet', lambda r: f'<b>{html.escape(str(r["Outlet ID"]))}</b>'),
        ('Issue', lambda r: _badge(r.diagnosis.replace(' issue', ''), issue_kind.get(r.diagnosis, 'neutral'))),
        ('Evidence', lambda r: html.escape(r.Evidence)),
        ('Recommended action', lambda r: f'<b>{html.escape(r.Action)}</b>'),
    ])

    healthy = a['healthy']
    healthy_table = _table(healthy, [
        ('Outlet', lambda r: f'<b>{html.escape(str(r["Outlet ID"]))}</b>'),
        ('Conversion', lambda r: pct(r.conversion)),
        ('Interaction', lambda r: pct(r.interaction_rate)),
        ('Engagement lift', lambda r: f'{r.lift_pp:+.1f}pp' if not np.isnan(r.lift_pp) else 'n/a'),
        ('Likely driver', lambda r: _badge(str(r.signal) if str(r.signal) != 'nan' else 'Mixed', 'good' if 'Promoter' in str(r.signal) else 'neutral')),
    ])

    scale = a['scale']
    scale_table = _table(scale, [
        ('Outlet', lambda r: f'<b>{html.escape(str(r["Outlet ID"]))}</b>'),
        ('Conversion', lambda r: pct(r.conversion)),
        ('Engagement', lambda r: pct(r.interaction_rate)),
        ('Availability', lambda r: pct(r.availability)),
        ('Est. headroom', lambda r: f'<b style="color:{ACCENT_DARK};">+{r.headroom_units:.0f} units/period</b>'),
    ])

    rel = a['relevance']
    def rel_badge(v):
        if v == 'Reassess outlet':
            return _badge(v, 'bad')
        if v == 'Wrong shopper mix':
            return _badge(v, 'warn')
        return _badge(v, 'neutral')
    rel_table = _table(rel, [
        ('Outlet', lambda r: f'<b>{html.escape(str(r["Outlet ID"]))}</b>'),
        ('Relevant %', lambda r: pct(r.relevant_rate)),
        ('Relevant / manday', lambda r: f'{r.relevant_per_manday:.1f}'),
        ('Verdict', lambda r: rel_badge(r.verdict)),
    ])

    stock = a['stock']
    stock_table = _table(stock.head(5), [
        ('Outlet', lambda r: f'<b>{html.escape(str(r["Outlet ID"]))}</b>'),
        ('SKU', lambda r: html.escape(r.SKU)),
        ('Availability', lambda r: pct(r.availability)),
        ('Days cover', lambda r: f'{r.days_cover:.1f}'),
        ('ROP', lambda r: f'{r.reorder_point:.0f}'),
        ('Suggested order', lambda r: f'<b style="color:{BAD if r.recommended_order>0 else MUTED};">{r.recommended_order:.0f}</b>'),
    ])

    # Embedded visual cards
    visuals = f'''
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:14px;">
      <tr>
        <td width="49%" valign="top" style="padding-right:6px;">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#FFFFFF;border:1px solid {BORDER};border-radius:16px;box-shadow:0 6px 20px rgba(25,78,66,0.08);">
            <tr><td style="padding:14px 14px 10px 14px;"><img src="cid:funnel" style="display:block;width:100%;height:auto;border:0;"></td></tr>
          </table>
        </td>
        <td width="2%"></td>
        <td width="49%" valign="top" style="padding-left:6px;">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#FFFFFF;border:1px solid {BORDER};border-radius:16px;box-shadow:0 6px 20px rgba(25,78,66,0.08);">
            <tr><td style="padding:14px 14px 10px 14px;"><img src="cid:matrix" style="display:block;width:100%;height:auto;border:0;"></td></tr>
          </table>
        </td>
      </tr>
    </table>'''

    cadence_title = 'Daily Exception Flash' if cadence == 'daily' else 'Weekly Performance Flash'
    subject = f"Traya Retail Performance Flash | {a['label']}"

    body = f'''<!doctype html>
    <html><body style="margin:0;padding:0;background:{PAGE};font-family:Arial,Helvetica,sans-serif;color:{TEXT};">
    <div style="background:{PAGE};padding:24px 0;">
      <table role="presentation" width="820" align="center" cellspacing="0" cellpadding="0"
        style="width:820px;max-width:96%;margin:auto;">
        <tr><td>

          <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
            style="background:#FFFFFF;border:1px solid {BORDER};border-radius:16px;box-shadow:0 6px 20px rgba(25,78,66,0.08);margin-bottom:14px;">
            <tr>
              <td width="8" style="background:{ACCENT};border-radius:16px 0 0 16px;"></td>
              <td style="padding:18px 20px;">
                <div style="font-size:25px;line-height:31px;color:{TEXT};font-weight:700;">Traya Retail Performance Flash</div>
                <div style="font-size:11px;color:{MUTED};margin-top:4px;">Conversion · Scale-up · Outlet Relevance · Availability</div>
              </td>
              <td width="205" align="right" style="padding:18px 20px;font-size:10px;line-height:15px;color:{MUTED};">
                <b style="color:{ACCENT_DARK};">{cadence_title}</b><br>{a['label']}<br>vs {a['prev_label']}
              </td>
            </tr>
          </table>

          {kpi_html}

          {_section('1 · What requires action?', 'Weak conversion isolated by promoter engagement, conversion quality and availability.', action_table)}

          {_section('1A · Healthy conversion — likely performance driver', 'High-vs-low engagement day comparison helps separate promoter-supported performance from outlet pull. This is a signal, not causal attribution.', healthy_table)}

          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:14px;"><tr>
            <td width="49%" valign="top" style="padding-right:6px;">
              {_section('2 · Where can we sell more?', 'Healthy opportunity + engagement + conversion + availability.', scale_table)}
            </td>
            <td width="2%"></td>
            <td width="49%" valign="top" style="padding-left:6px;">
              {_section('3 · Are we in the right outlets?', 'Persistent relevant-shopper weakness is separated from low overall footfall.', rel_table)}
            </td>
          </tr></table>

          {_section('4 · Availability & replenishment', 'Exceptions only. Reorder point = expected lead-time demand + safety stock; lead time and service factor are configurable.', stock_table)}

          {visuals}

          <div style="font-size:9px;line-height:14px;color:#8B9791;padding:4px 6px 10px 6px;">
            Peer benchmark: City + Channel · Promoter-supported vs outlet-pull is a performance signal, not proof of causality · Email built with table-based HTML and inline CSS for Gmail/Outlook compatibility.
          </div>
        </td></tr>
      </table>
    </div>
    </body></html>'''

    return {
        'subject': subject,
        'html_body': body,
        'images': {'funnel': funnel, 'matrix': matrix},
    }
