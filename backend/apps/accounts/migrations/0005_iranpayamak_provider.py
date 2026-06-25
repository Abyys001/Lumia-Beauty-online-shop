from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_wishlistitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='smsprovidersettings',
            name='bearer_token_encrypted',
            field=models.TextField(blank=True, verbose_name='توکن Bearer رمزنگاری\u200cشده'),
        ),
        migrations.AddField(
            model_name='smsprovidersettings',
            name='bearer_token_expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='انقضای Bearer'),
        ),
        migrations.AddField(
            model_name='smsprovidersettings',
            name='line_number',
            field=models.CharField(blank=True, max_length=30, verbose_name='شماره خط IranPayamak'),
        ),
        migrations.AddField(
            model_name='smsprovidersettings',
            name='number_format',
            field=models.CharField(
                choices=[('english', 'English'), ('persian', 'Persian')],
                default='english',
                max_length=10,
                verbose_name='فرمت اعداد پیامک',
            ),
        ),
        migrations.AddField(
            model_name='smsprovidersettings',
            name='panel_password_encrypted',
            field=models.TextField(blank=True, verbose_name='رمز پنل رمزنگاری\u200cشده'),
        ),
        migrations.AddField(
            model_name='smsprovidersettings',
            name='panel_username',
            field=models.CharField(blank=True, max_length=100, verbose_name='نام کاربری پنل'),
        ),
        migrations.AddField(
            model_name='otptemplate',
            name='pattern_code',
            field=models.CharField(blank=True, max_length=50, verbose_name='کد Pattern IranPayamak'),
        ),
        migrations.AlterField(
            model_name='otptemplate',
            name='sms_ir_template_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='شناسه قالب SMS.ir'),
        ),
        migrations.AlterField(
            model_name='smsprovidersettings',
            name='provider_mode',
            field=models.CharField(
                choices=[
                    ('mock', 'Mock (توسعه)'),
                    ('smsir', 'SMS.ir'),
                    ('iranpayamak', 'IranPayamak'),
                ],
                default='mock',
                max_length=20,
                verbose_name='ارائه\u200cدهنده',
            ),
        ),
    ]
