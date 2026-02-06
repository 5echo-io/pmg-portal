# Generated migration for Customer.logo field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_customer_org_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='logo',
            field=models.ImageField(blank=True, help_text='Customer logo displayed on dashboard', null=True, upload_to='customer_logos/'),
        ),
    ]
