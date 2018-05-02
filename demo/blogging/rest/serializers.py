'''
Created on 15-Mar-2018

@author: anshul
'''

from blogging.models import Content, Policy
from rest_framework import serializers

from django.contrib.auth.models import User
from rest_framework.serializers import (HyperlinkedRelatedField,CharField)
from blogging.settings import blog_settings
from django.db import transaction

class ContentSerializer(serializers.HyperlinkedModelSerializer):
    author = HyperlinkedRelatedField(queryset=User.objects.all(), 
                                     view_name='user-detail',
                                     required = False)
    data = CharField(style={'base_template': 'textarea.html'}, required=False)
    class Meta:
        model = Content
        fields = ('url', 'id', 'title', 'data', 'author', 
                  'create_date', 'last_modified')
        extra_kwargs = {'title': {'max_length': 100,
                                  'required': False},
                        }

    def is_valid(self):
        if (serializers.HyperlinkedModelSerializer.is_valid(self)):
            #If some field is not posted, it is missing in the dictionary
            #Unlike forms where it is empty
            if self._validated_data.get('title',None) is None \
               and self._validated_data.get('data', None) is None:
                self.errors['detail'] = ['Either title or content must be non-empty']
                return False
            return True
        return False

if blog_settings.USE_POLICY:
    class PolicySerializer(serializers.ModelSerializer):
        class Meta:
            model = Policy
            fields = ('id', 'entry', 'policy', 'start', 'end')
            extra_kwargs = {'start': {'required': False},
                            'end': {'required': False},
                            'entry': {'required': False}}
    
    class ManageSerializer(ContentSerializer):
        policy = PolicySerializer(many=True)
        
        class Meta:
            model = Content
            fields = ('url', 'id', 'title', 'data', 'author', 'create_date', 
                      'last_modified', 'policy')
            extra_kwargs = {'url': {'view_name':'content/manage-detail'}}
            
        def create(self, validated_data):
            policy_data = validated_data.pop('policy')
            with transaction.atomic():
                entry = Content.objects.create(**validated_data)
                for policy in policy_data:
                    Policy.objects.create(entry=entry, **policy)
            return entry
        
        def update(self, instance, validated_data):
            policy_data = validated_data.pop('policy')
            instance.title = validated_data.get('title', instance.title)
            instance.data = validated_data.get('data', instance.data)
            with transaction.atomic():
                instance.save()
                for policy_entry in policy_data:
                    policy = instance.policy.get(policy=policy_entry.get('policy'))
                    policy.start = policy_entry.get('start', policy.start)
                    policy.end = policy_entry.get('end', policy.end)
                    policy.save()
            return instance
else:
    class ManageSerializer(ContentSerializer):
        class Meta:
            model = Content
            fields = ('url','id', 'title', 'data', 'author', 'create_date', 
                      'last_modified', 'is_active')
            extra_kwargs = {'url': {'view_name':'content/manage-detail'}}