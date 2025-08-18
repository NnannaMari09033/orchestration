import graphene
from graphene_django import DjangoObjectType
from .models import Task

class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"

class Query(graphene.ObjectType):
    all_tasks = graphene.List(TaskType)
    task_by_id = graphene.Field(TaskType, id=graphene.Int(required=True))

    def resolve_all_tasks(root, info):
        return Task.objects.all()

    def resolve_task_by_id(root, info, id):
        return Task.objects.get(pk=id)

class CreateTask(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    task = graphene.Field(TaskType)

    def mutate(root, info, name):
        user = info.context.user
        task = Task.objects.create(user=user, name=name)
        return CreateTask(task=task)

class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
