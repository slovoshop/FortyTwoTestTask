from .models import RequestContent


class RequestContentMiddleware(object):
    def process_request(self, request):
        """ Alex code """
        if request.path == '/get_new/':
            initLMID = request.POST['username'] + '_ILMID'
            request.in_initLMID = request.session.get(initLMID)
        """ Alex code """

        """ Alex code """
        chat_views = ['/userchat/', '/send/', '/get_new/', '/scan_threads/']
        if request.path == '/get_new/':
            import datetime
            nowtime = datetime.datetime.now().strftime('%H:%M:%S')

            if 'admin_ILMID' in request.session:
                print('\n' + nowtime +\
                      ' RequestContentMiddleware > process_request > ' +\
                      request.path +\
                      ' > session[admin_ILMID] = ' +\
                      str(request.session.get('admin_ILMID')))
        """ Alex code """

    def process_response(self, request, response):
        '''  Log request info in DB '''
        if request.path == "/request/" and request.is_ajax():
            return response

        request_log = RequestContent(
          method=request.method,
          path=request.build_absolute_uri(),
          status_code=response.status_code,
        )
        request_log.save()

        """ Save bigger values in LMID dict if it was reseted to lower value """
        chat_views = ['/userchat/', '/send/', '/get_new/', '/scan_threads/']
        if request.path == '/get_new/':
            initLMID = request.POST['username'] + '_ILMID'
            out_initLMID = request.session.get(initLMID)
            print('request.in_initLMID = ' + str(request.in_initLMID))
            print('out_initLMID = ' + str(out_initLMID))
            for key in out_initLMID:
               if key in request.in_initLMID and\
               out_initLMID[key] < request.in_initLMID[key]:
                   out_initLMID[key] = request.in_initLMID[key]
                   print('Out_value < in_value')
            request.session[initLMID] = out_initLMID
            request.session.modified = True
            request.session.save()

        return response
