import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from core.models import Jobdetails  # Adjust the import path according to your app structure

class Command(BaseCommand):
    help = 'Import jobs from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The CSV file path')

    def handle(self, *args, **options):
        with open(options['csv_file_path'], newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Parse the job posting date from string to date object
                job_posting_date = datetime.strptime(row['Job Posting Date'], '%Y-%m-%d').date()  # adjust the date format if it's different

                Jobdetails.objects.create(
                    experience=row['Experience'],
                    qualifications=row['Qualifications'],
                    salary_range=row['Salary Range'],
                    location=row['location'],  # Ensure this matches the CSV column name exactly
                    country=row['Country'],
                    work_type=row['Work Type'],
                    job_posting_date=job_posting_date,  # Use the parsed date
                    job_title=row['Job Title'],
                    role=row['Role'],
                    job_portal=row['Job Portal'],
                    job_description=row['Job Description'],
                    skills=row['skills'],  # Ensure this matches the CSV column name exactly
                    responsibilities=row['Responsibilities'],
                    company=row['Company'],
                    mbti=row['mbti']  # Ensure this matches the CSV column name exactly
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported jobs from CSV'))
