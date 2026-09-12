#!/usr/bin/env python
"""Verifie les contrastes du theme « papier » (WCAG 2.1 - 1.4.3 / 1.4.11).

Lit les couleurs dans static/src/input.css, calcule le ratio de contraste de
chaque paire texte/fond reellement utilisee par les gabarits, et sort en
erreur si une paire passe sous le seuil.

Seuils WCAG :
  4.5:1  texte normal
  3.0:1  grand texte (>= 24 px, ou >= 19 px en gras) et elements d'interface

Usage :  .venv/bin/python scripts/check-contrast.py
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INPUT_CSS = REPO / 'static/src/input.css'

FAILURES = []


def hex_to_rgb(value):
    value = value.lstrip('#')
    if len(value) == 3:
        value = ''.join(c * 2 for c in value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    channels = []
    for raw in rgb:
        c = raw / 255
        channels.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground, background):
    l1 = relative_luminance(hex_to_rgb(foreground))
    l2 = relative_luminance(hex_to_rgb(background))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def read_theme():
    """Extrait les variables --color-* : #hex du bloc de theme."""
    text = INPUT_CSS.read_text()
    block = re.search(r'@plugin[^{]*\{([^}]*)\}', text, re.DOTALL)
    if not block:
        sys.exit(f'Bloc de theme introuvable dans {INPUT_CSS}')
    return {
        name: value
        for name, value in re.findall(r'--color-([a-z0-9-]+):\s*(#[0-9a-fA-F]{3,6})', block.group(1))
    }


def check_rule(selector, foreground, background, threshold=4.5):
    """Verifie une regle composee : un element imbrique dans un fond colore.

    Le simple test des variables du theme ne suffit pas. Exemple reel : la
    liste d'erreurs generales d'un formulaire est rendue DANS une alerte
    rouge. La regle .errorlist lui donnait un texte rouge sur ce fond rouge,
    soit 1:1 — invisible — alors que toutes les paires du theme passaient.
    On verifie donc aussi que la regle CSS qui corrige ce cas existe bien.
    """
    css = INPUT_CSS.read_text()
    if selector not in css:
        print(f'  ECHEC {selector} absent de input.css')
        FAILURES.append(f'{selector} : regle de correction absente (risque de texte sur son propre fond)')
        return
    check(f'{selector} -> {foreground} sur {background}', foreground, background, threshold)


def check(label, foreground, background, threshold=4.5):
    c = read_theme()
    fg, bg = c[foreground], c[background]
    ratio = contrast_ratio(fg, bg)
    ok = ratio >= threshold
    status = 'ok  ' if ok else 'ECHEC'
    print(f'  {status} {label:<52} {ratio:5.2f}:1  (seuil {threshold})')
    if not ok:
        FAILURES.append(f'{label} : {ratio:.2f}:1 < {threshold}')


def main():
    theme = read_theme()
    print(f'Couleurs du theme : {len(theme)} variables\n')

    print('Texte sur les surfaces de page et de carte')
    check('texte sur carte (base-content / base-100)', 'base-content', 'base-100')
    check('texte sur fond de page (base-content / base-200)', 'base-content', 'base-200')

    print('\nLibelles sur les boutons pleins')
    for name in ('primary', 'secondary', 'accent', 'neutral',
                 'info', 'success', 'warning', 'error'):
        check(f'{name}-content sur {name}', f'{name}-content', name)

    print('\nLiens et messages, sur carte et sur fond de page')
    for surface in ('base-100', 'base-200'):
        check(f'lien (primary) sur {surface}', 'primary', surface, threshold=4.5)
        check(f'erreur (error) sur {surface}', 'error', surface, threshold=4.5)

    print('\nElements imbriques dans un fond colore (regles composees)')
    check_rule('.alert .errorlist', 'error-content', 'error')

    print('\nBordures et elements non textuels (WCAG 1.4.11)')
    check('bordure (base-300) sur carte', 'base-300', 'base-100', threshold=1.0)

    print()
    if FAILURES:
        print(f'{len(FAILURES)} paire(s) sous le seuil :')
        for failure in FAILURES:
            print(f'  - {failure}')
        return 1
    print('Toutes les paires respectent les seuils WCAG.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
