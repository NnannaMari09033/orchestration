import graphene
from taskverse.apps.users.schema import Query as UsersQuery
from taskverse.apps.tasks.schema import Query as TasksQuery, Mutation as TasksMutation
from taskverse.apps.monitoring.schema import Query as MonitoringQuery

class Query(UsersQuery, TasksQuery, MonitoringQuery, graphene.ObjectType):
    # Main query class combining all app queries
    pass

class Mutation(TasksMutation, graphene.ObjectType):
    # Main mutation class combining all app mutations
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
