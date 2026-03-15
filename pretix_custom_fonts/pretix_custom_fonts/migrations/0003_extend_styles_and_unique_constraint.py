from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pretix_custom_fonts', '0002_customfont_style'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfont',
            name='style',
            field=models.CharField(choices=[('regular', 'Regular'), ('italic', 'Italic'), ('bold', 'Bold'), ('bolditalic', 'Bold Italic'), ('thin', 'Thin'), ('thinitalic', 'Thin Italic'), ('extralight', 'Extra Light'), ('light', 'Light'), ('medium', 'Medium'), ('italicbold', 'Italic Bold'), ('black', 'Black')], default='regular', max_length=20, verbose_name='Font style'),
        ),
        migrations.AddConstraint(
            model_name='customfont',
            constraint=models.UniqueConstraint(fields=('organizer', 'name', 'style'), name='unique_font_per_organizer_name_style'),
        ),
    ]
