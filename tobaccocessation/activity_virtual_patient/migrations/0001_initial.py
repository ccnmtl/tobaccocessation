# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Medication'
        db.create_table(u'activity_virtual_patient_medication', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('instructions', self.gf('django.db.models.fields.TextField')()),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('rx_count', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['Medication'])

        # Adding model 'ConcentrationChoice'
        db.create_table(u'activity_virtual_patient_concentrationchoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('medication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.Medication'])),
            ('concentration', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['ConcentrationChoice'])

        # Adding model 'DosageChoice'
        db.create_table(u'activity_virtual_patient_dosagechoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('medication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.Medication'])),
            ('dosage', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['DosageChoice'])

        # Adding model 'RefillChoice'
        db.create_table(u'activity_virtual_patient_refillchoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('medication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.Medication'])),
            ('refill', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['RefillChoice'])

        # Adding model 'Patient'
        db.create_table(u'activity_virtual_patient_patient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('history', self.gf('django.db.models.fields.TextField')()),
            ('display_order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['Patient'])

        # Adding model 'TreatmentClassification'
        db.create_table(u'activity_virtual_patient_treatmentclassification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['TreatmentClassification'])

        # Adding model 'TreatmentOption'
        db.create_table(u'activity_virtual_patient_treatmentoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.Patient'])),
            ('classification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.TreatmentClassification'])),
            ('medication_one', self.gf('django.db.models.fields.related.ForeignKey')(related_name='medication_one', to=orm['activity_virtual_patient.Medication'])),
            ('medication_two', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='medication_two', null=True, to=orm['activity_virtual_patient.Medication'])),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['TreatmentOption'])

        # Adding model 'TreatmentOptionReasoning'
        db.create_table(u'activity_virtual_patient_treatmentoptionreasoning', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.Patient'])),
            ('classification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.TreatmentClassification'])),
            ('medication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.Medication'], null=True, blank=True)),
            ('combination', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reasoning', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['TreatmentOptionReasoning'])

        # Adding model 'TreatmentFeedback'
        db.create_table(u'activity_virtual_patient_treatmentfeedback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('patient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.Patient'])),
            ('classification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activity_virtual_patient.TreatmentClassification'])),
            ('correct_dosage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('combination_therapy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('feedback', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['TreatmentFeedback'])

        # Adding model 'ActivityState'
        db.create_table(u'activity_virtual_patient_activitystate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='virtual_patient_user', to=orm['auth.User'])),
            ('json', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'activity_virtual_patient', ['ActivityState'])


    def backwards(self, orm):
        # Deleting model 'Medication'
        db.delete_table(u'activity_virtual_patient_medication')

        # Deleting model 'ConcentrationChoice'
        db.delete_table(u'activity_virtual_patient_concentrationchoice')

        # Deleting model 'DosageChoice'
        db.delete_table(u'activity_virtual_patient_dosagechoice')

        # Deleting model 'RefillChoice'
        db.delete_table(u'activity_virtual_patient_refillchoice')

        # Deleting model 'Patient'
        db.delete_table(u'activity_virtual_patient_patient')

        # Deleting model 'TreatmentClassification'
        db.delete_table(u'activity_virtual_patient_treatmentclassification')

        # Deleting model 'TreatmentOption'
        db.delete_table(u'activity_virtual_patient_treatmentoption')

        # Deleting model 'TreatmentOptionReasoning'
        db.delete_table(u'activity_virtual_patient_treatmentoptionreasoning')

        # Deleting model 'TreatmentFeedback'
        db.delete_table(u'activity_virtual_patient_treatmentfeedback')

        # Deleting model 'ActivityState'
        db.delete_table(u'activity_virtual_patient_activitystate')


    models = {
        u'activity_virtual_patient.activitystate': {
            'Meta': {'object_name': 'ActivityState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'virtual_patient_user'", 'to': u"orm['auth.User']"})
        },
        u'activity_virtual_patient.concentrationchoice': {
            'Meta': {'object_name': 'ConcentrationChoice'},
            'concentration': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medication': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.Medication']"})
        },
        u'activity_virtual_patient.dosagechoice': {
            'Meta': {'object_name': 'DosageChoice'},
            'correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'dosage': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medication': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.Medication']"})
        },
        u'activity_virtual_patient.medication': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'Medication'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'rx_count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'activity_virtual_patient.patient': {
            'Meta': {'object_name': 'Patient'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'history': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'activity_virtual_patient.refillchoice': {
            'Meta': {'object_name': 'RefillChoice'},
            'correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medication': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.Medication']"}),
            'refill': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'activity_virtual_patient.treatmentclassification': {
            'Meta': {'object_name': 'TreatmentClassification'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        u'activity_virtual_patient.treatmentfeedback': {
            'Meta': {'object_name': 'TreatmentFeedback'},
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.TreatmentClassification']"}),
            'combination_therapy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'correct_dosage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'feedback': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.Patient']"})
        },
        u'activity_virtual_patient.treatmentoption': {
            'Meta': {'object_name': 'TreatmentOption'},
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.TreatmentClassification']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medication_one': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'medication_one'", 'to': u"orm['activity_virtual_patient.Medication']"}),
            'medication_two': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'medication_two'", 'null': 'True', 'to': u"orm['activity_virtual_patient.Medication']"}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.Patient']"})
        },
        u'activity_virtual_patient.treatmentoptionreasoning': {
            'Meta': {'object_name': 'TreatmentOptionReasoning'},
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.TreatmentClassification']"}),
            'combination': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medication': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.Medication']", 'null': 'True', 'blank': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.Patient']"}),
            'reasoning': ('django.db.models.fields.TextField', [], {})
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
        }
    }

    complete_apps = ['activity_virtual_patient']