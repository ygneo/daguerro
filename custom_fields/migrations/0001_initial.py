# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CustomField'
        db.create_table('custom_fields_customfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('field_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('custom_fields', ['CustomField'])

        # Adding model 'GenericCustomField'
        db.create_table('custom_fields_genericcustomfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['custom_fields.CustomField'])),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('custom_fields', ['GenericCustomField'])

        # Adding unique constraint on 'GenericCustomField', fields ['field', 'content_type', 'object_id']
        db.create_unique('custom_fields_genericcustomfield', ['field_id', 'content_type_id', 'object_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'GenericCustomField', fields ['field', 'content_type', 'object_id']
        db.delete_unique('custom_fields_genericcustomfield', ['field_id', 'content_type_id', 'object_id'])

        # Deleting model 'CustomField'
        db.delete_table('custom_fields_customfield')

        # Deleting model 'GenericCustomField'
        db.delete_table('custom_fields_genericcustomfield')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'custom_fields.customfield': {
            'Meta': {'object_name': 'CustomField'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'custom_fields.genericcustomfield': {
            'Meta': {'unique_together': "(('field', 'content_type', 'object_id'),)", 'object_name': 'GenericCustomField'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_fields.CustomField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['custom_fields']