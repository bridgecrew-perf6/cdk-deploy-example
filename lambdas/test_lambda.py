import pytest
import lambda_handler


class TestLambdaHandler:
    @pytest.fixture
    def event(self):
        return {
            "Records": [
                {"body": "Hello"}
            ]
        }

    @pytest.fixture
    def context(self):
        return None

    def test_lambda_handler(self, event, context):
        result = lambda_handler.handler(event, context)
        assert result == {
            'statusCode': 200,
            'body': "Received Message Body : Hello"
        }
