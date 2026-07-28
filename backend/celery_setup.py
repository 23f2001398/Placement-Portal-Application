from celery import Celery


def make_celery(app=None):
    celery_app = Celery('tasks')

    class FlaskTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            if app is not None:
                with app.app_context():
                    return self.run(*args, **kwargs)
            return self.run(*args, **kwargs)

    celery_app.Task = FlaskTask
    return celery_app

celery = make_celery()