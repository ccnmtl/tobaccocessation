# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Medication'
        db.create_table(u'activity_prescription_writing_medication', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('dosage', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('dispensing', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('signature', self.gf('django.db.models.fields.TextField')()),
            ('refills', self.gf('django.db.models.fields.IntegerField')()),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')()),
            ('dosage_callout', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('dispensing_callout', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('signature_callout', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('refills_callout', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('rx_count', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'activity_prescription_writing', ['Medication'])

        # Adding model 'ActivityState'
        db.create_table(u'activity_prescription_writing_activitystate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='prescription_writing_user', unique=True, to=orm['auth.User'])),
            ('json', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'activity_prescription_writing', ['ActivityState'])

        # Adding model 'Block'
        db.create_table(u'activity_prescription_writing_block', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('medication_name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('show_correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'activity_prescription_writing', ['Block'])


    def backwards(self, orm):
        # Deleting model 'Medication'
        db.delete_table(u'activity_prescription_writing_medication')

        # Deleting model 'ActivityState'
        db.delete_table(u'activity_prescription_writing_activitystate')

        # Deleting model 'Block'
        db.delete_table(u'activity_prescription_writing_block')


    models = {
        u'activity_prescription_writing.activitystate': {
            'Meta': {'object_name': 'ActivityState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prescription_writing_user'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        u'activity_prescription_writing.block': {
            'Meta': {'object_name': 'Block'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medication_name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'show_correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'activity_prescription_writing.medication': {
            'Meta': {'object_name': 'Medication'},
            'dispensing': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dispensing_callout': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dosage': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'dosage_callout': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'refills': ('django.db.models.fields.IntegerField', [], {}),
            'refills_callout': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rx_count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'signature': ('django.db.models.fields.TextField', [], {}),
            'signature_callout': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pagetree.hierarchy': {
            'Meta': {'object_name': 'Hierarchy'},
            'base_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'pagetree.pageblock': {
            'Meta': {'ordering': "('section', 'ordinality')", 'object_name': 'PageBlock'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'css_extra': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ordinality': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pagetree.Section']"})
        },
        u'pagetree.section': {
            'Meta': {'object_name': 'Section'},
            'deep_toc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'hierarchy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pagetree.Hierarchy']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show_toc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['activity_prescription_writing']