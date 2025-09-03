import graphene
from graphene_django import DjangoObjectType
from .models import MonitoringRecord


class MonitoringRecordType(DjangoObjectType):
    class Meta:
        model = MonitoringRecord
        fields = "__all__"


class Query(graphene.ObjectType):
    all_monitoring_records = graphene.List(MonitoringRecordType)
    monitoring_record_by_id = graphene.Field(MonitoringRecordType, id=graphene.Int(required=True))

    def resolve_all_monitoring_records(root, info):
        return MonitoringRecord.objects.all()

    def resolve_monitoring_record_by_id(root, info, id):
        return MonitoringRecord.objects.get(pk=id)


class CreateMonitoringRecord(graphene.Mutation):
    class Arguments:
        service_name = graphene.String(required=True)
        status = graphene.String(required=True)
        details = graphene.String(required=False)

    record = graphene.Field(MonitoringRecordType)

    def mutate(root, info, service_name, status, details=None):
        record = MonitoringRecord.objects.create(
            service_name=service_name,
            status=status,
            details=details,
        )
        return CreateMonitoringRecord(record=record)


class Mutation(graphene.ObjectType):
    create_monitoring_record = CreateMonitoringRecord.Field()
