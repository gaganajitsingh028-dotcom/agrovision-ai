from django.db import models

class YieldPrediction(models.Model):

    rainfall = models.FloatField()

    temperature = models.FloatField()

    pesticides = models.FloatField()

    area = models.CharField(max_length=100)

    item = models.CharField(max_length=100)

    year = models.IntegerField()

    result = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item
    
class DiseasePrediction(models.Model):

    image = models.ImageField(upload_to='predictions/')

    result = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.result    
