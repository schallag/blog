'''
Created on 14-Mar-2018

@author: anshul
'''
from django.test import TestCase

from blogging import views, models
from blogging.forms import ContentForm, TemplateForm

from django.contrib.auth.models import User

from django.test.client import RequestFactory, Client

from django.urls import resolve

from unittest import skip
from django.shortcuts import render

from blogging.settings import blog_settings

class BaseTest(TestCase):
    def _create_post(self, title, text, author=None):
        return models.Content.objects.create(title=title, 
                                             text=text, 
                                             author=author if author is not None else self.user)
        
    def _create_policy(self, content, policy, start=None, stop=None):
        return models.Policy.objects.create(entry=content, 
                                            policy=policy,
                                            start = start,
                                            end = stop)
        
    def setUp(self):
        #Use request factory to test views without behaving like a browser
        self.factory = RequestFactory()
        self.password = 'secret'
        self.user = User.objects.create_user(username="tester",
                                           email="tester@testing.co",
                                           password=self.password)
        self.client = Client()
        TestCase.setUp(self)
        print("In method", self._testMethodName)

    def tearDown(self):
        TestCase.tearDown(self)

from django.http import HttpRequest
class IndexView(BaseTest):
    def test_resolve_index_page(self):
        found = resolve("/blogging/")
        self.assertEqual(found.func, views.index, "Could not find view")
        
    def test_template_used(self):
        self.client.login(username=self.user.username, 
                          password=self.password)
        response = self.client.get('/blogging/')
        self.assertTemplateUsed(response, 'blogging/index.html')

    def test_no_content_message_returned(self):
        request = HttpRequest()
        response = views.index(request)
        self.assertContains(response=response, 
                            text="No posts have been created yet. Start writing!", 
                            count=1,
                            status_code=200)
        
    def test_client_no_content_message_returned(self):
        c = Client()
        response = c.get('/blogging/')
        self.assertContains(response=response, 
                            text="No posts have been created yet. Start writing!", 
                            count=1,
                            status_code=200)

    def test_get_non_empty_content_list(self):
        from django.utils import timezone
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        policy_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2")
        policy_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        request = HttpRequest()
        response = views.index(request)
        
        self.assertContains(response=response, 
                            text="Post 1", 
                            count=1,
                            status_code=200)
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)

        
class PolicyTests(BaseTest):
    def test_get_1_published_1_non_published_content_list(self):
        from django.utils import timezone
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        policy_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2")
        policy_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=None, 
                                     stop=None)
        request = HttpRequest()
        response = views.index(request)
        
        self.assertContains(response=response, 
                            text="Post 1", 
                            count=1,
                            status_code=200)
        self.assertNotContains(response, text='Post 2', status_code=200)

    def test_get_with_author_filter(self):
        from django.utils import timezone
        user = User.objects.create_user(username="tester2",
                                           email="tester2@testing.co",
                                           password=self.password)
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        policy_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2",
                                    author = user)
        policy_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        
        request = HttpRequest()
        request.GET['author']= 'tester2'
        response = views.index(request)
        
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)
        self.assertNotContains(response, text='Post 1', status_code=200)

    def test_get_pinned_posts(self):
        from django.utils import timezone
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        publish_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        pin_1 = self._create_policy(entry_1, 
                                     models.Policy.PIN, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2")
        publish_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        request = HttpRequest()
        request.GET['pinned']= ''
        response = views.index(request)
        
        self.assertContains(response=response, 
                            text="Post 1", 
                            count=1,
                            status_code=200)
        self.assertNotContains(response=response, 
                               text="Post 2", 
                               status_code=200)
    
    @skip('Not applicable for now')
    def test_get_published_with_pinned_has_no_repetitions(self):
        from django.utils import timezone
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2")
        publish_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        publish_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        pin_1 = self._create_policy(entry_1, 
                                     models.Policy.PIN, 
                                     start=timezone.now(), 
                                     stop=None)
        request = HttpRequest()
        response = views.index(request)
        print(response.content)
        
class ManageView(BaseTest):
    #This view actually should not be visible without login
    #And later, must be filtered by author
    def test_resolve_index_page(self):
        found = resolve("/blogging/manage/")
        self.assertEqual(found.func, views.manage_content, "Could not find view")

    def test_template_used(self):
        self.client.login(username=self.user.username, 
                          password=self.password)
        response = self.client.get('/blogging/manage/')
        self.assertTemplateUsed(response, 'blogging/list.html')

    def redirect_to_login_page_on_access(self):
        #Not currently interested in login page url
        request = HttpRequest()
        response = views.manage_content(request)
        self.assertContains(response=response, 
                            text="", 
                            count=0,
                            status_code=302)
        
    def test_no_content_message_returned(self):
        request = HttpRequest()
        request.user = self.user
        response = views.index(request)
        self.assertContains(response=response, 
                            text="No posts have been created yet. Start writing!", 
                            count=1,
                            status_code=200)

    def test_client_no_content_message_returned(self):
        self.client.login(username=self.user.username, 
                          password=self.password)
        response = self.client.get('/blogging/manage/')
        self.assertContains(response=response, 
                            text="No posts have been created yet. Start writing!", 
                            count=1,
                            status_code=200)

    def test_get_non_empty_content_list(self):
        self._create_post(title="Post 1", text="This is post number 1")
        self._create_post(title="Post 2", text="This is post number 2")
        request = HttpRequest()
        request.user = self.user
        response = views.manage_content(request)
        
        self.assertContains(response=response, 
                            text="Post 1", 
                            count=1,
                            status_code=200)
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)
        
    def test_get_with_author_filter(self):
        from django.utils import timezone
        user = User.objects.create_user(username="tester2",
                                           email="tester2@testing.co",
                                           password=self.password)
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        policy_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2",
                                    author = user)
        policy_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        
        request = HttpRequest()
        request.GET['author']= 'tester2'
        request.user = self.user
        response = views.manage_content(request)
        
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)
        self.assertNotContains(response, text='Post 1', status_code=200)
        
    def test_get_with_draft_filter(self):
        from django.utils import timezone
        user = User.objects.create_user(username="tester2",
                                           email="tester2@testing.co",
                                           password=self.password)
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        policy_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2",
                                    author = user)
        policy_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=None, 
                                     stop=None)
        
        request = HttpRequest()
        request.GET['drafts']= ''
        request.user = self.user
        response = views.manage_content(request)
        
        self.assertNotContains(response, text='Post 1', status_code=200)
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)
        
        
    def test_get_with_author_and_draft_filter(self):
        from django.utils import timezone
        user = User.objects.create_user(username="tester2",
                                           email="tester2@testing.co",
                                           password=self.password)
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        policy_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2",
                                    author = user)
        policy_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=None, 
                                     stop=None)
        entry_3 = self._create_post(title="Post 3", 
                                    text="This is post number 3")
        policy_3 = self._create_policy(entry_3, 
                                     models.Policy.PUBLISH, 
                                     start=None, 
                                     stop=None)
                
        request = HttpRequest()
        request.GET['author']= 'tester2'
        request.GET['drafts']= ''
        request.user = self.user
        response = views.manage_content(request)
        
        self.assertNotContains(response, text='Post 1', status_code=200)
        self.assertNotContains(response, text='Post 3', status_code=200)
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)
        

    def test_get_with_published_filter(self):
        from django.utils import timezone
        user = User.objects.create_user(username="tester2",
                                           email="tester2@testing.co",
                                           password=self.password)
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        policy_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2",
                                    author = user)
        policy_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_3 = self._create_post(title="Post 3", 
                                    text="This is post number 3")
        
        request = HttpRequest()
        request.GET['published']= ''
        request.user = self.user
        response = views.manage_content(request)
        
        self.assertContains(response=response, 
                            text="Post 1", 
                            count=1,
                            status_code=200)
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)
        self.assertNotContains(response, text='Post 3', status_code=200)
        
    def test_get_with_author_and_published_filter(self):
        from django.utils import timezone
        user = User.objects.create_user(username="tester2",
                                           email="tester2@testing.co",
                                           password=self.password)
        entry_1 = self._create_post(title="Post 1", 
                                    text="This is post number 1")
        policy_1 = self._create_policy(entry_1, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_2 = self._create_post(title="Post 2", 
                                    text="This is post number 2",
                                    author = user)
        policy_2 = self._create_policy(entry_2, 
                                     models.Policy.PUBLISH, 
                                     start=timezone.now(), 
                                     stop=None)
        entry_3 = self._create_post(title="Post 3", 
                                    text="This is post number 3")
        
        request = HttpRequest()
        request.GET['author']= 'tester2'
        request.GET['published']= ''
        request.user = self.user
        response = views.manage_content(request)
        
        self.assertNotContains(response, text='Post 1', status_code=200)
        self.assertContains(response=response, 
                            text="Post 2", 
                            count=1,
                            status_code=200)
        self.assertNotContains(response, text='Post 3', status_code=200)

class DetailView(BaseTest):
    def test_resolve_detail_blog_page(self):
        found = resolve("/blogging/1/")
        self.assertEqual(found.func, views.detail, "Could not find view")
        
    def test_get_invalid_blog_id(self):
        from django.http import Http404
        request = HttpRequest()
        self.assertRaises(Http404, views.detail, request, blog_id=1)
        
    def test_get_valid_detail_page(self):
        obj = self._create_post(title="Post 1", text="This is post number 1")
#         html="<div>"+\
#              "<h1>Post 1</h1>"+\
#              "<div><span>Created on "+ obj.create_date.strftime("%B %d, %Y, %-H:%M %p")+\
#              " by "+ obj.author.username.title() +"</span></div>"+\
#              "<p>This is post number 1</p></div>"
        request = HttpRequest()
        response = views.detail(request, blog_id=1)
        #print (response.content)
        self.assertContains(response=response, 
                            text="This is post number 1",
                            #text= html, 
                            count=1, 
                            status_code=200, 
                            html=True)

from django.urls import reverse

class EditView(BaseTest):
    def test_resolve_edit_page(self):
        found = resolve('/blogging/edit/')
        self.assertEqual(found.func.__name__, 
                         views.EditView.as_view().__name__, 
                         "The views are dissimilar")
    
    def test_template_used(self):
        self.client.login(username=self.user.username, 
                          password=self.password)
        response = self.client.get('/blogging/edit/')
        self.assertTemplateUsed(response, 'blogging/edit.html')
        
    def test_form_class(self):
        self.client.login(username=self.user.username, 
                          password=self.password)
        response = self.client.get('/blogging/edit/')
        self.assertIsInstance(response.context['entry'], 
                              ContentForm, 
                              "The two forms are not the same types")
    
    def test_get_without_login_gives_error(self):
        response = self.client.get('/blogging/edit/')
        #It redirects to login page instead of giving a permissions error
        self.assertContains(response,
                            text='Error',
                            count=0, 
                            status_code=302)
    
    def test_post_without_login_gives_error(self):
        response = self.client.post('/blogging/edit/',
                                    data={'title':"This is a test post",
                                          'text': 'These are the post contents',
                                          'Save':'Save',
                                          }) #Follow redirect
        #It redirects to login page instead of giving a permissions error
        self.assertContains(response,
                            text='Error',
                            count=0, 
                            status_code=302)
    
    def test_post_with_save_redirects_to_filled_form(self):
        self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
        response = self.client.post('/blogging/edit/',
                                    data={'title':"This is a test post",
                                          'text': 'These are the post contents',
                                          'Save':'Save',
                                          },
                                    follow=True) #Follow redirect
        self.assertRedirects(response, 
                             expected_url= reverse('blogging:edit', 
                                                   kwargs={'blog_id':1}), 
                             status_code=302, 
                             target_status_code=200,
                             fetch_redirect_response=True)
        self.assertContains(response,
                            text='This is a test post',
                            count=1, 
                            status_code=200)
    
    def test_post_with_publish_redirects_to_detail(self):
        self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
        response = self.client.post('/blogging/edit/',
                                    data={'title':"This is a test post",
                                          'text': 'These are the post contents',
                                          'Publish':'Publish',
                                          },
                                    follow=True) #Follow redirect

        self.assertRedirects(response, 
                             expected_url= reverse('blogging:detail', 
                                                   kwargs={'blog_id':1}), 
                             status_code=302, 
                             target_status_code=200,
                             fetch_redirect_response=True)
        self.assertContains(response,
                            text='This is a test post',
                            count=1, 
                            status_code=200,
                            html=True)
        
    def test_get_already_created_post_form(self):
        obj = self._create_post(title="Post Edit 1", text="Content of post 1")
        self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
        response = self.client.get('/blogging/{blog}/edit/'.format(blog=obj.id))
        self.assertContains(response, 
                            text="Post Edit 1", 
                            count=1, 
                            status_code=200, 
                            html=False)
        self.assertContains(response, 
                            text="Content of post 1", 
                            count=1, 
                            status_code=200, 
                            html=False)

    def test_edit_already_created_post(self):
        obj = self._create_post(title="Post Edit 1", text="Content of post 1")
        self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
        response = self.client.post('/blogging/{blog}/edit/'.format(blog=obj.id),
                                    data={'title':"Altered title",
                                          'text': 'Altered data',
                                          'Save': 'Save'},
                                          follow = True)
        self.assertNotContains(response, 
                               text="Post Edit 1", 
                               status_code=200)
        self.assertNotContains(response, 
                               text="Content of post 1", 
                               status_code=200)
        self.assertContains(response, 
                            text="Altered title", 
                            count=1, 
                            status_code=200, 
                            html=False)
        self.assertContains(response, 
                            text="Altered data", 
                            count=1, 
                            status_code=200, 
                            html=False)
        
    def test_delete_post(self):
        obj = self._create_post(title="Post Edit 1", text="Content of post 1")
        self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
        response = self.client.post('/blogging/1/edit/', 
                                    data={'Delete':'Delete'})
        self.assertRedirects(response, 
                             expected_url='/blogging/', 
                             status_code=302, 
                             target_status_code=200)
        
    def test_post_without_title_or_content_redirects(self):
        self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
        response = self.client.post('/blogging/edit/',
                                    data={'title':'',
                                          'text': '',
                                          'Publish':'Publish',
                                          },
                                    follow=True) #Follow redirect
        self.assertContains(response, 
                            text="Either title or content must be non-empty", 
                            count=1, 
                            status_code=400)
    
    def test_post_without_title_with_text(self):
        self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
        response = self.client.post('/blogging/edit/',
                                    data={'title':'',
                                          'text': 'Some data is present',
                                          'Publish':'Publish',
                                          },
                                    follow=True) #Follow redirect
        self.assertContains(response, 
                            text="Some data", 
                            count=2, 
                            status_code=200)
        
    def test_post_with_title_without_text(self):
        self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
        response = self.client.post('/blogging/edit/',
                                    data={'title':'Contains title',
                                          'text': '',
                                          'Publish':'Publish',
                                          },
                                    follow=True) #Follow redirect
        self.assertContains(response, 
                            text="Contains title", 
                            count=1, 
                            status_code=200)
        
if blog_settings.USE_TEMPLATES:
    from blogging.factory import CreateTemplate
    from blogging.models import Template
    import os
    import json
    
    class TestTemplates(BaseTest):
        
        def tearDown(self):
            BaseTest.tearDown(self)
            
            if(CreateTemplate.file_exists('Blogging')):
                #pass
                os.remove(CreateTemplate.get_full_file_path(
                                    CreateTemplate.get_file_name("Blogging")))

        def test_resolve_edit_page(self):
            found = resolve('/blogging/template/edit/')
            self.assertEqual(found.func.__name__, 
                             views.TemplateView.as_view().__name__, 
                             "The views are dissimilar")
        
        def test_template_used(self):
            self.client.login(username=self.user.username, 
                              password=self.password)
            response = self.client.get('/blogging/template/edit/')
            self.assertTemplateUsed(response, 'blogging/template.html')
            
        def test_form_class(self):
            self.client.login(username=self.user.username, 
                              password=self.password)
            response = self.client.get('/blogging/template/edit/')
            self.assertIsInstance(response.context['template'], 
                                  TemplateForm, 
                                  "The two forms are not the same types")
            
        def test_create_new_template(self):
            self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
            
            name = 'Blogging'
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                'extra': None
                                }
                       },
                      ]
            
            response = self.client.post('/blogging/template/edit/', 
                                        data={'name':name,
                                         'fields': json.dumps(layout),
                                         },
                                        follow = True)
            self.assertRedirects(response, 
                             expected_url= reverse('blogging:template', 
                                                   kwargs={'template_id':1}), 
                             status_code=302, 
                             target_status_code=200,
                             fetch_redirect_response=True)
            
            qs = Template.objects.all()
            
            self.assertEqual(qs.count(), 1, "One DB entry must exist")
            
            for obj in qs:
                self.assertEqual(obj.name, name, "Improper name saved in DB")
            
            os.remove(CreateTemplate.get_full_file_path(CreateTemplate.get_file_name(name)))

        def test_edit_existing_template(self):
            self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
            name = 'Blogging'
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                'extra': None
                                }
                       },
                      ]
            
            response = self.client.post('/blogging/template/edit/', 
                                        data={'name':name,
                                         'fields': json.dumps(layout),
                                         },
                                        follow = True)
            self.assertRedirects(response, 
                             expected_url= reverse('blogging:template', 
                                                   kwargs={'template_id':1}), 
                             status_code=302, 
                             target_status_code=200,
                             fetch_redirect_response=True)
            
            qs = Template.objects.all()
            
            self.assertEqual(qs.count(), 1, "One DB entry must exist")
            
            for obj in qs:
                self.assertEqual(obj.name, name, "Improper name saved in DB")
                
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                'extra': None
                                }
                       },
                      {'another' : {'type': 'TextField',
                                'extra': None
                                }
                       },
                      ]
            
            response = self.client.post('/blogging/template/'+str(obj.id)+'/edit/', 
                                        data={'name':name,
                                         'fields': json.dumps(layout),
                                         },
                                        follow = True)
            self.assertRedirects(response, 
                             expected_url= reverse('blogging:template', 
                                                   kwargs={'template_id':1}), 
                             status_code=302, 
                             target_status_code=200,
                             fetch_redirect_response=True)
            
            qs = Template.objects.all()
            
            self.assertEqual(qs.count(), 1, "One DB entry must exist")
            
            for obj in qs:
                self.assertEqual(obj.name, name, "Improper name saved in DB")
                
            os.remove(CreateTemplate.get_full_file_path(CreateTemplate.get_file_name(name)))

        def test_create_duplicate_template_fails(self):
            self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
            
            name = 'Blogging'
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}}]
            
            response = self.client.post('/blogging/template/edit/', 
                                        data={'name':name,
                                              'fields': json.dumps(layout),
                                              })
            
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                                 {'body' : {'type': 'TextField',
                                            'extra': None
                                            }
                                  }]
            
            response = self.client.post('/blogging/template/edit/', 
                                        data={'name':'blogging',
                                         'fields': json.dumps(layout),
                                         })
            self.assertContains(response,
                                text='OK',
                                count=0,
                                status_code=400)
            qs = Template.objects.all()
            
            self.assertEqual(qs.count(), 1, "Only one DB entry must exist")
            
            for obj in qs:
                self.assertEqual(obj.name, 
                                    name, "Improper name saved in DB")
                
            os.remove(CreateTemplate.get_full_file_path(
                                     CreateTemplate.get_file_name(name)))
            
        
        def test_get_template_form(self):
            self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
            
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                 'extra': None
                                 }
                       }]
            
            name = 'Blogging'
            self.client.post('/blogging/template/edit/', 
                                        data={'name':name,
                                         'fields': json.dumps(layout),
                                         })
            response = self.client.get('/blogging/edit/?template=Blogging')
            #TODO Do some checks if the body contains the 'Body' field
            #print(response.content)
            
            os.remove(CreateTemplate.get_full_file_path(
                                     CreateTemplate.get_file_name(name)))


        def test_create_entry_with_template(self):
            self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
            
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                 'extra': None
                                 }
                       }]
            
            name = 'Blogging'
            self.client.post('/blogging/template/edit/', 
                                        data={'name':name,
                                         'fields': json.dumps(layout),
                                         })
            module_name = 'blogging.custom.'+\
                                    CreateTemplate.get_file_name(name)
            
            #Created. Now load
            from importlib import import_module
            module = import_module(module_name)
            
            form_name = CreateTemplate.get_form_name(name)
            form = getattr(module, form_name)
            
            #Loaded, now try to create
            form_obj = form(data={'title': 'Test Post',
                            'body': 'This is a test post!',
                            'policy': [{'policy': 'PUB'}]},
                            initial={'author': self.user})
            
            if form_obj.is_valid():
                obj = form_obj.save(commit=False)
                obj.author = self.user
                obj.save()
            else:
                print('Not valid')
            print(form_obj.errors)
            
            mod_obj = models.Content.objects.get(id=1)
            #print(json.loads(mod_obj.text))
            #mod_obj = model.objects.get(id=1)
            self.assertNotEqual(mod_obj, None, "No object returned")
            os.remove(CreateTemplate.get_full_file_path(
                                    CreateTemplate.get_file_name(name)))
        
        def test_create_entry_with_template_from_client(self):
            self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
            
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                 'extra': None
                                 }
                       }]
            
            name = 'Blogging'
            self.client.post('/blogging/template/edit/', 
                                        {'name':name,
                                         'fields': json.dumps(layout),
                                         })
            module_name = 'blogging.custom.'+\
                                    CreateTemplate.get_file_name(name)
            
            response = self.client.post('/blogging/edit/', 
                                         data={'title':'Test Post',
                                               'body': 'Data in test post',
                                               'template': 1,
                                               'Save': 'Save'},
                                         follow = True)
            
            #print(response.content)
            self.assertContains(response,
                                text='OK',
                                count=0,
                                status_code=200)
            
            obj = models.Content.objects.get(id=1)
            self.assertNotEqual(obj, None, "No valid object returned.")

            os.remove(CreateTemplate.get_full_file_path(
                                    CreateTemplate.get_file_name(name)))

        def test_fetch_entry_for_editing(self):
            self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
            
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                 'extra': None
                                 }
                       }]
            
            name = 'Blogging'
            self.client.post('/blogging/template/edit/', 
                                        {'name':name,
                                         'fields': json.dumps(layout),
                                         })
            
            self.client.post('/blogging/edit/', 
                            data= {'title':'Test Post',
                                 'body': 'Data in test post',
                                 'template': 1,
                                 })
            
            response = self.client.get('/blogging/1/edit/')
            
            #print(response.content)
            
            os.remove(CreateTemplate.get_full_file_path(
                                    CreateTemplate.get_file_name(name)))
            
        def test_edit_entry(self):
            self.assertTrue(self.client.login(username=self.user.username, 
                                          password=self.password),
                                          "Login not successful")
            
            layout = [{'title': {'type': 'CharField',
                                     'extra': {'max_length': 100}}},
                      {'body' : {'type': 'TextField',
                                 'extra': None
                                 }
                       }]
            
            name = 'Blogging'
            self.client.post('/blogging/template/edit/', 
                                        {'name':name,
                                         'fields': json.dumps(layout),
                                         })

            self.client.post('/blogging/edit/', 
                                {'title':'Test Post',
                                 'body': 'Data in test post',
                                 'template': 1,
                                 })
            
            #response = self.client.get('/blogging/1/edit/')
            
            response = self.client.post('/blogging/1/edit/', 
                                data={'title':'Test Post Edit',
                                     'body': 'Edited text',
                                     'template': 1,
                                     })
            
            response = self.client.get('/blogging/1/edit/')
            
            #print(response.content)
            os.remove(CreateTemplate.get_full_file_path(
                                    CreateTemplate.get_file_name(name)))
            
        def test_edit_entry_with_deleted_template(self):
            pass