from django.db import models

# Create your models here.
class PipeData(models.Model):
    mid = models.TextField()
    b = models.TextField()
    c = models.TextField()
    d = models.TextField()
    e = models.TextField()
    ts = models.TextField()
    count = models.TextField()
    weight = models.TextField()
    ps = models.TextField()
    site_time = models.TextField()
    def toDic(self):
        return{'a': self.mid, 'b': self.b, 'c': self.c, 'd': self.d, 'e': self.e, 'ts': self.ts, 'count': self.count, 'weight': self.weight, 'ps': self.ps, "site_time": self.site_time}
