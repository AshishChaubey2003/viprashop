import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image_emoji', models.CharField(default='📦', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idempotency_key', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('session_key', models.CharField(max_length=100)),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
                    default='pending',
                    max_length=20,
                )),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stripe_session_id', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price_at_purchase', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='store.order',
                )),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='store.product',
                )),
            ],
        ),
    ]
    