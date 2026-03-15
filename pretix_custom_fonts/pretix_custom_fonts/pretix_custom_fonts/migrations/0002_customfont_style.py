from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pretix_custom_fonts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfont',
            name='style',
            field=models.CharField(choices=[('regular', 'Regular'), ('bold', 'Bold'), ('italic', 'Italic'), ('bolditalic', 'Bold Italic')], default='regular', max_length=20, verbose_name='Font style'),
        ),
        migrations.AlterField(
            model_name='customfont',
            name='name',
            field=models.CharField(help_text='A name for the font family, e.g. "Roboto".', max_length=255, verbose_name='Family name'),
        ),
    ]
