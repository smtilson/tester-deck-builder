from tortoise import fields, models

class BasicModel(models.Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    version = fields.CharField(max_length=50, null=True)
    class Meta:
        abstract = True