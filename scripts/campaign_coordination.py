"""Experiment coordination contract v1; no model, product or peer dependencies.

Markers are append-only observations. A marker never chooses a new provider/account.
State is local by default. Explicit sharing is data exchange, not a runtime import.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path, PurePosixPath
import re
import uuid

LOCAL_REASONS=frozenset(('cwd','process','parse','output','schema','fixture','auth_home','accounting','unknown_local'))
GLOBAL_REASONS=frozenset(('quota','rate_limit','capacity','auth_account'))
KEYS={'contract_version','scope','provider','account_domain','campaign','reason','evidence','time'}


class CoordinationBlocked(RuntimeError):pass
class ReservationBusy(RuntimeError):pass


def identity(value):
    if not isinstance(value,str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,63}',value):
        raise ValueError('expected opaque non-secret identity, no email/path/token')
    return value


def stamp(value):
    if not isinstance(value,str):raise ValueError('timestamp must be ISO8601 with timezone')
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    if result.tzinfo is None:raise ValueError('timestamp needs timezone')
    return result


def evidence_path(value):
    if (not isinstance(value,str) or not value or value=='.' or ':' in value or '\\' in value or value.startswith('/')
            or '..' in value.split('/') or str(PurePosixPath(value))!=value or any(ord(c)<32 for c in value)):
        raise ValueError('evidence must be a portable relative identifier, never a private path')


def validate_marker(marker):
    if not isinstance(marker,dict) or set(marker)!=KEYS or type(marker.get('contract_version')) is not int or marker['contract_version']!=1:
        raise ValueError('unsupported marker format; expected coordination contract1, do not infer a global scope')
    for key in ('provider','campaign'):identity(marker[key])
    if marker['account_domain'] is not None:identity(marker['account_domain'])
    if marker['reason'] in LOCAL_REASONS:expected='campaign'
    elif marker['reason'] in GLOBAL_REASONS:expected='provider_account'
    else:raise ValueError('unknown fault category')
    if marker['scope']!=expected:raise ValueError('fault category and scope conflict')
    if not isinstance(marker['evidence'],list) or not marker['evidence']:raise ValueError('fault evidence is required')
    for path in marker['evidence']:evidence_path(path)
    stamp(marker['time']);return marker


def fault(provider,account_domain,campaign,reason,evidence,time=None):
    scope='campaign' if reason in LOCAL_REASONS else 'provider_account'
    return validate_marker({'contract_version':1,'scope':scope,'provider':provider,'account_domain':account_domain,
            'campaign':campaign,'reason':reason,'evidence':list(evidence),'time':time or datetime.now(timezone.utc).isoformat()})


def decision(marker,*,provider,account_domain,campaign,now=None,max_age_seconds=86400):
    validate_marker(marker);identity(provider);identity(campaign)
    if account_domain is not None:identity(account_domain)
    if marker['provider']!=provider:return {'blocked':False,'diagnostic':'OTHER_PROVIDER'}
    if marker['account_domain'] is not None and account_domain is not None and marker['account_domain']!=account_domain:
        return {'blocked':False,'diagnostic':'OTHER_CONFIRMED_ACCOUNT_DOMAIN'}
    if marker['scope']=='campaign' and marker['campaign']!=campaign:
        return {'blocked':False,'diagnostic':'OTHER_CAMPAIGN_LOCAL_FAULT'}
    current=now or datetime.now(timezone.utc)
    if current.tzinfo is None:raise ValueError('current time needs timezone')
    age=(current-stamp(marker['time'])).total_seconds()
    if age<0 or age>max_age_seconds:
        return {'blocked':True,'diagnostic':'STALE_MARKER_REVIEW_REQUIRED'}
    unknown=marker['scope']=='provider_account' and (account_domain is None or marker['account_domain'] is None)
    return {'blocked':True,'diagnostic':'UNKNOWN_ACCOUNT_DOMAIN_PAUSE_PROVIDER' if unknown else 'MATCHING_SCOPE_STOP'}


def record_marker(directory,marker):
    validate_marker(marker);directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    path=directory/(uuid.uuid4().hex+'.json')
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(marker,stream,indent=2);stream.write('\n')
    return path


def stop_file(path,*,provider,account_domain,campaign):
    """Explicit legacy stop files remain local prerequisites, never global facts."""
    path=Path(path)
    if not path.exists():return {'blocked':False,'diagnostic':'NO_MARKER'}
    try:
        marker=json.loads(path.read_text(encoding='utf-8'))
        return decision(marker,provider=provider,account_domain=account_domain,campaign=campaign)
    except (ValueError,TypeError,KeyError):
        return {'blocked':True,'diagnostic':'LEGACY_OR_INVALID_LOCAL_MARKER_REVIEW_REQUIRED'}


def classify_failure(reason,transport_text=''):
    """Classify transport evidence, never candidate/source prose.

    Missing credentials in a fresh home is local. An otherwise unlocalized
    account auth failure pauses the same provider until its domain is known.
    Parsing/accounting/output errors never prove a provider-wide quota event.
    """
    text=transport_text.lower()
    if any(s in text for s in ('no authentication information','not logged in','missing authentication','no credentials')):return 'auth_home'
    if any(s in text for s in ('rate limit','rate_limit','too many requests')):return 'rate_limit'
    if any(s in text for s in ('quota exhausted','quota exceeded','usage limit','credits exhausted','insufficient_quota')):return 'quota'
    if any(s in text for s in ('over capacity','at capacity','capacity limit')):return 'capacity'
    if any(s in text for s in ('unauthorized','authentication failed','account revoked','http 401')):return 'auth_account'
    if reason in LOCAL_REASONS:return reason
    return {'missing_or_invalid_accounting':'accounting','event_parse':'parse','incomplete_reservation':'process',
            'cli_failure':'process','host_skill_isolation_unverified_or_leaked':'fixture',
            'reported_model_mismatch':'fixture'}.get(reason,'unknown_local')


class CampaignLedger:
    """Conservative reservations: unknown/in-flight attempts consume capacity forever.

    File creation lock coordinates threads/processes. A crash-held lock requires
    explicit review; it is never deleted as a time-based guess.
    """
    def __init__(self,root,*,provider,account_domain,campaign,cap,max_inflight=1):
        if type(cap) is not int or not 1<=cap<=9999 or type(max_inflight) is not int or not 1<=max_inflight<=cap:
            raise ValueError('positive integer cap/inflight required')
        identity(provider);identity(campaign)
        if account_domain is not None:identity(account_domain)
        self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
        self.config={'contract_version':1,'provider':provider,'account_domain':account_domain,'campaign':campaign,'cap':cap,'max_inflight':max_inflight}

    @contextmanager
    def locked(self):
        path=self.root/'reservation.lock'
        try:stream=path.open('x',encoding='utf-8')
        except FileExistsError as exc:raise ReservationBusy('LOCKED_REVIEW_REQUIRED_OR_RETRY_WHEN_OWNER_EXITS') from exc
        except PermissionError as exc:
            # Windows may return access-denied while another owner deletes the
            # exclusive lock. Never bypass the lock or guess that it is stale.
            raise ReservationBusy('LOCK_TRANSITION_OR_PERMISSION_REVIEW_REQUIRED') from exc
        try:
            with stream:stream.write('reservation in progress\n')
            yield
        finally:path.unlink()

    def reserve(self,markers=()):
        with self.locked():
            config=self.root/'campaign.json'
            if config.exists():
                if json.loads(config.read_text(encoding='utf-8'))!=self.config:
                    raise CoordinationBlocked('CAMPAIGN_IDENTITY_OR_BUDGET_CHANGED: never switch to bypass a stop')
            else:
                with config.open('x',encoding='utf-8') as stream:json.dump(self.config,stream,sort_keys=True)
            for marker in markers:
                result=decision(marker,**{k:self.config[k] for k in ('provider','account_domain','campaign')})
                if result['blocked']:raise CoordinationBlocked(result['diagnostic'])
            tickets=sorted(self.root.glob('attempt-*.json'))
            if len(tickets)>=self.config['cap']:raise CoordinationBlocked('CLI_CAP_EXHAUSTED')
            active=[p for p in tickets if not p.with_suffix('.result').exists()]
            if len(active)>=self.config['max_inflight']:raise ReservationBusy('INFLIGHT_OR_UNCERTAIN_RESERVATION')
            ticket=self.root/('attempt-'+str(len(tickets)+1).zfill(4)+'.json')
            with ticket.open('x',encoding='utf-8') as stream:json.dump({'id':ticket.stem,'time':datetime.now(timezone.utc).isoformat()},stream)
            return ticket.stem

    def finish(self,ticket,status):
        if not isinstance(ticket,str) or not re.fullmatch(r'attempt-[0-9]{4}',ticket):raise ValueError('invalid ticket')
        if status not in ('PASS','FAIL','BLOCKED_ENVIRONMENT','CANCELLED_UNKNOWN'):raise ValueError('invalid attempt result')
        with self.locked():
            path=self.root/(ticket+'.json')
            if not path.is_file():raise ValueError('unknown ticket')
            with path.with_suffix('.result').open('x',encoding='utf-8') as stream:json.dump({'status':status},stream)
