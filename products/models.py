from django.db import models

CATEGORY_CHOICES = (
    ('HA', 'House/Apartment'),
    ('C', 'Car'),
    ('F', 'Furniture'),
    ('E', 'Electronics'),
    ('M', 'Miscellaneous')
)

LABLE_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

# Create your models here.
class Product(models.Model):
    title       = models.CharField(max_length = 120)
    description = models.TextField(blank = True, null = True)
    price       = models.DecimalField(decimal_places = 2, max_digits = 10000)
    summary     = models.TextField(blank = True, null = False)
    category    = models.CharField(choices = CATEGORY_CHOICES, max_length = 2)
    label       = models.CharField(choices = LABLE_CHOICES, max_length = 1)
    Product_Main_Img = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

