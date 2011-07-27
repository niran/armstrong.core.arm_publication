from armstrong.dev.tasks import *


settings = {
    'DEBUG': True,
    'INSTALLED_APPS': (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'armstrong.core.arm_publication',
        'armstrong.core.arm_publication.tests.arm_publication_support',
        'lettuce.django',
    ),
}

full_name = "armstrong.core.arm_publication"
main_app = "arm_publication"
tested_apps = ("arm_publication", )
