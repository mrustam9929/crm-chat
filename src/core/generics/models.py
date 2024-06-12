from django.db import models


class ModelWithDate(models.Model):
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Дата обновления'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания'
    )

    class Meta:
        abstract = True


class ModelWithOnlyUpdatedDate(models.Model):
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Дата обновления'
    )

    class Meta:
        abstract = True


class Langs(models.TextChoices):
    RU = 'ru', 'Русский'
    EN = 'en', 'Английский'
    UZ = 'uz', 'Узбекский'
