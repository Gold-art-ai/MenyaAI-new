from src.analytics.report_gen import TeacherAnalyst
from src.ml_engine.processor import ActivityProcessor

def generate_report():
    print("[START] Teacher Insight & Analytics Generator")
    
    # In a real app, this data would come from the database / child session logs.
    student = "Gloria"
    current_activity = "Shapes"
    mock_touches = [(105, 102), (148, 155), (205, 95)]
    time_taken = 15
    lifts = 1
    
    # Calculate child's performance metrics
    target_path = [(100, 100), (150, 150), (200, 100)]
    processor = ActivityProcessor(target_path)
    metrics = processor.calculate_metrics(mock_touches, time_taken, lifts)
    
    # Generate insights
    analyst = TeacherAnalyst()
    advice = analyst.get_individual_advice(
        student, metrics["precision"], metrics["lifts"], metrics.get("jerk_index", 0.0)
    )
    
    print(f"\n==========================================")
    print(f" TEACHER REPORT CARD: {student}")
    print(f"==========================================")
    print(f" Activity: {current_activity}")
    print(f" Precision: {metrics['precision'] * 100}%")
    print(f" Smoothness Ratio: {metrics['smoothness']}")
    print(f" Dynamic Time Warping (DTW) Distance: {metrics.get('dtw_distance', 0.0)}")
    print(f" Tremor/Jerk Index: {metrics.get('jerk_index', 0.0)}")
    print(f" Time Taken: {metrics['time']} seconds")
    print(f" Hand Lifts: {metrics['lifts']}")
    print(f"------------------------------------------")
    print(f" Advice (EN): {advice['EN']}")
    print(f" Advice (RW): {advice['RW']}")
    print(f" Advice (FR): {advice['FR']}")
    print(f"==========================================\n")

if __name__ == "__main__":
    generate_report()
