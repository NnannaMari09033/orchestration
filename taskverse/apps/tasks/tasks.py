from celery import shared_task

def send_task_notification(task_id, user_id):
    # In a real app, you might send an email or push notification here
    print(f"[CELERY TASK] Notification: Task {task_id} assigned to user {user_id}")
    return f"Notification sent for task {task_id} to user {user_id}"

send_task_notification = shared_task(send_task_notification)
