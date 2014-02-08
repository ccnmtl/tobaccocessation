# flake8: noqa
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Patient.gender'
        db.add_column(u'activity_virtual_patient_patient', 'gender',
                      self.gf('django.db.models.fields.CharField')(default='F', max_length=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Patient.gender'
        db.delete_column(u'activity_virtual_patient_patient', 'gender')


    models = {
        u'activity_virtual_patient.activitystate': {
            'Meta': {'object_name': 'ActivityState'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'virtual_patient_user'", 'unique': 'True', 'to': u"orm['auth.User']"})
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
            'gender': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1'}),
            'history': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'activity_virtual_patient.patientassessmentblock': {
            'Meta': {'object_name': 'PatientAssessmentBlock'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'patient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['activity_virtual_patient.Patient']"}),
            'view': ('django.db.models.fields.IntegerField', [], {})
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

    complete_apps = ['activity_virtual_patient']