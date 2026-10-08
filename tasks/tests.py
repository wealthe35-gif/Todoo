from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Todo


class TodoViewsTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(username='owner', password='test-password')
		self.other_user = user_model.objects.create_user(username='other', password='test-password')
		self.client.force_login(self.user)

	def test_signup_creates_account_and_saves_user_todos(self):
		password = 'N5!valid-long-passphrase'
		response = self.client.post(reverse('signup'), {
			'username': 'new-user',
			'password1': password,
			'password2': password,
		})

		self.assertRedirects(response, reverse('todo_list'))
		new_user = get_user_model().objects.get(username='new-user')
		self.assertEqual(response.wsgi_request.user, new_user)

		self.client.post(reverse('todo_list'), {'title': 'Saved for later'})
		self.client.logout()
		self.assertTrue(self.client.login(username='new-user', password=password))
		self.assertContains(self.client.get(reverse('todo_list')), 'Saved for later')
		self.assertTrue(Todo.objects.filter(owner=new_user, title='Saved for later').exists())

	def test_signup_rejects_duplicate_username(self):
		response = self.client.post(reverse('signup'), {
			'username': self.user.username,
			'password1': 'N5!valid-long-passphrase',
			'password2': 'N5!valid-long-passphrase',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'already exists')

	def test_signup_explains_invalid_password(self):
		response = self.client.post(reverse('signup'), {
			'username': 'weak-password-user',
			'password1': 'password',
			'password2': 'password',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Your account was not created')
		self.assertContains(response, 'too common')
		self.assertFalse(get_user_model().objects.filter(username='weak-password-user').exists())

	def test_todo_list_requires_login(self):
		self.client.logout()

		response = self.client.get(reverse('todo_list'))

		self.assertRedirects(response, f"{reverse('login')}?next={reverse('todo_list')}")

	def test_todo_list_shows_only_current_users_todos(self):
		own_todo = Todo.objects.create(owner=self.user, title='Mine')
		Todo.objects.create(owner=self.other_user, title='Not mine')

		response = self.client.get(reverse('todo_list'))

		self.assertContains(response, own_todo.title)
		self.assertNotContains(response, 'Not mine')

	def test_create_trims_title_and_ignores_blank_title(self):
		response = self.client.post(reverse('todo_list'), {'title': '  Buy milk  '})
		self.assertRedirects(response, reverse('todo_list'))
		self.assertTrue(Todo.objects.filter(owner=self.user, title='Buy milk').exists())

		self.client.post(reverse('todo_list'), {'title': '   '})
		self.assertEqual(Todo.objects.filter(owner=self.user).count(), 1)

	def test_update_requires_post_and_ownership(self):
		todo = Todo.objects.create(owner=self.user, title='Mine')
		other_todo = Todo.objects.create(owner=self.other_user, title='Theirs')

		self.assertEqual(self.client.get(reverse('update_todo', args=[todo.pk])).status_code, 405)
		self.assertEqual(self.client.post(reverse('update_todo', args=[other_todo.pk])).status_code, 404)
		todo.refresh_from_db()
		self.assertFalse(todo.completed)

		self.client.post(reverse('update_todo', args=[todo.pk]))
		todo.refresh_from_db()
		self.assertTrue(todo.completed)

	def test_delete_requires_post_and_ownership(self):
		todo = Todo.objects.create(owner=self.user, title='Mine')
		other_todo = Todo.objects.create(owner=self.other_user, title='Theirs')

		self.assertEqual(self.client.get(reverse('delete_todo', args=[todo.pk])).status_code, 405)
		self.assertEqual(self.client.post(reverse('delete_todo', args=[other_todo.pk])).status_code, 404)
		self.assertTrue(Todo.objects.filter(pk=todo.pk).exists())

		self.client.post(reverse('delete_todo', args=[todo.pk]))
		self.assertFalse(Todo.objects.filter(pk=todo.pk).exists())
