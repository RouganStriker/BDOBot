import boto3

TABLE_NAME = 'bdo-bot'


class BasePlugin(object):
    # Plugin type is used to uniquely identify the plugin's item in dynamodb
    PLUGIN_TYPE = None
    # Mapping of attribute names to a type
    ATTRIBUTE_MAPPING = {}

    def __init__(self, discord_client=None):
        self.db = boto3.client('dynamodb')
        self.discord = discord_client

    @property
    def partition_key(self):
        return {
            'plugin-type': {
                'S': self.PLUGIN_TYPE
            }
        }

    def get_item(self):
        """Returns this plugin's data stored in dynamodb."""
        if self.PLUGIN_TYPE is None:
            raise NotImplemented("PLUGIN_TYPE is not defined, cannot access DB.")

        return self.db.get_item(
            TableName=TABLE_NAME,
            Key=self.partition_key
        )

    def _python_type_to_dynamo_type(self, attribute_class):
        if issubclass(attribute_class, str):
            return 'S'
        elif attribute_class in [int, long, float, complex]:
            return 'N'
        elif issubclass(attribute_class, list):
            return 'L'
        elif issubclass(attribute_class, bool):
            return 'BOOL'
        else:
            raise Error("Unexpected attribute class {0}".format(attribute_class))

    def create_item(self, **kwargs):
        """Create an item in dynamodb with attributes in initial kwargs."""

        item = self.partition_key

        for attribute, value in kwargs.items():
            if attribute not in self.ATTRIBUTE_MAPPING:
                continue

            attribute_type = self._python_type_to_dynamo_type(self.ATTRIBUTE_MAPPING[attribute])
            item[attribute] = {
                attribute_type: value
            }

        return self.db.put_item(
            TableName=TABLE_NAME,
            Item=item
        )

    def update_item(self, **kwargs):
        """Create an item in dynamodb with attributes in kwargs."""

        placeholders = {}
        update_attributes = []

        for attribute, value in kwargs.items():
            if attribute not in self.ATTRIBUTE_MAPPING:
                continue

            attribute_type = self._python_type_to_dynamo_type(self.ATTRIBUTE_MAPPING[attribute])

            attr_placeholder = ":value{}".format(len(placeholders))
            placeholders[attr_placeholder] = {attribute_type: value}
            update_attributes.add("{} = {}".format(attribute, attr_placeholder))

        if not update_attributes:
            return None

        return self.db.update_item(
            TableName=TABLE_NAME,
            Key=self.partition_key,
            UpdateExpression="SET {}".format(", ".join(update_attributes)),
            ExpressionAttributeValues=placeholders
        )

    def run(self):
        """Entry point for the plugin."""
        raise NotImplemented()