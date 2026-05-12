import pandas as pd
class TeacherAnalyst:
    def __init__(self, csv_path='data/toddler_progress.csv'):
        self.df= pd.read_csv(csv_path)
        
    def generate_class_report(self):
        total_students = len(self.df)
        avg_precision = self.df['precision'].mean()
        struggling_kids = self.df[self.df['precision'] < 0.55]
        star_kids = self.df[self.df['precision']>0.90]
        
        reports = {
            "EN": f"Class Overview: Average precision is {avg_precision:.2f}. "
                  f"{len(struggling_kids)} students need extra help with motor skills.",
            
            "RW": f"Igereranyo rusange: Ubuhanga bwo gushushanya buri kuri {avg_precision:.2f}. "
                  f"Abanyeshuri {len(struggling_kids)} bakeneye ubufasha bwihariye.",
            
            "FR": f"Aperçu de la classe: La précision moyenne est de {avg_precision:.2f}. "
               
                  f"{len(struggling_kids)} élèves ont besoin d'une aide supplémentaire."
        }
        return reports
    def get_individual_advice(self)