from django.db import migrations, models
import django.db.models.deletion
import pretix_custom_fonts.pretix_custom_fonts.models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pretixbase', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFont',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A name for the font family, e.g. "Roboto".', max_length=255, verbose_name='Family name')),
                ('style', models.CharField(choices=[('regular', 'Regular'), ('bold', 'Bold'), ('italic', 'Italic'), ('bolditalic', 'Bold Italic')], default='regular', max_length=20, verbose_name='Font style')),
                ('font_file', models.FileField(help_text='Only TTF and OTF files are supported.', upload_to=pretix_custom_fonts.pretix_custom_fonts.models.font_path, verbose_name='Font file')),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_fonts', to='pretixbase.organizer')),
            ],
        ),
    ]
