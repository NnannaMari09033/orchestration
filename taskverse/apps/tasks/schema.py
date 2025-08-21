import graphene
from graphene_django import DjangoObjectType  
from .models import Task, Project
from django.contrib.auth import get_user_model
from .tasks import send_task_notification

# ← Add TaskType definition
class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        fields = "__all__"


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = "__all__"


class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        member_ids = graphene.List(graphene.Int, required=False)

    project = graphene.Field(ProjectType)

    def mutate(root, info, name, description=None, member_ids=None):
        User = get_user_model()
        project = Project.objects.create(name=name, description=description)
        if member_ids:
            members = User.objects.filter(id__in=member_ids)
            project.members.set(members)
        return CreateProject(project=project)

class CreateTask(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True)
        project_id = graphene.Int(required=False)

    task = graphene.Field(TaskType)

    def mutate(root, info, name, project_id=None):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        
        # Handle optional project
        project = None
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                # Check if user is a member of the project
                if not project.members.filter(id=user.id).exists():
                    raise Exception("User is not a member of this project")
            except Project.DoesNotExist:
                raise Exception(f"Project with id {project_id} does not exist")
        
        task = Task.objects.create(
            user=user, 
            name=name, 
            project=project
        )
        
        send_task_notification.delay(task.id, user.id)
        return CreateTask(task=task)


# Graphene Query and Mutation classes for tasks app
class Query(graphene.ObjectType):
    all_tasks = graphene.List(TaskType)
    all_projects = graphene.List(ProjectType)

    def resolve_all_tasks(root, info):
        return Task.objects.all()

    def resolve_all_projects(root, info):
        return Project.objects.all()


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    create_project = CreateProject.Field()