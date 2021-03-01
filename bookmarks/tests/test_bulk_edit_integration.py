from django.forms import model_to_dict
from django.test import TestCase
from django.urls import reverse

from bookmarks.models import Bookmark
from bookmarks.tests.helpers import BookmarkFactoryMixin


class BulkEditIntegrationTests(TestCase, BookmarkFactoryMixin):

    def setUp(self) -> None:
        user = self.get_or_create_test_user()
        self.client.force_login(user)

    def assertBookmarksAreUnmodified(self, bookmarks: [Bookmark]):
        self.assertEqual(len(bookmarks), Bookmark.objects.count())

        for bookmark in bookmarks:
            self.assertEqual(model_to_dict(bookmark), model_to_dict(Bookmark.objects.get(id=bookmark.id)))

    def test_bulk_archive(self):
        bookmark1 = self.setup_bookmark()
        bookmark2 = self.setup_bookmark()
        bookmark3 = self.setup_bookmark()

        self.client.post(reverse('bookmarks:bulk_edit'), {
            'bulk_archive': [''],
            'bookmark_id': [str(bookmark1.id), str(bookmark2.id), str(bookmark3.id)],
        })

        self.assertTrue(Bookmark.objects.get(id=bookmark1.id).is_archived)
        self.assertTrue(Bookmark.objects.get(id=bookmark2.id).is_archived)
        self.assertTrue(Bookmark.objects.get(id=bookmark3.id).is_archived)

    def test_bulk_unarchive(self):
        bookmark1 = self.setup_bookmark(is_archived=True)
        bookmark2 = self.setup_bookmark(is_archived=True)
        bookmark3 = self.setup_bookmark(is_archived=True)

        self.client.post(reverse('bookmarks:bulk_edit'), {
            'bulk_unarchive': [''],
            'bookmark_id': [str(bookmark1.id), str(bookmark2.id), str(bookmark3.id)],
        })

        self.assertFalse(Bookmark.objects.get(id=bookmark1.id).is_archived)
        self.assertFalse(Bookmark.objects.get(id=bookmark2.id).is_archived)
        self.assertFalse(Bookmark.objects.get(id=bookmark3.id).is_archived)

    def test_bulk_edit_handles_empty_bookmark_id(self):
        bookmark1 = self.setup_bookmark()
        bookmark2 = self.setup_bookmark()
        bookmark3 = self.setup_bookmark()

        response = self.client.post(reverse('bookmarks:bulk_edit'), {
            'bulk_archive': [''],
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('bookmarks:bulk_edit'), {
            'bulk_archive': [''],
            'bookmark_id': [],
        })
        self.assertEqual(response.status_code, 302)

        self.assertBookmarksAreUnmodified([bookmark1, bookmark2, bookmark3])

    def test_empty_action_does_not_modify_bookmarks(self):
        bookmark1 = self.setup_bookmark()
        bookmark2 = self.setup_bookmark()
        bookmark3 = self.setup_bookmark()

        self.client.post(reverse('bookmarks:bulk_edit'), {
            'bookmark_id': [str(bookmark1.id), str(bookmark2.id), str(bookmark3.id)],
        })

        self.assertBookmarksAreUnmodified([bookmark1, bookmark2, bookmark3])
