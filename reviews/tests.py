"""Tests de rendu et d'accessibilite.

Le test le plus utile ici est `test_no_template_syntax_leaks`. Django ne
reconnait un commentaire `{# #}` que sur UNE SEULE ligne (son lexer ne
couvre pas les retours a la ligne) : un commentaire multi-ligne s'affiche
donc tel quel dans la page. Ce test rend toutes les pages et verifie
qu'aucune syntaxe de gabarit n'atteint le HTML envoye au navigateur.
"""
import re
from html.parser import HTMLParser

from django.test import TestCase
from django.urls import reverse

from .models import Review, Ticket, User

PASSWORD = 'Litrevu-2026'

BLOCK_ELEMENTS = {'ul', 'ol', 'div', 'p', 'section', 'form', 'fieldset', 'table'}


class ParagraphNestingParser(HTMLParser):
    """Repere un element de bloc a l'interieur d'un <p>.

    C'est du HTML invalide : le navigateur ferme le <p> de lui-meme, ce qui
    casse la mise en page sans qu'aucune erreur n'apparaisse cote serveur.
    """

    def __init__(self):
        super().__init__()
        self.open_paragraphs = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.open_paragraphs.append(self.getpos()[0])
        elif tag in BLOCK_ELEMENTS and self.open_paragraphs:
            self.problems.append((tag, self.open_paragraphs[-1], self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag == 'p' and self.open_paragraphs:
            self.open_paragraphs.pop()


class PageRenderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='alice', password=PASSWORD)
        cls.other = User.objects.create_user(username='bob', password=PASSWORD)
        cls.own_ticket = Ticket.objects.create(
            user=cls.user, title='Mon billet', description='Description de mon billet.')
        cls.other_ticket = Ticket.objects.create(
            user=cls.other, title='Billet de bob', description='Description du billet de bob.')
        # Billet sur lequel alice n'a pas encore ecrit : la regle "une critique
        # par utilisateur et par billet" autorise donc la page de creation.
        cls.reviewable_ticket = Ticket.objects.create(
            user=cls.other, title='Autre billet de bob', description='A critiquer.')
        cls.own_review = Review.objects.create(
            ticket=cls.other_ticket, user=cls.user, headline='Ma critique', rating=4,
            body='Le corps de ma critique.')

    def connected_pages(self):
        """Toutes les pages accessibles a un utilisateur connecte."""
        return [
            reverse('feed'),
            reverse('posts'),
            reverse('follows'),
            reverse('create_ticket'),
            reverse('create_ticket_and_review'),
            reverse('create_review', args=[self.reviewable_ticket.id]),
            reverse('edit_ticket', args=[self.own_ticket.id]),
            reverse('delete_ticket', args=[self.own_ticket.id]),
            reverse('edit_review', args=[self.own_review.id]),
            reverse('delete_review', args=[self.own_review.id]),
        ]

    def public_pages(self):
        """Pages accessibles sans etre connecte."""
        return [reverse('login'), reverse('signup')]

    def test_no_template_syntax_leaks(self):
        """Aucune balise de gabarit ne doit apparaitre dans le HTML rendu."""
        for url in self.public_pages():
            with self.subTest(url=url):
                content = self.client.get(url).content.decode()
                for syntax in ('{#', '#}', '{%', '%}', '{{', '}}'):
                    self.assertNotIn(syntax, content, f'{syntax} visible dans {url}')

        self.client.force_login(self.user)
        for url in self.connected_pages():
            with self.subTest(url=url):
                content = self.client.get(url).content.decode()
                for syntax in ('{#', '#}', '{%', '%}', '{{', '}}'):
                    self.assertNotIn(syntax, content, f'{syntax} visible dans {url}')

    def test_connected_pages_return_200(self):
        self.client.force_login(self.user)
        for url in self.connected_pages():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_anonymous_is_redirected_to_login(self):
        for url in self.connected_pages():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response.url)

    def test_cannot_edit_another_users_ticket(self):
        """La page de modification d'autrui doit renvoyer 403, pas 404."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('edit_ticket', args=[self.other_ticket.id]))
        self.assertEqual(response.status_code, 403)

    def test_form_error_is_linked_to_its_field(self):
        """L'erreur doit etre reliee au champ, pas seulement affichee a cote."""
        self.client.force_login(self.user)
        response = self.client.post(reverse('create_ticket'), {'title': '', 'description': ''})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('aria-invalid="true"', content)
        self.assertIn('aria-describedby="id_title_error"', content)
        self.assertIn('id="id_title_error"', content)

    def test_rating_is_a_labelled_radio_group(self):
        """La note est un groupe de radios avec un <legend>, donc annonce."""
        self.client.force_login(self.user)
        content = self.client.get(
            reverse('create_review', args=[self.reviewable_ticket.id])).content.decode()
        self.assertIn('<legend', content)
        self.assertEqual(content.count('name="rating"'), 6)

    def test_login_error_is_shown_once(self):
        """Un mauvais identifiant ne doit produire qu'UNE alerte, pas deux.

        Le gabarit de login ecrivait sa propre alerte « Identifiants
        invalides » en plus de celle generee par form.non_field_errors : la
        meme erreur s'affichait deux fois, empilee.
        """
        response = self.client.post(
            reverse('login'), {'username': self.user.username, 'password': 'mauvais'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertEqual(content.count('alert-error'), 1)
        self.assertEqual(content.count('Identifiants invalides'), 1)

    def test_skip_link_is_present_and_first(self):
        """Le lien d'evitement (WCAG 2.4.1) doit etre le premier focusable."""
        content = self.client.get(reverse('login')).content.decode()
        self.assertIn('href="#main-content"', content)
        self.assertLess(content.index('skip-link'), content.index('<main'))

    def test_no_block_element_inside_a_paragraph(self):
        """Un <ul> ou <div> dans un <p> est invalide et casse la mise en page.

        Les help_text de Django contiennent parfois une liste (regles de mot
        de passe) : le gabarit doit donc les rendre dans un <div>, pas un <p>.
        """
        self.client.force_login(self.user)
        for url in self.public_pages() + self.connected_pages():
            with self.subTest(url=url):
                parser = ParagraphNestingParser()
                parser.feed(self.client.get(url).content.decode())
                self.assertEqual(parser.problems, [], f'balise de bloc dans un <p> sur {url}')

    def test_aria_describedby_targets_exist(self):
        """Chaque id cite par aria-describedby doit exister dans la page.

        Django ajoute lui-meme aria-describedby="id_x_helptext id_x_error"
        sur les champs : c'est au gabarit d'ecrire ces ids, sinon la
        reference pointe dans le vide.
        """
        self.client.force_login(self.user)
        responses = [self.client.get(url) for url in self.public_pages() + self.connected_pages()]
        responses.append(self.client.post(
            reverse('signup'), {'username': 'carol', 'password1': 'a', 'password2': 'b'}))
        responses.append(self.client.post(
            reverse('create_review', args=[self.reviewable_ticket.id]), {'headline': ''}))
        for response in responses:
            with self.subTest(url=response.request['PATH_INFO']):
                content = response.content.decode()
                ids = set(re.findall(r'id="([^"]+)"', content))
                for group in re.findall(r'aria-describedby="([^"]+)"', content):
                    for target in group.split():
                        self.assertIn(target, ids, f'aria-describedby cible {target}, absent de la page')
