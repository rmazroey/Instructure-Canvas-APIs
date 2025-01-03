import datetime
import time
import requests
import json
import csv
from pprint import pprint
from django.core.management.base import BaseCommand, CommandError
from django.SIS.models import Module
from django.canvas.models import Courses, Users, Submissions, Assignments, AssignmentGroups, Section
from django.canvas.util.logging import LogManagement
from django.settings import LMS_TEST_BASE_URL, LMS_TEST_ACCESS_TOKEN, LMS_LIVE_BASE_URL, LMS_LIVE_ACCESS_TOKEN, DIR_ARCHIVE
from django.core.util.common_functions import mod_offers_of_ayr_dict
from django.db.models import Q

class Command(BaseCommand):
    resource_type = 'Canvas API import'
    help = 'Imports data from Canvas API and updates or creates records in the database.'
    log = LogManagement(resource_type)

    def add_arguments(self, parser):
        parser.add_argument('--resource', required=True)
        parser.add_argument('--acc_id', required=True)
        parser.add_argument('--ay', required=True)
        parser.add_argument('--live_site', required=True)
        parser.add_argument('--del_existing', default='No')

    def handle(self, *args, **options):
        resource = self.validate_resource(options['resource'])
        lms_base_url, lms_access_token = self.get_lms_credentials(options['live_site'])
        truncate_table = options['del_existing'].lower() in ['yes', 'y']
        
        if truncate_table:
            self.truncate_model(resource)

        self.log.import_info(resource, 'n/a', options['acc_id'], lms_base_url, truncate_table)
        course_ids = self.get_course_ids(resource, options['ay'])

        request_headers = {'Authorization': f'Bearer {lms_access_token}'}
        self.fetch_and_process_data(resource, course_ids, lms_base_url, request_headers)

    def validate_resource(self, resource):
        valid_resources = ['Users', 'Assignments', 'Courses', 'Submissions', 'AssignmentGroups', 'Section']
        if resource not in valid_resources:
            raise CommandError(f"Invalid resource specified: {resource}")
        return resource

    def get_lms_credentials(self, live_site):
        if live_site.lower() in ['yes', 'y']:
            return LMS_LIVE_BASE_URL, LMS_LIVE_ACCESS_TOKEN
        return LMS_TEST_BASE_URL, LMS_TEST_ACCESS_TOKEN

    def truncate_model(self, resource):
        model = eval(resource)
        model.truncate()

    def get_course_ids(self, resource, ay):
        if resource in ['Assignments', 'Submissions', 'AssignmentGroups', 'Section']:
            return self.list_of_modules(mod_offers_of_ayr_dict()[ay])
        return [ay]

    def fetch_and_process_data(self, resource, course_ids, lms_base_url, request_headers):
        for course_id in course_ids:
            api_url = f"{lms_base_url}/courses/{course_id}/{resource.lower()}"
            response = requests.get(api_url, headers=request_headers)
            data = response.json()
            self.save_data(resource, data)

    def save_data(self, resource, data):
        for item in data:
            defaults = self.map_data(resource, item)
            model = eval(resource)
            model.objects.update_or_create(id=item['id'], defaults=defaults)

    def map_data(self, resource, item):
        mappings = {
            'Assignments': {
                'name': item.get('name'),
                'due_at': item.get('due_at'),
                'course_id': item.get('course_id'),
                'published': item.get('published')
            },
            'Courses': {
                'name': item.get('name'),
                'course_code': item.get('course_code'),
                'workflow_state': item.get('workflow_state')
            },
            'Users': {
                'name': item.get('name'),
                'email': item.get('email'),
                'last_login': item.get('last_login')
            }
        }
        return mappings.get(resource, {})

    def list_of_modules(self, offers_list):
        return [module.lms_id for module in Module.objects.filter(mod_offer__in=offers_list).exclude(lms_id__exact='')]
