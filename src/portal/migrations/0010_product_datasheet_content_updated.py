# Migration: ProductDatasheet – content_md, optional file, updated_at

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0009_systeminfo"),
    ]

    operations = [
        migrations.AddField(
            model_name="productdatasheet",
            name="content_md",
            field=models.TextField(blank=True, default="", help_text="Optional: Build the datasheet in Markdown (tables, headings, etc.). Shown at /datasheet/<product-slug>/."),
        ),
        migrations.AddField(
            model_name="productdatasheet",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="productdatasheet",
            name="file",
            field=models.FileField(blank=True, help_text="Optional: PDF from manufacturer", null=True, upload_to="product_datasheets/"),
        ),
        migrations.AlterModelOptions(
            model_name="productdatasheet",
            options={"ordering": ["-updated_at"]},
        ),
    ]
