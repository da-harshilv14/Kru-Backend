from django.db import migrations, models


class Migration(migrations.Migration):

    # This is a merge migration resolving two conflicting 0002 migrations.
    dependencies = [
        ('support', '0002_alter_grievance_status'),
        ('support', '0002_update_status_choices'),
    ]

    operations = [
        # Ensure the final choices for 'status' are the desired set.
        migrations.AlterField(
            model_name='grievance',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Under Review', 'Under Review')], default='Pending', max_length=32),
        ),
    ]
