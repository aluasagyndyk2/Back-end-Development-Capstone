from django.test import TestCase

from django.contrib.auth.models import User
from django.urls import reverse
from .models import Concert, ConcertAttending


class BandWorkflowTests(TestCase):
    def test_public_pages(self):
        for route, template in [('index', 'index.html'), ('songs', 'songs.html'), ('photos', 'photos.html')]:
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template)
            self.assertContains(response, '<nav id="navbar"')

    def test_signup_login_logout(self):
        response = self.client.post(reverse('signup'), {'username': 'fan', 'password': 'test-pass-123'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.get(username='fan').check_password('test-pass-123'))
        self.assertEqual(self.client.get(reverse('logout')).status_code, 302)
        response = self.client.post(reverse('login'), {'username': 'fan', 'password': 'test-pass-123'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {'username': 'missing', 'password': 'incorrect'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_invalid_concert_id_returns_bad_request(self):
        user = User.objects.create_user(username='fan', password='pass123')
        self.client.force_login(user)
        for value in ['abc', '', None]:
            data = {'attendee_choice': 'Attending'}
            if value is not None:
                data['concert_id'] = value
            self.assertEqual(self.client.post(reverse('concert_attendee'), data).status_code, 400)

    def test_anonymous_concerts_require_login(self):
        self.assertEqual(self.client.get(reverse('concerts')).status_code, 302)

    def test_attendance_is_per_user_and_can_change(self):
        concert = Concert.objects.create(concert_name='Test Concert', duration=2, city='Paris')
        user = User.objects.create_user(username='fan', password='pass123')
        other = User.objects.create_user(username='other', password='pass123')
        ConcertAttending.objects.create(concert=concert, user=other, attending='Attending')
        self.client.force_login(user)
        self.client.post(reverse('concert_attendee'), {'concert_id': concert.id, 'attendee_choice': 'Attending'})
        self.assertEqual(ConcertAttending.objects.filter(user=user).get().attending, 'Attending')
        self.client.post(reverse('concert_attendee'), {'concert_id': concert.id, 'attendee_choice': 'Not Attending'})
        self.assertEqual(ConcertAttending.objects.filter(user=user).get().attending, 'Not Attending')
        self.assertEqual(ConcertAttending.objects.filter(user=other).get().attending, 'Attending')

# Create your tests here.
