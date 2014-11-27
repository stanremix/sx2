# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table('people_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tag', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('avatar', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('age', self.gf('django.db.models.fields.IntegerField')(default=18, null=True, blank=True)),
            ('zodiac', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('wx', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('deviceid', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('push_setting', self.gf('django.db.models.fields.CharField')(default='1', max_length=20, null=True, blank=True)),
            ('login_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('is_guest', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('profile_category', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('people', ['Profile'])

        # Adding model 'Auth'
        db.create_table('people_auth', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tag', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('auth_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('auth_from', self.gf('django.db.models.fields.CharField')(default='sina', max_length=100)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('expire', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('people', ['Auth'])

        # Adding model 'Feedback'
        db.create_table('people_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tag', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('feedback', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('level', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('reply_text', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('is_system', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('people', ['Feedback'])

        # Adding model 'User_Log'
        db.create_table('people_user_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tag', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('action', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('people', ['User_Log'])


    def backwards(self, orm):
        # Deleting model 'Profile'
        db.delete_table('people_profile')

        # Deleting model 'Auth'
        db.delete_table('people_auth')

        # Deleting model 'Feedback'
        db.delete_table('people_feedback')

        # Deleting model 'User_Log'
        db.delete_table('people_user_log')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'people.auth': {
            'Meta': {'object_name': 'Auth'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'auth_from': ('django.db.models.fields.CharField', [], {'default': "'sina'", 'max_length': '100'}),
            'auth_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expire': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tag': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'people.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'feedback': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reply_text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tag': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'people.profile': {
            'Meta': {'object_name': 'Profile'},
            'age': ('django.db.models.fields.IntegerField', [], {'default': '18', 'null': 'True', 'blank': 'True'}),
            'avatar': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'deviceid': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'gender': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_guest': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'login_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'profile_category': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'push_setting': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'wx': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zodiac': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'people.user_log': {
            'Meta': {'object_name': 'User_Log'},
            'action': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['people']