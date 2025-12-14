import graphene

class Query(graphene.ObjectType):
    # We can move the 'hello' field here, or just leave a placeholder
    # For now, let's keep it simple so the code is valid.
    crm_hello = graphene.String(default_value="Hello from CRM App!")