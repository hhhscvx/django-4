from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields  # по каким полям будет упорядочивание
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):  # метод который вызывается перед сохранением в БД
        if getattr(model_instance, self.attname) is None:  # если значение не установлено
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    query = {field: getattr(model_instance, field) for field in self.for_fields}
                    qs = qs.filter(**query)  # если указаны поля то чото там с ними ага
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)  # если значение установлено
