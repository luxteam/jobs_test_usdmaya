tool_name = 'maya_usd'
report_type = 'default'
show_skipped_groups = True
tracked_metrics_files_number = 10
groups_without_time_comparision = ['CPU_Mode', 'Dual_Mode']
tracked_metrics = {
    'render_time': {'displaying_name': 'Render time', 'function': 'sum', 'displaying_unit': 's'}
}
tracked_metrics_charts_location = 'performance'
tracked_metrics_files_number = 10000
analyze_render_time = {"max_diff": 0.05} 