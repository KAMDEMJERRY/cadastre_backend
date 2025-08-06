from rest_framework import serializers

class PDFGenerateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['simple', 'template', 'table'], required=True)
    data = serializers.DictField(child=serializers.JSONField(), required=True)

    def validate_data(self, value):
        if self.initial_data['type'] == 'simple':
            if 'content' not in value:
                raise serializers.ValidationError("Content is required for simple PDF generation.")
        elif self.initial_data['type'] == 'template':
            if 'template_name' not in value or 'context' not in value:
                raise serializers.ValidationError("Template name and context are required for template PDF generation.")
        elif self.initial_data['type'] == 'table':
            if 'data' not in value:
                raise serializers.ValidationError("Data is required for table PDF generation.")
        return value