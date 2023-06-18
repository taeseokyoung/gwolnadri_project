from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import User


class UserManager(BaseUserManager):
    def create_user(self, email, password, username, **kwargs):
        if not email:
            raise ValueError("사용자 이메일은 필수 입력 사항입니다.")
        elif not username:
            raise ValueError("사용자 이름은 필수 입력 사항입니다.")
        elif not password:
            raise ValueError("사용자 비밀번호는 필수 입력 사항입니다.")

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=email, username=username, password=password)

        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    username = models.CharField(max_length=20, unique=True, null=True, blank=False)
    password = models.CharField(max_length=255)
    profile_image = models.URLField(null=True, blank=True)
    # profile_image = models.ImageField(upload_to="%Y/%m", blank=True)
    # URL으로 할건지, 파일로 받을건지 정해서 하나 사용하기.

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_member_of_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
