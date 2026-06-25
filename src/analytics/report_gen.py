import pandas as pd
import numpy as np
import json
import os

class TeacherAnalyst:
    def __init__(self, csv_path='data/toddler_progress.csv', state_file="data/student_state.json"):
        self.csv_path = csv_path
        self.state_file = state_file
        # Load historical toddler progress dataset (class-wide context)
        if os.path.exists(csv_path):
            self.df = pd.read_csv(csv_path)
        else:
            self.df = pd.DataFrame(columns=['current_activity', 'precision', 'smoothness', 'lifts', 'time_spent', 'recommended_activity'])
        
    def generate_class_report(self):
        if self.df.empty:
            return {
                "EN": "No class data available.",
                "RW": "Nta makuru y'ishuri aboneka.",
                "FR": "Aucune donnée de classe disponible."
            }
            
        total_students = len(self.df)
        avg_precision = self.df['precision'].mean()
        struggling_kids = self.df[self.df['precision'] < 0.55]
        
        reports = {
            "EN": f"Class Overview: Average precision is {avg_precision:.2f}. "
                  f"{len(struggling_kids)} students need extra help with motor skills.",
            
            "RW": f"Igereranyo rusange: Ubuhanga bwo gushushanya buri kuri {avg_precision:.2f}. "
                  f"Abanyeshuri {len(struggling_kids)} bakeneye ubufasha bwihariye.",
            
            "FR": f"Aperçu de la classe: La précision moyenne est de {avg_precision:.2f}. "
                  f"{len(struggling_kids)} élèves ont besoin d'une aide supplémentaire."
        }
        return reports

    def get_individual_advice(self, student_name, precision, lifts, current_jerk=0.0):
        """Generates specific advice for one kid based on current metrics and historical learning trend."""
        
        # 1. Load history if available in state file
        history = []
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    if student_name in state:
                        history = state[student_name].get("history", [])
            except Exception:
                pass

        # 2. Analyze Trend using linear regression slope (if at least 3 attempts exist)
        trend_status = "stable"
        slope = 0.0
        if len(history) >= 3:
            precisions = [h.get("precision", 0.0) for h in history]
            try:
                slope = np.polyfit(range(len(precisions)), precisions, 1)[0]
                if slope > 0.05:
                    trend_status = "improving"
                elif slope < -0.05:
                    trend_status = "struggling"
            except Exception:
                pass
        
        # 3. Analyze Tremors (Jerk Index)
        # Average jerk index from last 3 records (or current_jerk if history is empty)
        jerks = [h.get("jerk_index", 0.0) for h in history[-3:] if "jerk_index" in h]
        avg_jerk = np.mean(jerks) if len(jerks) > 0 else current_jerk

        # 4. Generate Diagnostic Advice
        # Tremor / Fine Motor Delay Flag
        if avg_jerk > 5.0:
            return {
                "RW": f"Uyu mwana ({student_name}) arerekana guhinda kw'ikaramu (Tremor Index: {avg_jerk:.1f}). Mufashe gukora imyitozo yoroshye yo gutunganya imikaya.",
                "EN": f"This child ({student_name}) shows high pen tremor (Jerk Index: {avg_jerk:.1f}). Recommend finger muscle strengthening games or slower speeds.",
                "FR": f"Cet enfant ({student_name}) présente un tremblement du stylet élevé (Jerk Index : {avg_jerk:.1f}). Recommander des jeux de renforcement des doigts."
            }
        
        # Pen Lifts Alert
        if lifts > 5:
            return {
                "RW": f"Uyu mwana akunda kuzamura ikaramu kenshi (inshuro {lifts}). Mugufashe gukomeza ku rupapuro no kugabanya guhagarara.",
                "EN": f"This child lifts the pen too often ({lifts} lifts). Encourage continuous stroke drawing without lifting.",
                "FR": f"Cet enfant lève trop souvent le stylo ({lifts} levées). Encouragez des traits continus sans lever le stylo."
            }

        # Trend-based updates
        if trend_status == "improving":
            return {
                "RW": f"Uyu mwana ({student_name}) ari kwerekana iterambere ryiza cyane ry'ubuhanga! Komeza ubashishikarize.",
                "EN": f"This child ({student_name}) is showing positive progress over their last sessions! Excellent work.",
                "FR": f"Cet enfant ({student_name}) montre des progrès constants lors des dernières sessions ! Excellent travail."
            }
        elif trend_status == "struggling":
            return {
                "RW": f"Uyu mwana ({student_name}) ari guhura n'imbogamizi kuko amanota ye arimo kugabanuka. Bakeneye ubufasha bworoshye.",
                "EN": f"This child ({student_name}) seems to be struggling as performance shows a downward trend. Recommend simpler tracing exercises.",
                "FR": f"Cet enfant ({student_name}) semble en difficulté car ses performances régressent. Recommander des tracés simplifiés."
            }

        # General baseline encouragement
        return {
            "RW": "Arigukora neza ku rugero ruringaniye! Komeza umushishikarize.",
            "EN": "Doing great at a steady pace! Keep encouraging them.",
            "FR": "Progrès stables et réguliers ! Continuez à l'encourager."
        }

       