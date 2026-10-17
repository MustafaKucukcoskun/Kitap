#!/usr/bin/env python3
'''Roman denetim aracı.

Kullanım:
  python3 araclar/kontrol.py bolumler/03.md    tek dosya
  python3 araclar/kontrol.py --tum              bütün bölümler
'''
import re
import statistics
import string
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

KOK = Path(__file__).resolve().parent.parent
LISTE = KOK / 'araclar' / 'yasakli.txt'
BOLUMLER = KOK / 'bolumler'
NOKTALAMA = string.punctuation + '«»“”‘’—–…'


def kucuk(metin):
    return metin.replace('I', 'ı').replace('İ', 'i').lower()


def kelimeler(metin):
    sonuc = []
    for parca in kucuk(metin).split():
        parca = parca.strip(NOKTALAMA)
        if parca:
            sonuc.append(parca)
    return sonuc


def ad(yol):
    try:
        return yol.relative_to(KOK)
    except ValueError:
        return yol


def liste_oku():
    duz, desen = [], []
    for satir in LISTE.read_text(encoding='utf-8').splitlines():
        satir = satir.strip()
        if not satir or satir.startswith('#'):
            continue
        if satir.startswith('re:'):
            desen.append(re.compile(satir[3:]))
        else:
            duz.append(kucuk(satir))
    return duz, desen


def obekler(liste, n=4):
    return [' '.join(liste[i:i + n]) for i in range(len(liste) - n + 1)]


def cumle_uzunluklari(metin):
    govde = re.sub('^#.*$', '', metin, flags=re.M)
    parcalar = re.split('[.!?…]+', govde)
    return [len(kelimeler(p)) for p in parcalar if kelimeler(p)]


def dosya_tara(yol):
    metin = yol.read_text(encoding='utf-8')
    sayi = len(kelimeler(metin))
    print()
    print(f'== {ad(yol)} · {sayi} kelime')
    duz, desen = liste_oku()
    bulgu = 0
    for no, satir in enumerate(metin.splitlines(), 1):
        ks = kucuk(satir)
        for ifade in duz:
            if ifade in ks:
                print(f'  satır {no}: «{ifade}»')
                bulgu += 1
        for d in desen:
            if d.search(ks):
                print(f'  satır {no}: kalıp /{d.pattern}/')
                bulgu += 1
    print(f'  işaretlenen ifade: {bulgu}')
    tekrar = [(o, s) for o, s in Counter(obekler(kelimeler(metin))).most_common(10) if s > 1]
    if tekrar:
        print('  tekrar eden dörtlü öbekler: ' + '; '.join(f'«{o}» ×{s}' for o, s in tekrar))
    uz = cumle_uzunluklari(metin)
    if len(uz) > 1:
        print(f'  cümle: {len(uz)} adet, ortalama {statistics.mean(uz):.1f}, '
              f'sapma {statistics.stdev(uz):.1f} kelime (sapma 5 altındaysa ritim tekdüze olabilir)')
    return sayi


def tum_kitap():
    dosyalar = sorted(BOLUMLER.glob('*.md'))
    if not dosyalar:
        print('bolumler/ boş, henüz bölüm yok. Araç çalışıyor.')
        return
    toplam = 0
    hangi = defaultdict(set)
    for yol in dosyalar:
        toplam += dosya_tara(yol)
        for o in set(obekler(kelimeler(yol.read_text(encoding='utf-8')))):
            hangi[o].add(yol.stem)
    print()
    print(f'== Toplam: {toplam} kelime ≈ {toplam / 250:.0f} sayfa (250 kelime/sayfa)')
    tik = sorted(((o, b) for o, b in hangi.items() if len(b) >= 3), key=lambda x: -len(x[1]))[:15]
    if tik:
        print('Kitap çapında tekrar eden öbekler (3+ bölümde):')
        for o, b in tik:
            bolum_listesi = ', '.join(sorted(b))
            print(f'  «{o}» → {bolum_listesi}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == '--tum':
        tum_kitap()
    else:
        dosya_tara(Path(sys.argv[1]).resolve())
