from models import RequestContent


RequestContent.objects.all().delete()
print('RequestContent is clear')
