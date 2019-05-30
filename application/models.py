import datetime
import subprocess

from peewee import CharField, ForeignKeyField, Model, SqliteDatabase, TextField
from playhouse.sqlite_ext import JSONField, DateTimeField

import config
from application import runner

sqlite_db = SqliteDatabase(str(config.DB_PATH))


class BaseModel(Model):
    class Meta:
        database = sqlite_db


class User(BaseModel):
    token: str = CharField(max_length=128, primary_key=True)
    username: str = CharField(max_length=128, null=True)


class Task(BaseModel):
    name: str = CharField()
    description: str = TextField()
    examples: list = JSONField()
    tests: list = JSONField()


class Solution(BaseModel):
    user: User = ForeignKeyField(User, to_field='token')
    task: Task = ForeignKeyField(Task)
    solution_file: CharField(null=True)
    submitted: datetime.datetime = DateTimeField(default=lambda: datetime.datetime.now())
    status: str = CharField(choices=('QUEUED', 'RUNNING', 'ACCEPTED', 'FAILED'), default='QUEUED', null=True)
    error: str = CharField(null=True)

    @classmethod
    def store(cls, user: User, task: Task, source: str):
        try:
            solution_id = cls.select().order_by(Solution.id.desc()).get().id + 1
        except cls.DoesNotExist:
            solution_id = 0
        filename = str(config.SOLUTIONS_FOLDER / f'{user.username}-{task.id}-{solution_id}.py')
        solution = cls.create(id=solution_id, user=user, task=task, solution_file=filename)

        with open(filename, 'w') as f:
            f.write(source)
        return solution

    def run_tests(self):
        self.status = 'RUNNING'
        self.save()
        for i, test_suite in enumerate((*self.task.examples, *self.task.tests)):
            error = None
            try:
                result, error = runner.run_test(self.solution_file, test_suite['input'], test_suite['output'])
                if not result:
                    raise AssertionError
            except (subprocess.SubprocessError, AssertionError, OSError) as e:
                if error is None:
                    error = e.__class__.__name__
                self.status = 'FAILED'
                self.error = f'{error} at {i+1} test'
                self.save()
                return False
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f'error {e}', exc_info=1)
        else:
            self.status = 'ACCEPTED'
            self.save()
            return True


sqlite_db.create_tables(models=[User, Task, Solution], safe=True)
