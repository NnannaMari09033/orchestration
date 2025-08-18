import graphene
from taskverse.apps.users.schema import Query as UsersQuery
from taskverse.apps.tasks.schema import Query as TasksQuery, Mutation as TasksMutation
from taskverse.apps.monitoring.schema import Query as MonitoringQuery


class Query(UsersQuery, TasksQuery, MonitoringQuery, graphene.ObjectType):
    pass


class Mutation(TasksMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
