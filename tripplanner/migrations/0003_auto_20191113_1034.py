# Generated by Django 2.2.6 on 2019-11-13 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tripplanner', '0002_auto_20191112_1917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='line',
            name='stations',
        ),
        migrations.RemoveField(
            model_name='station',
            name='xpos',
        ),
        migrations.RemoveField(
            model_name='station',
            name='ypos',
        ),
        migrations.RemoveField(
            model_name='stationorder',
            name='order_num',
        ),
        migrations.RemoveField(
            model_name='stationorder',
            name='station',
        ),
        migrations.RemoveField(
            model_name='timetabledata',
            name='station_order',
        ),
        migrations.AddField(
            model_name='stationorder',
            name='distance',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stationorder',
            name='station_from',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='from+', to='tripplanner.Station'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stationorder',
            name='station_to',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='to+', to='tripplanner.Station'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='timetabledata',
            name='station',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='tripplanner.Station'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='line',
            name='name',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='station',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]
