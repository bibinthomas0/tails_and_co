from django.db import models
from django.template.defaultfilters import slugify
class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=100)

    def __str__(self):
        return self.subcategory_name

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class productcolor(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    gender = models.CharField(max_length=255)
    age = models.CharField(max_length=50)
    color = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug  = models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.color
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product.name +"-"+self.color)
        return super().save(*args, **kwargs)

class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    color = models.ForeignKey(productcolor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')
    
    def __str__(self):
        return self.product.name + ' Image'


class Notifications(models.Model):
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.content
