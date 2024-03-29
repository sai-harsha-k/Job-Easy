import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from core.models import Jobdetails  # Adjust the import path according to your app structure

class Command(BaseCommand):
    help = 'Import jobs from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The CSV file path')

    def handle(self, *args, **options):
        success_count = 0
        error_count = 0

        with open(options['csv_file_path'], newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Parse the job posting date from string to date object
                    job_posting_date = datetime.strptime(row['Job Posting Date'], '%Y-%m-%d').date()  # adjust the date format if it's different

                    # Ensure that model fields match CSV column names
                    Jobdetails.objects.create(
                        experience=row['Experience'],
                        qualifications=row['Qualifications'],
                        salary_range=row['Salary Range'],
                        location=row['location'],
                        country=row['Country'],
                        work_type=row['Work Type'],
                        job_posting_date=job_posting_date,
                        job_title=row['Job Title'],
                        role=row['Role'],
                        job_portal=row['Job Portal'],
                        job_description=row['Job Description'],
                        skills=row['skills'],
                        responsibilities=row['Responsibilities'],
                        company=row['Company'],
                        mbti=row['mbti']
                    )

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    self.stderr.write(self.style.ERROR(f'Error importing job: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {success_count} jobs from CSV'))
        if error_count > 0:
            self.stderr.write(self.style.WARNING(f'Failed to import {error_count} jobs from CSV'))
