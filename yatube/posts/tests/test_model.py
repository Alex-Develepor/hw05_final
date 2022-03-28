from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_objects_name(self):
        name = PostModelTest.post
        post = name.text[:15]
        self.assertEqual(post, str(name))

    def test_group_name(self):
        name = PostModelTest.group
        group = name.title
        self.assertEqual(group, str(name))

    def test_verbose_name(self):
        post = PostModelTest.post
        name = post._meta.get_field('author').verbose_name
        self.assertEqual(name, 'Aвтор')

    def test_help_text(self):
        post = PostModelTest.post
        text = post._meta.get_field('group').help_text
        self.assertEqual(text, 'Группа, к которой будет относиться пост')
