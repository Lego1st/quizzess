from rest_framework import serializers
from quizzes.models import Quiz, Question
from rest_framework_jwt.settings import api_settings
import json
from random import shuffle


## Quiz and Question serializers
class BriefQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        exclude = ('shuffle',)

class QuestionReadOnlySerializer(serializers.BaseSerializer):
    
    def to_representation(self, obj):
        output = {
            'index': obj.index,
            'type': obj.question_type,
            'content': obj.content,
            'options': json.loads(obj.options)
        }
        if obj.question_type == 'ma':
            output['matchings'] = json.loads(obj.matchings)

        return output

class QuizQuestionReadOnlySerializer(serializers.ModelSerializer):
    questions = QuestionReadOnlySerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id' ,'title', 'brief', 'category', 'shuffle', 'questions')

class FullQuestionSerializer(serializers.BaseSerializer):

    def to_internal_value(self, data):
        QUESTION_TYPE = {
            'si': {'max_option': 7, 'min_option': 2, 'full_name': 'Single choice'},
            'mu': {'max_option': 20, 'min_option': 3, 'full_name': 'Multiple choice'},
            'ma': {'max_option': 20, 'min_option': 2, 'full_name': 'Matching'},
            'fi': {'max_option': 0, 'min_option': 0, 'full_name': 'Filling in the blank'}
        }
        def _validate(logic, message):
            if not logic:
                raise serializers.ValidationError(message)
        
        index = str(data.get('index'))
        question_type = data.get('type')
        content = data.get('content')
        options = data.get('options')
        matchings = data.get('matchings')
        answer = data.get('answer')

        # validate fields
        _validate(index, {'index': 'This field is required.'})
        _validate(question_type, {'type|question index: {}'.format(index): 'This field is required.'})
        _validate(content, {'content|question index: {}'.format(index): 'This field is required.'})
        _validate(answer, {'answer|question index: {}'.format(index): 'This field is required.'})
        _validate(type(answer) == list, {'answer|question index: {}'.format(index): 'This field must be a list.'})
        _validate(options, {'options|question index: {}'.format(index): 'This field is required.'})
        _validate(type(options) == list, {'options|question index: {}'.format(index): 'This field must be a list.'})
        if question_type == 'ma':
            _validate(matchings, {'matchings|question index: {}'.format(index): 'This field is required in matching question.'})
            _validate(type(matchings), {'matchings|question index: {}'.format(index): 'This field must be a list'})

        # validate fields length
        min_option_len = QUESTION_TYPE[question_type]['min_option']
        max_option_len = QUESTION_TYPE[question_type]['max_option']
        question_name = QUESTION_TYPE[question_type]['full_name']
        _validate(
            len(options) >= min_option_len, 
            {'options|question index: {}'.format(index): '{} question needs at least {} options'.format(question_name, min_option_len)}
        )
        _validate(
            len(options) <= max_option_len,
            {'options|question index: {}'.format(index): '{} question limits to {} options'.format(question_name, max_option_len)}
        )

        if question_type == 'ma':
            _validate(
                len(options) == len(matchings) == len(answer), 
                {'options, matchings, answer|question index: {}'.format(index): 'These fields must have the same length in matching question'}
            )
            for a in answer:
                _validate(a in options, {'answer|question index: {}'.format(index): 'answer does not match options'})
        
        if question_type == 'si':
            _validate(len(answer) == 1, {'answer|question index: {}'.format(index): 'This field must have one item in single choice question'})
            _validate(answer[0] in options, {'answer|question index: {}'.format(index): 'answer does not match options'})
        
        if question_type == 'mu':
            _validate(len(answer) <= len(options), {'answer, options|question index: {}'.format(index): "answer's length must be equal or smaller than options' multiple choice question"}) 
            for a in answer:
                _validate(a in options, {'answer|question index: {}'.format(index): 'answer does not match options'})

        output = {
            'index': int(index),
            'question_type': question_type,
            'content': content,
            'options': json.dumps(options),
            'answer': json.dumps(answer)
        }
        if question_type == 'ma':
            output['matchings'] = json.dumps(matchings)
            output['options'] = json.dumps(random.shuffle(options))

        return output

    def to_representation(self, obj):
        output = {
            'index': obj.index,
            'type': obj.question_type,
            'content': obj.content,
            'options': json.loads(obj.options),
            'answer': json.loads(obj.answer)
        }
        if obj.question_type == 'ma':
            output['matchings'] = json.loads(obj.matchings)

        return output

class FullQuizSerializer(serializers.ModelSerializer):
    questions = FullQuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ('id' ,'title', 'brief', 'category', 'shuffle', 'questions')

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(quiz=quiz, **question_data)
        return quiz

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.brief = validated_data.get('brief', instance.brief)
        instance.category = validated_data.get('category', instance.category)
        instance.shuffle = validated_data.get('shuffle', instance.shuffle)
        instance.save()
        
        quiz_id = instance.id
        quiz = Quiz.objects.get(pk=quiz_id)
        Question.objects.filter(quiz=quiz).delete()
        questions_data = validated_data.pop('questions')
        for question_data in questions_data:
            Question.objects.create(quiz=quiz, **question_data)
        return instance
        
