"""
analytics.py - Task analytics using Pandas & NumPy
"""
import pandas as pd
import numpy as np


def get_analytics(tasks: list) -> dict:
    """
    Accept a list of task dicts and return analytics summary.
    Uses Pandas for data manipulation and NumPy for calculations.
    """
    if not tasks:
        return {
            'total_tasks':          0,
            'completed_tasks':      0,
            'pending_tasks':        0,
            'in_progress_tasks':    0,
            'completion_percentage': 0.0,
            'priority_breakdown':   {'low': 0, 'medium': 0, 'high': 0},
            'status_breakdown':     {'pending': 0, 'in_progress': 0, 'completed': 0},
            'avg_tasks_per_day':    0.0,
        }

    # ── Build DataFrame ──────────────────────────────────────────
    df = pd.DataFrame(tasks)
    df['created_at'] = pd.to_datetime(df['created_at'])

    # ── Basic Counts ─────────────────────────────────────────────
    total_tasks       = len(df)
    completed_tasks   = int((df['status'] == 'completed').sum())
    pending_tasks     = int((df['status'] == 'pending').sum())
    in_progress_tasks = int((df['status'] == 'in_progress').sum())

    # ── NumPy: completion percentage ─────────────────────────────
    completion_percentage = float(np.round((completed_tasks / total_tasks) * 100, 2))

    # ── Priority breakdown using value_counts ─────────────────────
    priority_counts = df['priority'].value_counts().to_dict()
    priority_breakdown = {
        'low':    int(priority_counts.get('low', 0)),
        'medium': int(priority_counts.get('medium', 0)),
        'high':   int(priority_counts.get('high', 0)),
    }

    # ── Status breakdown ─────────────────────────────────────────
    status_counts = df['status'].value_counts().to_dict()
    status_breakdown = {
        'pending':     int(status_counts.get('pending', 0)),
        'in_progress': int(status_counts.get('in_progress', 0)),
        'completed':   int(status_counts.get('completed', 0)),
    }

    # ── Average tasks created per unique day ─────────────────────
    tasks_per_day = df.groupby(df['created_at'].dt.date).size()
    avg_tasks_per_day = float(np.round(tasks_per_day.mean(), 2))

    return {
        'total_tasks':           total_tasks,
        'completed_tasks':       completed_tasks,
        'pending_tasks':         pending_tasks,
        'in_progress_tasks':     in_progress_tasks,
        'completion_percentage': completion_percentage,
        'priority_breakdown':    priority_breakdown,
        'status_breakdown':      status_breakdown,
        'avg_tasks_per_day':     avg_tasks_per_day,
    }
