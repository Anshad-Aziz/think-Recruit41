from django.db import models

class User(models.Model):
    str_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)

    def __str__(self):
        return self.str_id

class Connection(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections2')

    class Meta:
        unique_together = ('user1', 'user2')

    def save(self, *args, **kwargs):
        if self.user1.str_id > self.user2.str_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)
