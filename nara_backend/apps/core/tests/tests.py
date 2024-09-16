from core.models import NBaseDocument
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class ConcreteModel(NBaseDocument):
    class Meta:
        app_label = "concrete"


class NBaseDocumentTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password456")
        self.model = ConcreteModel.objects.create(
            created_by=self.user1, updated_by=self.user1
        )

    def test_creation(self):
        self.assertIsNotNone(self.model.id)
        self.assertEqual(self.model.created_by, self.user1)
        self.assertEqual(self.model.updated_by, self.user1)
        self.assertFalse(self.model.is_deleted)
        self.assertIsNone(self.model.deleted_at)

    def test_auto_timestamps(self):
        original_created_at = self.model.created_at
        original_updated_at = self.model.updated_at
        self.model.save()
        self.assertEqual(self.model.created_at, original_created_at)
        self.assertGreater(self.model.updated_at, original_updated_at)

    def test_soft_delete(self):
        self.model.soft_delete(self.user2)
        self.assertTrue(self.model.is_deleted)
        self.assertIsNotNone(self.model.deleted_at)
        self.assertEqual(self.model.updated_by, self.user2)

    def test_restore(self):
        self.model.soft_delete(self.user2)
        self.model.restore(self.user1)
        self.assertFalse(self.model.is_deleted)
        self.assertIsNone(self.model.deleted_at)
        self.assertEqual(self.model.updated_by, self.user1)

    def test_soft_delete_without_user(self):
        self.model.soft_delete()
        self.assertTrue(self.model.is_deleted)
        self.assertIsNotNone(self.model.deleted_at)
        self.assertEqual(self.model.updated_by, self.user1)

    def test_restore_without_user(self):
        self.model.soft_delete(self.user2)
        self.model.restore()
        self.assertFalse(self.model.is_deleted)
        self.assertIsNone(self.model.deleted_at)
        self.assertEqual(self.model.updated_by, self.user2)

    def test_queryset_filtering(self):
        model2 = ConcreteModel.objects.create(
            created_by=self.user2, updated_by=self.user2
        )
        self.model.soft_delete()
        active_models = ConcreteModel.objects.filter(is_deleted=False)
        deleted_models = ConcreteModel.objects.filter(is_deleted=True)
        self.assertEqual(active_models.count(), 1)
        self.assertEqual(deleted_models.count(), 1)
        self.assertEqual(active_models.first(), model2)
        self.assertEqual(deleted_models.first(), self.model)
