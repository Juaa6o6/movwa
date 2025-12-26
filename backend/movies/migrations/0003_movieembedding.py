from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_boxofficerank'),
    ]

    operations = [
        migrations.CreateModel(
            name='MovieEmbedding',
            fields=[
                ('movie', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='embedding', serialize=False, to='movies.movie')),
                ('vector', models.JSONField()),
                ('model_version', models.CharField(default='text-embedding-3-small', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
