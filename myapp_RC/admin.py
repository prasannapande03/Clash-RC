from django.contrib import admin

from .models import *

admin.site.register(Profile)
admin.site.register(User_Response)
admin.site.register(chatGPTLifeLine)

from import_export.admin import ImportExportModelAdmin
@admin.register(Question)
class QuestionResource(ImportExportModelAdmin):
    class Meta:
        model = Question
        fields = ('question_no','question','answer','is_junior')

@admin.register(EasyQuestion)
class EasyQuestionResource(ImportExportModelAdmin):
    class Meta:
        model = EasyQuestion
        fields = ('easyquestion_no','easyquestion','easyanswer')
