import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test title',
            slug='test_slug',
            description='Test descrip'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
        )
        cls.comment = Comment.objects.create(
            text='Test comment',
            author=cls.post.author,
            post_id=cls.post.id
        )

    def test_post(self):
        count_posts = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test text',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_1 = Post.objects.order_by('id').last()
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={
                'username': self.post.author
            }
        ))
        self.assertEqual(post_1.text, form_data['text'])
        self.assertEqual(post_1.group.id, form_data['group'])
        self.assertEqual(post_1.image.name, 'posts/' + form_data['image'].name)

    def test_authorized_edit_post(self):
        form_data = {
            'text': 'Another test text',
            'group': self.group.id
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={
                'post_id': self.post.id
            }),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(id=self.post.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.group.id, form_data['group'])

    def test_comment_create(self):
        form_data = {
            'text': 'Test comment'
        }
        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={
                'post_id': self.post.id
            }
        ),
            data=form_data,
            follow=True,
        )
        post_edit = Comment.objects.order_by('id').last()
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
