from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_unambiguous_legacy_todos(apps, schema_editor):
    Todo = apps.get_model('tasks', 'Todo')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    database = schema_editor.connection.alias
    user_ids = list(User.objects.using(database).values_list('pk', flat=True)[:2])
    if len(user_ids) == 1:
        Todo.objects.using(database).filter(owner__isnull=True).update(owner_id=user_ids[0])


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='todos',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(assign_unambiguous_legacy_todos, migrations.RunPython.noop),
    ]