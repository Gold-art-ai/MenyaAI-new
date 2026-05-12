import pandas as pd
class TeacherAnalyst:
    def __init__(self, csv_path='data/toddler_progress.csv'):
        self.df= pd.read_csv(csv_path)
        
    def generate_class_report(self):
        total_students = len(self.df)
        avg_