from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.views.generic.base import View
from .RedirectConf import RedirectConf
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from .GraphAPIManager import GraphAPIManager
from django.shortcuts import render
import os.path


class RedirectPage(View):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @xframe_options_exempt
    def dispatch(self, request, *args, **kwargs):
        url = RedirectConf.get_redirect_url()
        self.logger.info("redirect url: {}".format(url))
        # return redirect(url)
        context = dict()
        context['login_ms_url'] = url
        # res = HttpResponse("login page", content_type="text/html", status=200)
        # res['Content-Length'] = 10
        # res["Access-Control-Allow-Origin"] = "*"
        # res["X-Frame-Options"] = "ALLOW-FROM"
        # return res
        response = render(request, 'index.html', context)
        # response["X-Frame-Options"] = "ALLOW-FROM https://onedrive.live.com/"
        # response["Access-Control-Allow-Origin"] = "*"
        # response["Content-Security-Policy"] = "frame-ancestors live.com"
        # return HttpResponse("Main")
        return response


"""
Get code from auth reponse
"""
class GetCodePage(View):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.code = ""
        self.access_token = ""
        self.refresh_token = ""

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.code = code = request.GET['code']
        self.logger.info("auth code is {}".format(code))

        from .GetTokenConf import GetTokenConf
        url = GetTokenConf.get_token_url()
        body = GetTokenConf.get_token_body(code)

        # request = HttpRequest()
        # request.method = "POST"
        # request.content_type = "application/x-www-form-urlencoded"
        # request.POST(url)

        import http.client
        from .Office365Conf import ms_site_login_url
        site = ms_site_login_url.replace("https://", "")
        conn = http.client.HTTPSConnection(host=site)
        header = dict()
        header["Content-Type"] = "application/x-www-form-urlencoded"
        result = conn.request(method="POST", url=url, headers=header, body=body)
        response = HttpResponse(conn.getresponse())
        print("response content:")
        print(response.content)

        content = str(response.content, encoding='utf-8')
        content_dict = eval(content)
        self.access_token = content_dict['access_token']
        self.refresh_token = content_dict['refresh_token']

        GraphAPIManager.access_token = self.access_token
        GraphAPIManager.refresh_token = self.refresh_token
        GraphAPIManager.token_type = content_dict['token_type']

        file_content = "{} {}".format(self.access_token, GraphAPIManager.token_type)
        with open("token.bin", 'w') as f:
            f.write(file_content)
        return HttpResponse("OK...")


class ListPage(View):
    @xframe_options_exempt
    def dispatch(self, request, *args, **kwargs):
        api_manager = GraphAPIManager.getInstance()
        folder_list = api_manager.retrieve_root_directory()
        context = dict()

        # folder_list = list()
        # item = FolderItem()
        # item.display_name = "a"
        # folder_list.append(item)
        # item = FolderItem()
        # item.display_name = "bbbb"
        # item.is_folder = 'T'
        # folder_list.append(item)
        context['folder_list'] = folder_list
        response = render(request, 'Folder_Structure.html', context)
        # response["X-Frame-Options"] = "ALLOW-FROM"

        return response

class ReportElement(object):
    def __init__(self, rid, rname):
        self.rid = rid
        self.rname = rname


class RunPage(View):
    logon = False
    logon_manager = None

    def __init__(self):
        # if not RunPage.logon:
            from .LoginB1AHManager import LoginB1AHManager
            RunPage.logon_manager = LoginB1AHManager()
            RunPage.logon_manager.login()
            RunPage.logon = True

    @staticmethod
    def get_report_dir():
        from .settings import BASE_DIR
        return BASE_DIR + '/Reports/'

    @xframe_options_exempt
    def dispatch(self, request, *args, **kwargs):
        full_path = request.get_full_path()
        if full_path.find('?') < 0:
            from .DB import DBManager
            db = DBManager.get_instance()
            context = db.retrieve_report_list()
            report_list = list()
            for k in context:
                element = ReportElement(k, context.get(k))
                report_list.append(element)

            context_ = dict()
            context_['report_list'] = report_list
            response = render(request, 'Report_List.html', context_)
            # response["X-Frame-Options"] = "ALLOW-FROM"
            return response

        params = full_path.split('?')[1]
        report_id = params.split('=')[1]

        report_name = RunPage.logon_manager.run_excel_report(report_id, 1)
        import shutil
        report_dir = RunPage.get_report_dir()
        shutil.move(report_name, report_dir)

        new_report_name = report_dir + report_name
        if os.path.exists(new_report_name):
            content = GraphAPIManager.getInstance().upload_excel_report(new_report_name)
            if content is None:
                return HttpResponse('Failure!!')
            else:
                upload_info = GraphAPIManager.extract_uploaded_file_info(content)
                info = dict()
                info['report_name'] = upload_info.name
                info['web_url'] = upload_info.web_url
                response = render(request, 'Open_Excel_Report.html', context=info)
                # response["X-Frame-Options"] = "ALLOW-FROM"
                return response

        else:
            return HttpResponse('No')

class Test(View):
    def dispatch(self, request, *args, **kwargs):
        context  = dict()
        context['hello'] = "Hello Young"
        return render(request, 'Folder_Structure.html', context)


class SendJson(View):
    def dispatch(self, request, *args, **kwargs):
        response = render(request, 'customfunctions.json', {})
        response['Access-Control-Allow-Origin'] = '*'
        response['Content-Type'] = 'application/octet-stream'

        return response

class DimensionMeasureView(View):
    @xframe_options_exempt
    def dispatch(self, request, *args, **kwargs):
        from .DB import DBManager
        db = DBManager.get_instance()
        measures = db.retrieve_view_measures()
        dimensions = db.retrieve_view_dimensions()

        context = dict()
        context['measures'] = measures
        context['dimensions'] = dimensions
        response = render(request, 'View_Fields.html', context)
        response["Access-Control-Allow-Methods"] = "GET, PUT, POST, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "1000"

        return response


class SaveReportView(View):
    # @xframe_options_exempt
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        body = str(request.body, encoding='utf-8')
        import json
        fields = json.loads(body)

        context = dict()
        context['dimension0'] = fields['dimension']
        context['measure0'] = fields['measure']
        response = render(request, 'report_template.xml', context)
        newxml = str(response.content, encoding='utf-8')

        GraphAPIManager.getInstance().retrieve_report_template()
        from .DB import DBManager
        DBManager.get_instance().update_report_definition(newxml)
        print("Report Definition:")
        print(newxml)
        return HttpResponse("Saved Successfully")


class DownloadReportView(View):
    def dispatch(self, request, *args, **kwargs):

        return HttpResponse("Download")


class PopupHtmlView(View):
    def dispatch(self, request, *args, **kwargs):
        response = render(request, 'InsertGroup.html', None)
        response["allow-same-origin"] = '*'
        return response
